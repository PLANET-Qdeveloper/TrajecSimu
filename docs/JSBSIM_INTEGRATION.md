# JSBSim Integration in TrajecSimu

This document describes how JSBSim (a C++ flight dynamics simulation library) is integrated into the Rust-based TrajecSimu project.

## Architecture Overview

The integration uses a **C API wrapper** approach rather than automatic binding generation (bindgen). This provides better stability, control, and simplicity when interfacing with complex C++ libraries.

### Component Structure

```
┌─────────────────┐
│   Rust Code     │  (High-level API)
│ JSBSimExecutive │
└────────┬────────┘
         │
         ↓ (calls)
┌─────────────────┐
│   Rust FFI      │  (Foreign Function Interface)
│  src/jsbsim/    │  ffi.rs - extern "C" declarations
│     ffi.rs      │
└────────┬────────┘
         │
         ↓ (links to)
┌─────────────────┐
│  C API Wrapper  │  (C interface)
│  jsbsim_wrapper │  src/jsbsim_wrapper.cpp
│      .cpp       │
└────────┬────────┘
         │
         ↓ (calls)
┌─────────────────┐
│   JSBSim C++    │  (Original library)
│   FGFDMExec     │  Compiled from jsbsim/
└─────────────────┘
```

## Why C API Wrapper Instead of bindgen?

### bindgen Limitations
- **Complex C++ types**: bindgen struggles with `std::shared_ptr`, templates, custom types like `SGPath`
- **Large header dependencies**: JSBSim has extensive header hierarchies that are difficult to parse automatically
- **Fragile bindings**: Changes in JSBSim headers can break automatically generated bindings
- **Compilation issues**: libclang parsing errors with complex C++ codebases

### C API Wrapper Advantages
- ✅ **Full control**: Manually define which functions to expose
- ✅ **Simple types**: Use C-compatible types (`void*`, `const char*`, `double`, `bool`)
- ✅ **Stability**: Decouples from internal JSBSim C++ implementation details
- ✅ **Easier debugging**: Clear boundaries between Rust and C++ code
- ✅ **Smaller API surface**: Only expose what's actually needed

## Build Process

The integration uses a multi-stage build process defined in `build.rs`:

### Stage 1: Build JSBSim with CMake
```rust
let dst = Config::new("jsbsim")
    .define("BUILD_SHARED_LIBS", "OFF")  // Static library
    .define("BUILD_PYTHON_MODULE", "OFF")
    .define("CMAKE_CXX_STANDARD", "17")
    .build();
```

This:
- Compiles JSBSim as a static library (`libJSBSim.a`)
- Installs headers to a known location
- Disables unnecessary components (Python, docs, etc.)

### Stage 2: Compile C++ Wrapper with cc crate
```rust
cc::Build::new()
    .cpp(true)
    .file("src/jsbsim_wrapper.cpp")
    .include(format!("{}/include/JSBSim", dst.display()))
    .flag("-std=c++17")
    .compile("jsbsim_wrapper");
```

This:
- Compiles `jsbsim_wrapper.cpp` into a static library
- Links against JSBSim headers
- Uses C++17 standard

### Stage 3: Link Everything
```rust
println!("cargo:rustc-link-lib=static=JSBSim");
println!("cargo:rustc-link-lib=dylib=c++");  // macOS C++ runtime
```

## API Layers

### 1. C++ Wrapper (`src/jsbsim_wrapper.cpp`)

Provides C-compatible functions that wrap JSBSim C++ API:

```cpp
extern "C" {
    void* jsbsim_create() {
        return new JSBSim::FGFDMExec();
    }

    void jsbsim_destroy(void* ptr) {
        delete static_cast<JSBSim::FGFDMExec*>(ptr);
    }

    bool jsbsim_load_script(void* ptr, const char* script_path, double delta_t) {
        auto fdm = static_cast<JSBSim::FGFDMExec*>(ptr);
        return fdm->LoadScript(SGPath(script_path), delta_t);
    }

    // ... more functions
}
```

### 2. Rust FFI Layer (`src/jsbsim/ffi.rs`)

Declares external C functions for Rust to call:

```rust
extern "C" {
    pub fn jsbsim_create() -> *mut c_void;
    pub fn jsbsim_destroy(ptr: *mut c_void);
    pub fn jsbsim_load_script(ptr: *mut c_void, script_path: *const c_char, delta_t: f64) -> bool;
    // ... more declarations
}
```

### 3. Safe Rust API (`src/jsbsim/wrapper.rs`)

Provides safe, idiomatic Rust interface:

```rust
pub struct JSBSimExecutive {
    ptr: *mut c_void,
}

impl JSBSimExecutive {
    pub fn new() -> Result<Self> {
        let ptr = unsafe { ffi::jsbsim_create() };
        if ptr.is_null() {
            anyhow::bail!("Failed to create JSBSim FDMExec");
        }
        Ok(Self { ptr })
    }

    pub fn load_script<P: AsRef<Path>>(&mut self, script_path: P, delta_t: f64) -> Result<()> {
        let path_str = script_path.as_ref().to_str()
            .context("Invalid script path")?;
        let c_path = CString::new(path_str)
            .context("Invalid script path")?;

        let result = unsafe {
            ffi::jsbsim_load_script(self.ptr, c_path.as_ptr(), delta_t)
        };

        if !result {
            anyhow::bail!("Failed to load script: {:?}", script_path.as_ref());
        }
        Ok(())
    }

    // ... more methods
}

impl Drop for JSBSimExecutive {
    fn drop(&mut self) {
        unsafe { ffi::jsbsim_destroy(self.ptr); }
    }
}
```

## Usage Example

See `examples/jsbsim_basic.rs` for a complete example:

```rust
use trajecsim_rs::jsbsim::JSBSimExecutive;

fn main() -> Result<()> {
    // Create JSBSim executive
    let mut exec = JSBSimExecutive::new()?;

    // Set time step
    exec.set_dt(0.01);

    // Set up paths
    exec.set_root_dir("/path/to/jsbsim")?;
    exec.set_aircraft_path("/path/to/aircraft")?;

    // Load model
    exec.load_model("my_rocket")?;

    // Initialize
    exec.run_ic()?;

    // Run simulation
    while exec.run()? {
        let time = exec.get_sim_time();
        let altitude = exec.get_property("position/h-sl-ft")?;
        println!("Time: {:.2}s, Altitude: {:.2}ft", time, altitude);
    }

    Ok(())
}
```

## Available API Functions

### Lifecycle
- `new()` - Create new executive
- `drop()` - Automatically cleanup (RAII)

### Model Loading
- `load_model(model_name)` - Load aircraft model
- `load_script(script_path, delta_t)` - Load script file

### Simulation Control
- `run()` - Run one simulation step
- `run_ic()` - Initialize from initial conditions
- `hold()` / `resume()` - Pause/resume simulation
- `is_holding()` - Check pause state

### Time Management
- `get_sim_time()` - Get current simulation time
- `set_dt(dt)` / `get_dt()` - Set/get time step

### Properties
- `get_property(name)` - Read property value
- `set_property(name, value)` - Write property value

### Path Configuration
- `set_root_dir(path)` - Set JSBSim root directory
- `set_aircraft_path(path)` - Set aircraft directory
- `set_engine_path(path)` - Set engine directory
- `set_systems_path(path)` - Set systems directory
- `set_output_path(path)` - Set output directory

### Output Control
- `enable_output()` / `disable_output()` - Control output generation

## Testing

Run the test suite:

```bash
cargo test --lib jsbsim
```

Run the example:

```bash
cargo run --example jsbsim_basic
```

## Dependencies

### Rust Dependencies
- `anyhow` - Error handling
- `cmake` (build-dependency) - Build JSBSim
- `cc` (build-dependency) - Compile C++ wrapper

### System Dependencies
- CMake 3.10+
- C++17 compatible compiler
- C++ standard library (libc++ on macOS, libstdc++ on Linux)

## Troubleshooting

### Build Failures

**Issue**: CMake fails to find compiler
```
Solution: Install CMake and ensure cc/c++ are in PATH
```

**Issue**: Linking errors with C++ standard library
```
Solution: Verify correct C++ stdlib for your platform in build.rs
```

**Issue**: JSBSim compilation errors
```
Solution: Ensure jsbsim/ submodule is properly initialized
```

### Runtime Issues

**Issue**: "Failed to create JSBSim FDMExec"
```
Solution: Check that JSBSim library is properly linked
```

**Issue**: Property access returns unexpected values
```
Solution: Verify model is loaded and initialized with run_ic()
```

## Future Enhancements

Potential improvements to the integration:

1. **Property Manager**: Higher-level property access with type safety
2. **Initial Conditions Builder**: Rust builder pattern for IC setup
3. **Script Generation**: Generate JSBSim scripts from Rust config
4. **Parallel Execution**: Thread-safe wrapper for parallel simulations
5. **Async Support**: Async/await interface for long-running simulations

## References

- [JSBSim Documentation](https://jsbsim-team.github.io/jsbsim/)
- [JSBSim GitHub](https://github.com/JSBSim-Team/jsbsim)
- [Rust FFI Guide](https://doc.rust-lang.org/nomicon/ffi.html)
- [cc Crate Documentation](https://docs.rs/cc/)
