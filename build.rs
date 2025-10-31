use cmake::Config;

fn main() {
    let dst = Config::new("jsbsim")
        .define("BUILD_DOCS", "OFF")
        .define("BUILD_PYTHON_MODULE", "OFF")
        .define("BUILD_SHARED_LIBS", "OFF")
        .define("BUILD_JULIA_PACKAGE", "OFF")
        .define("BUILD_MATLAB_SFUNCTION", "OFF")
        .define("CMAKE_CXX_STANDARD", "17")
        .define("SYSTEM_EXPAT", "OFF")
        .define("CMAKE_CXX_STANDARD_REQUIRED", "ON")
        .build();

    println!("cargo:rustc-link-search=native={}/lib", dst.display());
    println!("cargo:rustc-link-lib=static=JSBSim");

    // C++ラッパーのビルド
    cc::Build::new()
        .cpp(true)
        .file("src/jsbsim_wrapper.cpp")
        .include(format!("{}/include/JSBSim", dst.display()))
        .flag("-std=c++17")
        .compile("jsbsim_wrapper");

    // Link against C++ standard library
    #[cfg(target_os = "macos")]
    println!("cargo:rustc-link-lib=dylib=c++");

    #[cfg(target_os = "linux")]
    println!("cargo:rustc-link-lib=dylib=stdc++");

    #[cfg(target_os = "windows")]
    println!("cargo:rustc-link-lib=dylib=stdc++");

}