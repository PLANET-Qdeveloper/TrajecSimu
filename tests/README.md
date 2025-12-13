# Tests for TrajecSimu

This directory contains comprehensive tests for the TrajecSimu project, following Rust testing best practices (2025).

## Test Structure

### Input Module Tests (`input_tests.rs`)

Comprehensive tests for the `src/input/` module covering:

#### 1. Loader Tests (`loader_tests`)
- **Valid Configuration Loading**: Tests loading a valid YAML configuration file
- **Nonexistent File Handling**: Ensures proper error handling for missing files
- **Invalid YAML Syntax**: Tests error handling for malformed YAML
- **Malformed Structure**: Validates error handling when YAML doesn't match schema

#### 2. Schema Tests (`schema_tests`)
- **Complete Configuration Deserialization**: Tests deserializing a full configuration
- **Optional Construction Field**: Validates that optional `construction` field works when absent
- **Default Value Application**: Ensures default values (like `roll: 0.0`) are properly applied
- **Empty String to None Conversion**: Tests custom deserializer for empty string paths
- **Non-empty Path Handling**: Validates that non-empty paths are properly parsed
- **Multiple Parachutes**: Tests array deserialization with multiple parachute configurations
- **Complete Construction Fields**: Validates all optional construction parameters

#### 3. Validator Tests (`validator_tests`)
- **Valid Configuration**: Ensures no errors for valid configurations
- **Missing Required File**: Tests error reporting for missing thrust curve file
- **Missing Optional File**: Tests error reporting for missing optional table files
- **Multiple Missing Files**: Validates detection of multiple missing files
- **Error Severity Levels**: Ensures all file-not-found errors are marked as `Error` severity

## Test Fixtures

Located in `tests/fixture/`:

- `landed_area.yaml`: Valid configuration file (copied from `data/input/`)
- `invalid.yaml`: Syntactically invalid YAML for error handling tests
- `malformed.yaml`: Valid YAML but doesn't match our schema structure

## Common Test Utilities

`tests/common/mod.rs` provides:
- `fixture_path(filename)`: Helper to get absolute paths to test fixture files

## Running Tests

### Run all input module tests:
```bash
cargo test --test input_tests
```

### Run specific test module:
```bash
cargo test --test input_tests loader_tests
cargo test --test input_tests schema_tests
cargo test --test input_tests validator_tests
```

### Run a specific test:
```bash
cargo test --test input_tests test_load_valid_config
```

### Run with output:
```bash
cargo test --test input_tests -- --nocapture
```

## Best Practices Applied (2025)

1. **Module Organization**: Tests are organized in submodules matching the source code structure
2. **Descriptive Names**: Test function names clearly describe what is being tested
3. **Comprehensive Coverage**: Tests cover happy paths, edge cases, and error conditions
4. **Fixture-based Testing**: Real fixture files for realistic testing scenarios
5. **Isolated Tests**: Each test is independent and can run in parallel
6. **Clear Assertions**: Each assertion includes descriptive failure messages
7. **Type Safety**: Full type annotations for clarity and correctness

## Test Coverage

The input module tests provide coverage for:
- ✅ File I/O and error handling
- ✅ YAML deserialization
- ✅ Schema validation
- ✅ Default value handling
- ✅ Optional field handling
- ✅ Custom deserializers (empty string to None)
- ✅ Path validation
- ✅ Error reporting and severity classification

## Notes

- Tests require the `tests/fixture/landed_area.yaml` file to exist
- Tests also reference files in `data/input/tables/` for validation tests
- All 16 tests pass successfully as of the latest implementation
