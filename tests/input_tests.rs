mod common;

mod loader_tests {
    use super::common::fixture_path;
    use trajecsim_rs::input::loader::load_config;

    #[test]
    fn test_load_valid_config() {
        let path = fixture_path("landed_area.yaml");
        let result = load_config(&path);
        assert!(result.is_ok(), "Failed to load valid config: {:?}", result.err());

        let config = result.unwrap();
        assert_eq!(config.flight_simulator.launcher.launcher_length, 5.0);
        assert_eq!(config.flight_simulator.launcher.coordinates.latitude, 40.242865);
        assert_eq!(config.flight_simulator.launcher.coordinates.longitude, 140.01045);
    }

    #[test]
    fn test_load_nonexistent_file() {
        let path = fixture_path("nonexistent.yaml");
        let result = load_config(&path);
        assert!(result.is_err(), "Should fail when loading nonexistent file");
    }

    #[test]
    fn test_load_invalid_yaml() {
        let path = fixture_path("invalid.yaml");
        let result = load_config(&path);
        assert!(result.is_err(), "Should fail when loading invalid YAML");
    }

    #[test]
    fn test_load_malformed_structure() {
        let path = fixture_path("malformed.yaml");
        let result = load_config(&path);
        assert!(result.is_err(), "Should fail when YAML structure doesn't match schema");
    }
}

mod schema_tests {
    use super::common::fixture_path;
    use trajecsim_rs::input::schema::*;
    use std::fs::File;

    #[test]
    fn test_deserialize_complete_config() {
        let path = fixture_path("landed_area.yaml");
        let file = File::open(&path).expect("Failed to open fixture file");
        let config: InputParameter = serde_yaml::from_reader(file)
            .expect("Failed to deserialize config");

        // Verify flight_simulator
        assert!(config.flight_simulator.launcher.launcher_length > 0.0);
        assert!(config.flight_simulator.rocket.diameter > 0.0);
        assert!(config.flight_simulator.rocket.height > 0.0);

        // Verify construction is present
        assert!(config.construction.is_some());
    }

    #[test]
    fn test_optional_construction_absent() {
        let yaml = r#"
flight_simulator:
  launcher:
    rotation:
      magnetic_declination: -9.34
      azimuth: 292.34
      pitch: 76.0
    coordinates:
      latitude: 40.242865
      longitude: 140.01045
      elevation: 5.3
    launcher_length: 5.0
  wind:
    use_power_law: true
    winds_table: ""
    power_law:
      wind_ref_altitude: 2.0
      ground_wind_dir: 0.0
      ground_wind_speed: 1.0
      wind_power_factor: 0.16666
  rocket:
    diameter: 0.145
    height: 1.889
    inertia:
      xx: 0.05
      yy: 4.12
      zz: 4.12
    mass:
      dry_weight: 16.99
      cg:
        x: 1.144
      cp:
        x: 1.374
        x_mach_table: ""
        y_mach_table: ""
        z_mach_table: ""
      oxidizer_mass: 3.53
      tank_position:
        x: 0.869
      fuel_mass_before_burn: 0.643
      fuel_mass_after_burn: 0.1
      fuel_position:
        x: 0.944
    parachute:
      - full_deploy_time: 0.01
        deploy_delay: 3.0
        drag_coefficient: 1.2
        area: 0.572
    aerodynamics:
      coefficients:
        lift_coefficient_alpha: 8.387848333
        lift_coefficient_table: ""
        side_coefficient_beta: 8.387848333
        side_coefficient_table: ""
        drag_coefficient: 0.466
        drag_coefficient_table: ""
        roll_damping_coefficient: -0.073
        roll_damping_table: ""
        pitch_damping_coefficient: -2.394
        pitch_damping_table: ""
        yaw_damping_coefficient: -2.394
        yaw_damping_table: ""
    thrust:
      thrust_curve: "data/input/tables/thrust.csv"
      cut_off_time: 1000.0
    solver:
      flight_duration: 4000.0
      time_step: 0.001
      notify_interval: 5.0
      output_rate: 10
      apogee_mode: 0
"#;
        let config: InputParameter = serde_yaml::from_str(yaml)
            .expect("Failed to deserialize minimal config");
        assert!(config.construction.is_none());
    }

    #[test]
    fn test_default_values_applied() {
        let yaml = r#"
flight_simulator:
  launcher:
    rotation:
      magnetic_declination: -9.34
      azimuth: 292.34
      pitch: 76.0
    coordinates:
      latitude: 40.242865
      longitude: 140.01045
      elevation: 5.3
    launcher_length: 5.0
  wind:
    use_power_law: true
    winds_table: ""
    power_law:
      wind_ref_altitude: 2.0
      ground_wind_dir: 0.0
      ground_wind_speed: 1.0
      wind_power_factor: 0.16666
  rocket:
    diameter: 0.145
    height: 1.889
    inertia:
      xx: 0.05
      yy: 4.12
      zz: 4.12
    mass:
      dry_weight: 16.99
      cg:
        x: 1.144
      cp:
        x: 1.374
        x_mach_table: ""
        y_mach_table: ""
        z_mach_table: ""
      oxidizer_mass: 3.53
      tank_position:
        x: 0.869
      fuel_mass_before_burn: 0.643
      fuel_mass_after_burn: 0.1
      fuel_position:
        x: 0.944
    parachute:
      - full_deploy_time: 0.01
        deploy_delay: 3.0
        drag_coefficient: 1.2
        area: 0.572
    aerodynamics:
      coefficients:
        lift_coefficient_alpha: 8.387848333
        lift_coefficient_table: ""
        side_coefficient_beta: 8.387848333
        side_coefficient_table: ""
        drag_coefficient: 0.466
        drag_coefficient_table: ""
        roll_damping_coefficient: -0.073
        roll_damping_table: ""
        pitch_damping_coefficient: -2.394
        pitch_damping_table: ""
        yaw_damping_coefficient: -2.394
        yaw_damping_table: ""
    thrust:
      thrust_curve: "data/input/tables/thrust.csv"
      cut_off_time: 1000.0
    solver:
      flight_duration: 4000.0
      time_step: 0.001
      notify_interval: 5.0
      output_rate: 10
      apogee_mode: 0
"#;
        let config: InputParameter = serde_yaml::from_str(yaml)
            .expect("Failed to deserialize config");

        // Check defaults are applied
        assert_eq!(config.flight_simulator.launcher.rotation.roll, 0.0);
        assert_eq!(config.flight_simulator.rocket.inertia.xy, 0.0);
        assert_eq!(config.flight_simulator.rocket.inertia.xz, 0.0);
        assert_eq!(config.flight_simulator.rocket.inertia.yz, 0.0);
        assert_eq!(config.flight_simulator.rocket.mass.cg.y, 0.0);
        assert_eq!(config.flight_simulator.rocket.mass.cg.z, 0.0);
    }

    #[test]
    fn test_empty_string_path_becomes_none() {
        let yaml = r#"
flight_simulator:
  launcher:
    rotation:
      magnetic_declination: -9.34
      azimuth: 292.34
      pitch: 76.0
    coordinates:
      latitude: 40.242865
      longitude: 140.01045
      elevation: 5.3
    launcher_length: 5.0
  wind:
    use_power_law: true
    winds_table: ""
    power_law:
      wind_ref_altitude: 2.0
      ground_wind_dir: 0.0
      ground_wind_speed: 1.0
      wind_power_factor: 0.16666
  rocket:
    diameter: 0.145
    height: 1.889
    inertia:
      xx: 0.05
      yy: 4.12
      zz: 4.12
    mass:
      dry_weight: 16.99
      cg:
        x: 1.144
      cp:
        x: 1.374
        x_mach_table: ""
        y_mach_table: ""
        z_mach_table: ""
      oxidizer_mass: 3.53
      tank_position:
        x: 0.869
      fuel_mass_before_burn: 0.643
      fuel_mass_after_burn: 0.1
      fuel_position:
        x: 0.944
    parachute:
      - full_deploy_time: 0.01
        deploy_delay: 3.0
        drag_coefficient: 1.2
        area: 0.572
    aerodynamics:
      coefficients:
        lift_coefficient_alpha: 8.387848333
        lift_coefficient_table: ""
        side_coefficient_beta: 8.387848333
        side_coefficient_table: ""
        drag_coefficient: 0.466
        drag_coefficient_table: ""
        roll_damping_coefficient: -0.073
        roll_damping_table: ""
        pitch_damping_coefficient: -2.394
        pitch_damping_table: ""
        yaw_damping_coefficient: -2.394
        yaw_damping_table: ""
    thrust:
      thrust_curve: "data/input/tables/thrust.csv"
      cut_off_time: 1000.0
    solver:
      flight_duration: 4000.0
      time_step: 0.001
      notify_interval: 5.0
      output_rate: 10
      apogee_mode: 0
"#;
        let config: InputParameter = serde_yaml::from_str(yaml)
            .expect("Failed to deserialize config");

        // Empty strings should be None
        assert!(config.flight_simulator.wind.winds_table.is_none());
        assert!(config.flight_simulator.rocket.mass.cp.x_mach_table.is_none());
        assert!(config.flight_simulator.rocket.mass.cp.y_mach_table.is_none());
        assert!(config.flight_simulator.rocket.mass.cp.z_mach_table.is_none());
    }

    #[test]
    fn test_non_empty_string_path_is_some() {
        let yaml = r#"
flight_simulator:
  launcher:
    rotation:
      magnetic_declination: -9.34
      azimuth: 292.34
      pitch: 76.0
    coordinates:
      latitude: 40.242865
      longitude: 140.01045
      elevation: 5.3
    launcher_length: 5.0
  wind:
    use_power_law: false
    winds_table: "data/input/tables/wind_table.csv"
  rocket:
    diameter: 0.145
    height: 1.889
    inertia:
      xx: 0.05
      yy: 4.12
      zz: 4.12
    mass:
      dry_weight: 16.99
      cg:
        x: 1.144
      cp:
        x: 1.374
        x_mach_table: "data/input/tables/cp_mach.csv"
        y_mach_table: ""
        z_mach_table: ""
      oxidizer_mass: 3.53
      tank_position:
        x: 0.869
      fuel_mass_before_burn: 0.643
      fuel_mass_after_burn: 0.1
      fuel_position:
        x: 0.944
    parachute:
      - full_deploy_time: 0.01
        deploy_delay: 3.0
        drag_coefficient: 1.2
        area: 0.572
    aerodynamics:
      coefficients:
        lift_coefficient_alpha: 8.387848333
        lift_coefficient_table: "data/input/tables/cnmach.csv"
        side_coefficient_beta: 8.387848333
        side_coefficient_table: ""
        drag_coefficient: 0.466
        drag_coefficient_table: ""
        roll_damping_coefficient: -0.073
        roll_damping_table: ""
        pitch_damping_coefficient: -2.394
        pitch_damping_table: ""
        yaw_damping_coefficient: -2.394
        yaw_damping_table: ""
    thrust:
      thrust_curve: "data/input/tables/thrust.csv"
      cut_off_time: 1000.0
    solver:
      flight_duration: 4000.0
      time_step: 0.001
      notify_interval: 5.0
      output_rate: 10
      apogee_mode: 0
"#;
        let config: InputParameter = serde_yaml::from_str(yaml)
            .expect("Failed to deserialize config");

        // Non-empty strings should be Some
        assert!(config.flight_simulator.wind.winds_table.is_some());
        assert!(config.flight_simulator.rocket.mass.cp.x_mach_table.is_some());
        assert_eq!(
            config.flight_simulator.wind.winds_table.unwrap().to_str().unwrap(),
            "data/input/tables/wind_table.csv"
        );
    }

    #[test]
    fn test_multiple_parachutes() {
        let yaml = r#"
flight_simulator:
  launcher:
    rotation:
      magnetic_declination: -9.34
      azimuth: 292.34
      pitch: 76.0
    coordinates:
      latitude: 40.242865
      longitude: 140.01045
      elevation: 5.3
    launcher_length: 5.0
  wind:
    use_power_law: true
    winds_table: ""
    power_law:
      wind_ref_altitude: 2.0
      ground_wind_dir: 0.0
      ground_wind_speed: 1.0
      wind_power_factor: 0.16666
  rocket:
    diameter: 0.145
    height: 1.889
    inertia:
      xx: 0.05
      yy: 4.12
      zz: 4.12
    mass:
      dry_weight: 16.99
      cg:
        x: 1.144
      cp:
        x: 1.374
        x_mach_table: ""
        y_mach_table: ""
        z_mach_table: ""
      oxidizer_mass: 3.53
      tank_position:
        x: 0.869
      fuel_mass_before_burn: 0.643
      fuel_mass_after_burn: 0.1
      fuel_position:
        x: 0.944
    parachute:
      - full_deploy_time: 0.01
        deploy_delay: 3.0
        drag_coefficient: 1.2
        area: 0.572
      - full_deploy_time: 0.02
        deploy_delay: 5.0
        drag_coefficient: 1.5
        area: 1.0
    aerodynamics:
      coefficients:
        lift_coefficient_alpha: 8.387848333
        lift_coefficient_table: ""
        side_coefficient_beta: 8.387848333
        side_coefficient_table: ""
        drag_coefficient: 0.466
        drag_coefficient_table: ""
        roll_damping_coefficient: -0.073
        roll_damping_table: ""
        pitch_damping_coefficient: -2.394
        pitch_damping_table: ""
        yaw_damping_coefficient: -2.394
        yaw_damping_table: ""
    thrust:
      thrust_curve: "data/input/tables/thrust.csv"
      cut_off_time: 1000.0
    solver:
      flight_duration: 4000.0
      time_step: 0.001
      notify_interval: 5.0
      output_rate: 10
      apogee_mode: 0
"#;
        let config: InputParameter = serde_yaml::from_str(yaml)
            .expect("Failed to deserialize config");

        assert_eq!(config.flight_simulator.rocket.parachute.len(), 2);
        assert_eq!(config.flight_simulator.rocket.parachute[0].area, 0.572);
        assert_eq!(config.flight_simulator.rocket.parachute[1].area, 1.0);
    }

    #[test]
    fn test_construction_complete_fields() {
        let path = fixture_path("landed_area.yaml");
        let file = File::open(&path).expect("Failed to open fixture file");
        let config: InputParameter = serde_yaml::from_reader(file)
            .expect("Failed to deserialize config");

        let construction = config.construction.expect("Construction should be present");

        // Check fin parameters
        let fin = construction.rocket.fin.expect("Fin should be present");
        assert!(fin.half_span.is_some());
        assert!(fin.root_chord.is_some());
        assert!(fin.tip_chord.is_some());
        assert!(fin.number_of_fins.is_some());
        assert!(fin.fin_thickness.is_some());
        assert!(fin.modulus_of_elasticity.is_some());
        assert!(fin.poisson_ratio.is_some());

        // Check body parameters
        let body = construction.rocket.body.expect("Body should be present");
        assert!(body.nose_shape.is_some());
        assert!(body.nose_length.is_some());
        assert!(body.body_bending_stiffness.is_some());

        // Check parachute parameters
        let parachute = construction.rocket.parachute.expect("Parachute should be present");
        assert!(parachute.opening_shock_factor.is_some());
    }
}

mod validator_tests {
    use super::common::fixture_path;
    use trajecsim_rs::input::loader::load_config;
    use trajecsim_rs::input::validator::{validate_config, Severity};

    #[test]
    fn test_valid_config_no_errors() {
        let path = fixture_path("landed_area.yaml");
        let config = load_config(&path).expect("Failed to load config");
        let errors = validate_config(&config);

        // Filter out warnings - only check for errors
        let critical_errors: Vec<_> = errors.iter()
            .filter(|e| e.severity == Severity::Error)
            .collect();

        assert!(
            critical_errors.is_empty(),
            "Valid config should have no errors, but found: {:?}",
            critical_errors
        );
    }

    #[test]
    fn test_missing_thrust_curve_file() {
        let yaml = r#"
flight_simulator:
  launcher:
    rotation:
      magnetic_declination: -9.34
      azimuth: 292.34
      pitch: 76.0
    coordinates:
      latitude: 40.242865
      longitude: 140.01045
      elevation: 5.3
    launcher_length: 5.0
  wind:
    use_power_law: true
    winds_table: ""
    power_law:
      wind_ref_altitude: 2.0
      ground_wind_dir: 0.0
      ground_wind_speed: 1.0
      wind_power_factor: 0.16666
  rocket:
    diameter: 0.145
    height: 1.889
    inertia:
      xx: 0.05
      yy: 4.12
      zz: 4.12
    mass:
      dry_weight: 16.99
      cg:
        x: 1.144
      cp:
        x: 1.374
        x_mach_table: ""
        y_mach_table: ""
        z_mach_table: ""
      oxidizer_mass: 3.53
      tank_position:
        x: 0.869
      fuel_mass_before_burn: 0.643
      fuel_mass_after_burn: 0.1
      fuel_position:
        x: 0.944
    parachute:
      - full_deploy_time: 0.01
        deploy_delay: 3.0
        drag_coefficient: 1.2
        area: 0.572
    aerodynamics:
      coefficients:
        lift_coefficient_alpha: 8.387848333
        lift_coefficient_table: ""
        side_coefficient_beta: 8.387848333
        side_coefficient_table: ""
        drag_coefficient: 0.466
        drag_coefficient_table: ""
        roll_damping_coefficient: -0.073
        roll_damping_table: ""
        pitch_damping_coefficient: -2.394
        pitch_damping_table: ""
        yaw_damping_coefficient: -2.394
        yaw_damping_table: ""
    thrust:
      thrust_curve: "nonexistent_file.csv"
      cut_off_time: 1000.0
    solver:
      flight_duration: 4000.0
      time_step: 0.001
      notify_interval: 5.0
      output_rate: 10
      apogee_mode: 0
"#;
        let config: trajecsim_rs::input::schema::InputParameter =
            serde_yaml::from_str(yaml).expect("Failed to deserialize");

        let errors = validate_config(&config);

        let thrust_errors: Vec<_> = errors.iter()
            .filter(|e| e.field_name.contains("thrust_curve"))
            .collect();

        assert!(!thrust_errors.is_empty(), "Should detect missing thrust curve file");
        assert_eq!(thrust_errors[0].severity, Severity::Error);
    }

    #[test]
    fn test_missing_optional_table_file() {
        let yaml = r#"
flight_simulator:
  launcher:
    rotation:
      magnetic_declination: -9.34
      azimuth: 292.34
      pitch: 76.0
    coordinates:
      latitude: 40.242865
      longitude: 140.01045
      elevation: 5.3
    launcher_length: 5.0
  wind:
    use_power_law: true
    winds_table: ""
    power_law:
      wind_ref_altitude: 2.0
      ground_wind_dir: 0.0
      ground_wind_speed: 1.0
      wind_power_factor: 0.16666
  rocket:
    diameter: 0.145
    height: 1.889
    inertia:
      xx: 0.05
      yy: 4.12
      zz: 4.12
    mass:
      dry_weight: 16.99
      cg:
        x: 1.144
      cp:
        x: 1.374
        x_mach_table: "nonexistent_cp_mach.csv"
        y_mach_table: ""
        z_mach_table: ""
      oxidizer_mass: 3.53
      tank_position:
        x: 0.869
      fuel_mass_before_burn: 0.643
      fuel_mass_after_burn: 0.1
      fuel_position:
        x: 0.944
    parachute:
      - full_deploy_time: 0.01
        deploy_delay: 3.0
        drag_coefficient: 1.2
        area: 0.572
    aerodynamics:
      coefficients:
        lift_coefficient_alpha: 8.387848333
        lift_coefficient_table: ""
        side_coefficient_beta: 8.387848333
        side_coefficient_table: ""
        drag_coefficient: 0.466
        drag_coefficient_table: ""
        roll_damping_coefficient: -0.073
        roll_damping_table: ""
        pitch_damping_coefficient: -2.394
        pitch_damping_table: ""
        yaw_damping_coefficient: -2.394
        yaw_damping_table: ""
    thrust:
      thrust_curve: "data/input/tables/thrust.csv"
      cut_off_time: 1000.0
    solver:
      flight_duration: 4000.0
      time_step: 0.001
      notify_interval: 5.0
      output_rate: 10
      apogee_mode: 0
"#;
        let config: trajecsim_rs::input::schema::InputParameter =
            serde_yaml::from_str(yaml).expect("Failed to deserialize");

        let errors = validate_config(&config);

        let cp_errors: Vec<_> = errors.iter()
            .filter(|e| e.field_name.contains("x_mach_table"))
            .collect();

        assert!(!cp_errors.is_empty(), "Should detect missing optional CP table file");
        assert_eq!(cp_errors[0].severity, Severity::Error);
    }

    #[test]
    fn test_multiple_missing_files() {
        let yaml = r#"
flight_simulator:
  launcher:
    rotation:
      magnetic_declination: -9.34
      azimuth: 292.34
      pitch: 76.0
    coordinates:
      latitude: 40.242865
      longitude: 140.01045
      elevation: 5.3
    launcher_length: 5.0
  wind:
    use_power_law: false
    winds_table: "nonexistent_wind.csv"
  rocket:
    diameter: 0.145
    height: 1.889
    inertia:
      xx: 0.05
      yy: 4.12
      zz: 4.12
    mass:
      dry_weight: 16.99
      cg:
        x: 1.144
      cp:
        x: 1.374
        x_mach_table: ""
        y_mach_table: ""
        z_mach_table: ""
      oxidizer_mass: 3.53
      tank_position:
        x: 0.869
      fuel_mass_before_burn: 0.643
      fuel_mass_after_burn: 0.1
      fuel_position:
        x: 0.944
    parachute:
      - full_deploy_time: 0.01
        deploy_delay: 3.0
        drag_coefficient: 1.2
        area: 0.572
    aerodynamics:
      coefficients:
        lift_coefficient_alpha: 8.387848333
        lift_coefficient_table: "nonexistent_lift.csv"
        side_coefficient_beta: 8.387848333
        side_coefficient_table: ""
        drag_coefficient: 0.466
        drag_coefficient_table: "nonexistent_drag.csv"
        roll_damping_coefficient: -0.073
        roll_damping_table: ""
        pitch_damping_coefficient: -2.394
        pitch_damping_table: ""
        yaw_damping_coefficient: -2.394
        yaw_damping_table: ""
    thrust:
      thrust_curve: "nonexistent_thrust.csv"
      cut_off_time: 1000.0
    solver:
      flight_duration: 4000.0
      time_step: 0.001
      notify_interval: 5.0
      output_rate: 10
      apogee_mode: 0
"#;
        let config: trajecsim_rs::input::schema::InputParameter =
            serde_yaml::from_str(yaml).expect("Failed to deserialize");

        let errors = validate_config(&config);

        // Should detect multiple missing files
        assert!(errors.len() >= 4, "Should detect at least 4 missing files");

        let has_wind_error = errors.iter().any(|e| e.field_name.contains("winds_table"));
        let has_thrust_error = errors.iter().any(|e| e.field_name.contains("thrust_curve"));
        let has_lift_error = errors.iter().any(|e| e.field_name.contains("lift_coefficient_table"));
        let has_drag_error = errors.iter().any(|e| e.field_name.contains("drag_coefficient_table"));

        assert!(has_wind_error, "Should detect missing wind table");
        assert!(has_thrust_error, "Should detect missing thrust curve");
        assert!(has_lift_error, "Should detect missing lift coefficient table");
        assert!(has_drag_error, "Should detect missing drag coefficient table");
    }

    #[test]
    fn test_error_severity_levels() {
        let yaml = r#"
flight_simulator:
  launcher:
    rotation:
      magnetic_declination: -9.34
      azimuth: 292.34
      pitch: 76.0
    coordinates:
      latitude: 40.242865
      longitude: 140.01045
      elevation: 5.3
    launcher_length: 5.0
  wind:
    use_power_law: true
    winds_table: ""
    power_law:
      wind_ref_altitude: 2.0
      ground_wind_dir: 0.0
      ground_wind_speed: 1.0
      wind_power_factor: 0.16666
  rocket:
    diameter: 0.145
    height: 1.889
    inertia:
      xx: 0.05
      yy: 4.12
      zz: 4.12
    mass:
      dry_weight: 16.99
      cg:
        x: 1.144
      cp:
        x: 1.374
        x_mach_table: ""
        y_mach_table: ""
        z_mach_table: ""
      oxidizer_mass: 3.53
      tank_position:
        x: 0.869
      fuel_mass_before_burn: 0.643
      fuel_mass_after_burn: 0.1
      fuel_position:
        x: 0.944
    parachute:
      - full_deploy_time: 0.01
        deploy_delay: 3.0
        drag_coefficient: 1.2
        area: 0.572
    aerodynamics:
      coefficients:
        lift_coefficient_alpha: 8.387848333
        lift_coefficient_table: ""
        side_coefficient_beta: 8.387848333
        side_coefficient_table: ""
        drag_coefficient: 0.466
        drag_coefficient_table: ""
        roll_damping_coefficient: -0.073
        roll_damping_table: ""
        pitch_damping_coefficient: -2.394
        pitch_damping_table: ""
        yaw_damping_coefficient: -2.394
        yaw_damping_table: ""
    thrust:
      thrust_curve: "nonexistent.csv"
      cut_off_time: 1000.0
    solver:
      flight_duration: 4000.0
      time_step: 0.001
      notify_interval: 5.0
      output_rate: 10
      apogee_mode: 0
"#;
        let config: trajecsim_rs::input::schema::InputParameter =
            serde_yaml::from_str(yaml).expect("Failed to deserialize");

        let errors = validate_config(&config);

        // All file-not-found errors should be Error severity
        for error in &errors {
            assert_eq!(error.severity, Severity::Error,
                "File not found should be Error severity, got {:?} for field {}",
                error.severity, error.field_name);
        }
    }
}
