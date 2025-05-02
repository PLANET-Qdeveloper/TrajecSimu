"""Rocket parameter processing module"""

import json

import numpy as np
import pandas as pd
from distutils.util import strtobool
from scipy import fftpack, integrate, interpolate

from Scripts.errors import ParameterDefineError
from Scripts.statistics_wind import getStatWindVector

# Constants
DEFAULT_DT = 0.05
DEFAULT_T_MAX = 6000  # 100*60 seconds
DEFAULT_N_RECORD = 500
DEFAULT_INTEGRATION = "lsoda_odeint"

# Launch conditions
DEFAULT_ELEVATION_ANGLE = 89.0  # degrees
DEFAULT_AZIMUTH = 0.0  # degrees
DEFAULT_RAIL_LENGTH = 5.0  # meters
DEFAULT_LATITUDE = 35.0  # degrees

# Atmosphere properties
DEFAULT_TEMPERATURE = 298.0  # Kelvin at 10m altitude
DEFAULT_PRESSURE = 1.013e5  # Pascal at 10m altitude

# Wind properties
DEFAULT_WIND_DIRECTION_ORIG = -1.0
DEFAULT_WIND_DIRECTION = 315.0  # degrees
DEFAULT_WIND_SPEED = 2.0  # m/s
DEFAULT_WIND_POWER_COEF = 14.0
DEFAULT_WIND_ALT_STD = 5.0  # meters
DEFAULT_WIND_MODEL = "power"

# Rocket aerodynamics
DEFAULT_AERO_FIN_MODE = "integ"
DEFAULT_CD0 = 0.6
DEFAULT_CMP = 0.0
DEFAULT_CMQ = -4.0
DEFAULT_CL_ALPHA = 12.0  # 1/rad
DEFAULT_MACH_AOA_DEP = True

# Engine parameters
DEFAULT_T_MECO = 9.3  # seconds
DEFAULT_THRUST = 800.0  # constant thrust
DEFAULT_THRUST_INPUT_TYPE = "curve_const_t"
DEFAULT_CURVE_FITTING = True
DEFAULT_FITTING_ORDER = 15
DEFAULT_THRUST_MAG_FACTOR = 1.0
DEFAULT_TIME_MAG_FACTOR = 1.0

# Parachute parameters
DEFAULT_T_DEPLOY = 1000.0  # seconds from ignition
DEFAULT_T_PARA_DELAY = 1000.0  # seconds from apogee detection
DEFAULT_CD_PARA = 1.0
DEFAULT_S_PARA = 0.5  # square meters
DEFAULT_SECOND_PARA = False
DEFAULT_T_DEPLOY_2 = 2000.0  # seconds from apogee detection
DEFAULT_CD_PARA_2 = 1.0
DEFAULT_S_PARA_2 = 6.082  # square meters
DEFAULT_ALT_PARA_2 = -100.0  # meters

# Location parameters
DEFAULT_LOC_LAT = 34.736139
DEFAULT_LOC_LON = 139.421333
DEFAULT_LOC_ALT = 0.0
DEFAULT_LOC_MAG = -7.5

# Gravity constant
GRAVITY = np.array([0.0, 0.0, -9.81])  # in fixed coordinate


class Parameters:
    """Class for rocket parameters setup"""

    def __init__(self, csv_filename):
        """Initialize parameters from CSV file

        Args:
            csv_filename: Path to the parameter CSV file
        """
        self.params_df = self._read_parameter_file(csv_filename)

        # Initialize with default values, then overwrite with CSV data
        self.params_dict = self._get_default_parameters()
        self.overwrite_parameters(self.params_df)

    def _read_parameter_file(self, csv_filename):
        """Read parameters from CSV file"""
        try:
            params_df = pd.read_csv(csv_filename, comment="$", names=("parameter", "value"))
        except:
            params_df = pd.read_csv(csv_filename, comment="$", names=("parameter", "value", " "))

        params_df["value"] = params_df["value"].str.strip()
        return params_df

    def _get_default_parameters(self):
        """Define default parameters dictionary"""
        return {
            # Numerical executive parameters
            "dt": DEFAULT_DT,
            "t_max": DEFAULT_T_MAX,
            "N_record": DEFAULT_N_RECORD,
            "integ": DEFAULT_INTEGRATION,
            # Launch condition parameters
            "elev_angle": DEFAULT_ELEVATION_ANGLE,
            "azimuth": DEFAULT_AZIMUTH,
            "rail_length": DEFAULT_RAIL_LENGTH,
            "latitude": DEFAULT_LATITUDE,
            # Atmosphere property
            "T0": DEFAULT_TEMPERATURE,
            "p0": DEFAULT_PRESSURE,
            # Wind property
            "wind_direction_original": DEFAULT_WIND_DIRECTION_ORIG,
            "wind_direction": DEFAULT_WIND_DIRECTION,
            "wind_speed": DEFAULT_WIND_SPEED,
            "wind_power_coeff": DEFAULT_WIND_POWER_COEF,
            "wind_alt_std": DEFAULT_WIND_ALT_STD,
            "wind_model": DEFAULT_WIND_MODEL,
            # Rocket aerodynamic parameters
            "aero_fin_mode": DEFAULT_AERO_FIN_MODE,
            "Cd0": DEFAULT_CD0,
            "Cmp": DEFAULT_CMP,
            "Cmq": DEFAULT_CMQ,
            "Cl_alpha": DEFAULT_CL_ALPHA,
            "Mach_AOA_dep": DEFAULT_MACH_AOA_DEP,
            # Rocket engine parameters
            "t_MECO": DEFAULT_T_MECO,
            "thrust": DEFAULT_THRUST,
            "thrust_input_type": DEFAULT_THRUST_INPUT_TYPE,
            "curve_fitting": DEFAULT_CURVE_FITTING,
            "fitting_order": DEFAULT_FITTING_ORDER,
            "thrust_mag_factor": DEFAULT_THRUST_MAG_FACTOR,
            "time_mag_factor": DEFAULT_TIME_MAG_FACTOR,
            # Parachute parameters
            "t_deploy": DEFAULT_T_DEPLOY,
            "t_para_delay": DEFAULT_T_PARA_DELAY,
            "Cd_para": DEFAULT_CD_PARA,
            "S_para": DEFAULT_S_PARA,
            "second_para": DEFAULT_SECOND_PARA,
            "t_deploy_2": DEFAULT_T_DEPLOY_2,
            "Cd_para_2": DEFAULT_CD_PARA_2,
            "S_para_2": DEFAULT_S_PARA_2,
            "alt_para_2": DEFAULT_ALT_PARA_2,
            # Location parameters
            "loc_lat": DEFAULT_LOC_LAT,
            "loc_lon": DEFAULT_LOC_LON,
            "loc_alt": DEFAULT_LOC_ALT,
            "loc_mag": DEFAULT_LOC_MAG,
        }

    def overwrite(self, params):
        """
        Wrapper method to overwrite parameters

        Args:
            params: Parameters to update
        """
        self.overwrite_dataframe(params)
        self.overwrite_parameters(self.params_df)

    def overwrite_dataframe(self, params):
        """
        Overwrite dataframe parameter values

        Args:
            params: n×2 numpy array of parameter names and values
        """
        for param_name, param_value in params:
            self.params_df.loc[self.params_df.parameter == param_name, "value"] = param_value

    def overwrite_parameters(self, params_df_userdef={}):
        """
        Update default parameters with user-defined parameters

        Args:
            params_df_userdef: Dataframe containing parameters to update
        """
        # Update dictionary with user values
        self.params_dict.update(dict(params_df_userdef.values))

        # Set parameters from dictionary
        self._set_numerical_parameters()
        self._set_launch_conditions()
        self._set_mass_properties()
        self._set_aerodynamic_properties()
        self._setup_tipoff_properties()
        self._set_engine_properties()
        self._set_parachute_properties()
        self._set_location_properties()

    def _set_numerical_parameters(self):
        """Set numerical executive parameters"""
        try:
            self.dt = float(self.params_dict["dt"])
            self.t_max = float(self.params_dict["t_max"])
            self.N_record = float(self.params_dict["N_record"])
            self.integ = self.params_dict["integ"].strip()
        except:
            raise ParameterDefineError("executive control")

    def _set_launch_conditions(self):
        """Set launch condition parameters"""
        try:
            # Launcher property
            rail_length = float(self.params_dict["rail_length"])
            self.elev_angle = float(self.params_dict["elev_angle"])
            self.azimuth = float(self.params_dict["azimuth"])
            self.rail_height = rail_length * np.sin(np.deg2rad(self.elev_angle))

            # Launch point property
            latitude_rad = np.deg2rad(float(self.params_dict["latitude"]))
            self.omega_earth = np.array([0.0, 0.0, -7.29e-5 * np.sin(latitude_rad)])

            # Atmosphere property
            self.T0 = float(self.params_dict["T0"])
            self.p0 = float(self.params_dict["p0"])

            # Wind properties
            self._configure_wind_parameters()

            # Earth gravity
            self.grav = GRAVITY
        except:
            raise ParameterDefineError("launch condition")

    def _configure_wind_parameters(self):
        """Configure wind parameters"""
        self.wind_direction = float(self.params_dict["wind_direction"])

        # Process wind direction
        wind_direction_original = float(self.params_dict["wind_direction_original"])
        if self._is_using_original_wind_direction(wind_direction_original):
            angle_wind = np.deg2rad(-wind_direction_original + 90.0)
            print("Using original wind direction:", wind_direction_original)
        else:
            angle_wind = np.deg2rad(-self.wind_direction + 90.0)

        # Set wind unit vector (blowing TO)
        self.wind_unitvec = -np.array([np.cos(angle_wind), np.sin(angle_wind), 0.0])

        # Other wind parameters
        self.wind_speed = float(self.params_dict["wind_speed"])
        self.Cwind = 1.0 / float(self.params_dict["wind_power_coeff"])
        self.wind_alt_std = float(self.params_dict["wind_alt_std"])
        self.wind_model = self.params_dict["wind_model"]

        # Handle additional wind model configurations
        self._configure_additional_wind_models()

    def _is_using_original_wind_direction(self, wind_direction_original):
        """Check if using original wind direction"""
        return wind_direction_original != -1.0 and self.params_dict["wind_model"] == "power-es-hybrid"

    def _configure_additional_wind_models(self):
        """Configure additional wind models if needed"""
        if "forecast_csvname" in self.params_dict:
            self.wind_forecast_csvname = self.params_dict["forecast_csvname"]
            self.setup_forecast()

        if "statistics_filename" in self.params_dict:
            self.wind_statistics_filename = self.params_dict["statistics_filename"]
            self.setup_statistics()

        if "error_stat_filename" in self.params_dict:
            self.wind_error_statistics_filename = self.params_dict["error_stat_filename"]
            self.setup_error_statistics()

    def _set_mass_properties(self):
        """Set mass and inertia properties"""
        try:
            self.m_dry = float(self.params_dict["m_dry"])
            self.m_prop = float(self.params_dict["m_prop"])
            self.CG_dry = float(self.params_dict["CG_dry"])
            self.CG_prop = float(self.params_dict["CG_prop"])

            # Moment of inertia arrays
            self.MOI_dry = np.array(
                [
                    float(self.params_dict["MOI_dry_x"]),
                    float(self.params_dict["MOI_dry_y"]),
                    float(self.params_dict["MOI_dry_z"]),
                ]
            )

            self.MOI_prop = np.array(
                [
                    float(self.params_dict["MOI_prop_x"]),
                    float(self.params_dict["MOI_prop_y"]),
                    float(self.params_dict["MOI_prop_z"]),
                ]
            )
        except:
            raise ParameterDefineError("mass property")

    def _set_aerodynamic_properties(self):
        """Set aerodynamic properties"""
        try:
            # Rocket dimensions
            rocket_height = float(self.params_dict["rocket_height"])
            rocket_diameter = float(self.params_dict["rocket_diameter"])
            self.X_area = np.pi * rocket_diameter**2 / 4.0

            # Set CP location
            self._set_cp_location(rocket_height)

            # Aerodynamic parameters
            self.Cd0 = float(self.params_dict["Cd0"])
            self.Cl_alpha = float(self.params_dict["Cl_alpha"])

            # Mach/AOA dependence
            self._set_mach_aoa_dependence()

            # Fin mode and aerodynamic damping
            self._set_fin_mode_and_damping(rocket_height, rocket_diameter)

        except:
            raise ParameterDefineError("aerodynamic property")

    def _set_cp_location(self, rocket_height):
        """Set center of pressure location"""
        try:
            self.CP_body = float(self.params_dict["CP_body"])
        except:
            # Default CP: 15% forward of static margin
            self.CP_body = self.CG_dry + 0.15 * rocket_height

    def _set_mach_aoa_dependence(self):
        """Set Mach/AOA dependence flag"""
        self.Mach_AOA_dependent = self.params_dict["Mach_AOA_dep"]
        if isinstance(self.Mach_AOA_dependent, str):
            self.Mach_AOA_dependent = strtobool(self.Mach_AOA_dependent)

    def _set_fin_mode_and_damping(self, rocket_height, rocket_diameter):
        """Set fin mode and aerodynamic damping"""
        self.aero_fin_mode = self.params_dict["aero_fin_mode"].strip()

        # Aerodynamic damping moment coefficients
        Cm_omega = np.array(
            [float(self.params_dict["Cmp"]), float(self.params_dict["Cmq"]), float(self.params_dict["Cmq"])]
        )

        # Dimensional coefficients
        self.Cm_omega_bar = Cm_omega * np.array([rocket_diameter, rocket_height, rocket_height]) ** 2 * self.X_area

        # Handle individual fin computation if needed
        if self.aero_fin_mode == "indiv":
            raise NotImplementedError("fin individual computation is currently not implemented.")

    def _setup_tipoff_properties(self):
        """Set tip-off properties"""
        try:
            # Get lug positions
            lug_1st = float(self.params_dict["lug_1st"])
            self.lug_2nd = float(self.params_dict["lug_2nd"])
        except:
            # Set default values
            rocket_height = float(self.params_dict["rocket_height"])
            lug_1st = 0.3 * rocket_height
            self.lug_2nd = 0.8 * rocket_height

        # Calculate center of gravity and heights
        CG_init = (self.m_dry * self.CG_dry + self.m_prop * self.CG_prop) / (self.m_dry + self.m_prop)
        rail_length = float(self.params_dict["rail_length"])
        elev_angle_rad = np.deg2rad(self.elev_angle)

        # Heights when lugs come off the rail
        self.height_1stlug_off = (rail_length - (CG_init - lug_1st)) * np.sin(elev_angle_rad)
        self.height_2ndlug_off = (rail_length + (self.lug_2nd - CG_init)) * np.sin(elev_angle_rad)

        # Height when nozzle comes off the rail
        rocket_height = float(self.params_dict["rocket_height"])
        self.height_nozzle_off = (rail_length + (rocket_height - CG_init)) * np.sin(elev_angle_rad)

    def _set_engine_properties(self):
        """Set engine properties"""
        try:
            self.thrust_input_type = self.params_dict["thrust_input_type"].strip()
            self.thrust_mag_factor = float(self.params_dict["thrust_mag_factor"])
            self.time_mag_factor = float(self.params_dict["time_mag_factor"])

            # Handle different thrust input types
            if self.thrust_input_type == "rectangle":
                self._setup_rectangle_thrust()
            elif self.thrust_input_type in ["curve_const_t", "time_curve"]:
                self._setup_curve_thrust()
            else:
                raise ParameterDefineError("Engine property: Invalid thrust input type")

            # Set up thrust curve
            self.setup_thrust(self.thrust_mag_factor, self.time_mag_factor)

        except:
            raise ParameterDefineError("engine property")

    def _setup_rectangle_thrust(self):
        """Set up rectangular thrust profile"""
        self.t_MECO = float(self.params_dict["t_MECO"])
        self.thrustforce = float(self.params_dict["thrust"])

    def _setup_curve_thrust(self):
        """Set up curve-based thrust profile"""
        if self.thrust_input_type == "curve_const_t":
            self.thrust_dt = float(self.params_dict["thrust_dt"])

        self.thrust_filename = self.params_dict["thrust_filename"].strip()

        # Parse curve fitting parameters
        self.curve_fitting = self.params_dict["curve_fitting"]
        if isinstance(self.curve_fitting, str):
            self.curve_fitting = strtobool(self.curve_fitting)

        self.fitting_order = int(self.params_dict["fitting_order"])

    def _set_parachute_properties(self):
        """Set parachute properties"""
        try:
            self.t_deploy = float(self.params_dict["t_deploy"])
            self.t_para_delay = float(self.params_dict["t_para_delay"])
            self.Cd_para = float(self.params_dict["Cd_para"])
            self.S_para = float(self.params_dict["S_para"])

            # Second parachute flag
            self.flag_2ndpara = self.params_dict["second_para"]
            if isinstance(self.flag_2ndpara, str):
                self.flag_2ndpara = strtobool(self.flag_2ndpara)

            # Set up second parachute if needed
            if self.flag_2ndpara:
                self._setup_second_parachute()

        except:
            raise ParameterDefineError("parachute property")

    def _setup_second_parachute(self):
        """Set up second parachute parameters"""
        self.t_deploy_2 = float(self.params_dict["t_deploy_2"])
        self.Cd_para_2 = float(self.params_dict["Cd_para_2"])
        self.S_para_2 = float(self.params_dict["S_para_2"])
        self.alt_para_2 = float(self.params_dict["alt_para_2"])

    def _set_location_properties(self):
        """Set location properties"""
        try:
            self.loc_lat = float(self.params_dict["loc_lat"])
            self.loc_lon = float(self.params_dict["loc_lon"])
            self.loc_alt = float(self.params_dict["loc_alt"])
            self.loc_mag = float(self.params_dict["loc_mag"])
        except:
            raise ParameterDefineError("location property")

    def setup_thrust(self, thrust_factor=1.0, time_factor=1.0):
        """
        Set up thrust curve from dataframe input or CSV thrust curve

        Args:
            thrust_factor: Thrust magnification factor
            time_factor: Burn time magnification factor
        """
        if self.thrust_input_type == "rectangle":
            self._setup_rectangle_thrust_curve(thrust_factor, time_factor)
        else:
            self._setup_csv_thrust_curve(thrust_factor, time_factor)

        # Calculate engine properties
        self._calculate_engine_properties()

        # Set up thrust function
        self._setup_thrust_function()

    def _setup_rectangle_thrust_curve(self, thrust_factor, time_factor):
        """Set up rectangular thrust curve"""
        self.time_array = np.array([0, self.t_MECO]) * time_factor
        self.thrust_array = np.ones(2) * self.thrustforce * thrust_factor

    def _setup_csv_thrust_curve(self, thrust_factor, time_factor):
        """Set up thrust curve from CSV file"""
        # Read the CSV file
        input_raw = np.array(pd.read_csv(self.thrust_filename, header=None))

        if self.thrust_input_type == "curve_const_t":
            self._process_constant_time_curve(input_raw, thrust_factor, time_factor)
        elif self.thrust_input_type == "time_curve":
            self._process_time_curve(input_raw, thrust_factor, time_factor)

    def _process_constant_time_curve(self, input_raw, thrust_factor, time_factor):
        """Process thrust curve with constant time step"""
        time_raw = input_raw[:, 0]
        thrust_raw = input_raw[:, 1]

        self.time_array = time_raw * time_factor
        self.thrust_array = thrust_raw * thrust_factor

    def _process_time_curve(self, input_raw, thrust_factor, time_factor):
        """Process time and thrust curve"""
        self.time_array = input_raw[:, 0]
        self.thrust_array = input_raw[:, 1]

        # Cut-off low values and apply magnification
        mask = self.thrust_array >= 0.01 * np.max(self.thrust_array)
        self.time_array = self.time_array[mask] * time_factor
        self.time_array -= self.time_array[0]  # Start from zero
        self.thrust_array = self.thrust_array[mask] * thrust_factor

    def _calculate_engine_properties(self):
        """Calculate engine properties from thrust curve"""
        self.Thrust_max = np.max(self.thrust_array)
        self.Impulse_total = integrate.trapz(self.thrust_array, self.time_array)
        self.Thrust_avg = self.Impulse_total / self.time_array[-1]
        self.t_MECO = self.time_array[-1]
        self.It_poly_error = 0.0

    def _setup_thrust_function(self):
        """Set up the thrust function"""
        if self.thrust_input_type == "rectangle":
            # Simple interpolation for rectangle thrust
            self.thrust_function = interpolate.interp1d(self.time_array, self.thrust_array, fill_value="extrapolate")
        else:
            # Process curve-based thrust
            if self.thrust_input_type == "curve_const_t":
                self._process_fft_filtering()

            # Set up thrust function with curve fitting or interpolation
            if self.curve_fitting:
                self._setup_curve_fitted_thrust()
            else:
                self.thrust_function = interpolate.interp1d(
                    self.time_array, self.thrust_array, fill_value="extrapolate"
                )

    def _process_fft_filtering(self):
        """Apply FFT filtering to smooth thrust curve"""
        # FFT (fast fourier transformation)
        tf = fftpack.fft(self.thrust_array)
        freq = fftpack.fftfreq(len(self.thrust_array), self.thrust_dt)

        # Filtering - cut off frequency 10 Hz
        fs = 10.0
        tf2 = np.copy(tf)
        tf2[np.abs(freq) > fs] = 0

        # Inverse FFT and clean up
        self.thrust_array = np.real(fftpack.ifft(tf2))

        # Filter out low values
        roi_mask = self.thrust_array >= (0.01 * np.max(self.thrust_array))
        self.time_array = self.time_array[roi_mask]
        self.time_array -= self.time_array[0]  # Start from zero
        self.thrust_array = self.thrust_array[roi_mask]
        self.thrust_array[self.thrust_array < 0] = 0

    def _setup_curve_fitted_thrust(self):
        """Set up polynomial curve-fitted thrust function"""
        # Curve fitting
        n_fit = int(self.fitting_order)
        a_fit = np.polyfit(self.time_array, self.thrust_array, n_fit)

        # Create polynomial function
        self.thrust_function = np.poly1d(a_fit)

        # Calculate total impulse error
        time_for_poly = np.linspace(self.time_array[0], self.time_array[-1], 10000)
        thrust_poly = self.thrust_function(time_for_poly)
        thrust_poly[thrust_poly < 0.0] = 0.0  # Clip negative values

        # Calculate total impulse and error
        Impulse_total_poly = integrate.trapz(thrust_poly, time_for_poly)
        self.It_poly_error = abs(Impulse_total_poly - self.Impulse_total) / self.Impulse_total * 100.0

    def setup_aero_coeffs(self):
        """Set up aerodynamic coefficients and CP location interpolations"""
        if self.Mach_AOA_dependent:
            self._setup_mach_dependent_coeffs()
        else:
            self._setup_constant_coeffs()

    def _setup_mach_dependent_coeffs(self):
        """Set up Mach-number dependent coefficient functions"""
        # Load drag coefficient data
        try:
            data = np.loadtxt("bin/Cd0.dat", delimiter=",", skiprows=1)
        except:
            raise FileNotFoundError("bin/Cd0.dat not found")

        # Create drag coefficient interpolation
        Mach_array = data[:, 0]
        Cd0_array = data[:, 1] * (self.Cd0 / data[0, 1])  # Scaling
        self.f_cd0 = interpolate.interp1d(Mach_array, Cd0_array, kind="linear")

        # Load lift coefficient data
        try:
            data = np.loadtxt("bin/Clalpha.dat", delimiter=",", skiprows=1)
        except:
            raise FileNotFoundError("bin/Clalpha.dat not found")

        # Create lift coefficient interpolation
        Mach_array = data[:, 0]
        Clalpha_array = data[:, 1] * (self.Cl_alpha / data[0, 1])  # Scaling
        self.f_cl_alpha = interpolate.interp1d(Mach_array, Clalpha_array, kind="linear")

        # Load CP location data
        try:
            df = pd.read_csv("bin/CPloc.csv", header=None, na_values="Mach/AOA")
        except:
            raise FileNotFoundError("bin/CPloc.csv not found")

        # Process CP location data
        Mach_array = np.array(df.iloc[1:, 0])
        AOA_array = np.array(df.iloc[0, 1:]) * np.pi / 180.0  # Convert to radians

        # Create CP location interpolation
        CPloc_array = np.array(df.iloc[1:, 1:])
        tmpfunc = interpolate.RectBivariateSpline(Mach_array, AOA_array, CPloc_array)
        CPloc_array *= self.CP_body / tmpfunc(0.3, np.deg2rad(0.0))

        self.f_CPloc = interpolate.RectBivariateSpline(Mach_array, AOA_array, CPloc_array)

    def _setup_constant_coeffs(self):
        """Set up constant coefficient functions"""
        # Simple functions that return constant values
        self.f_cd0 = lambda a: self.Cd0
        self.f_cl_alpha = lambda a: self.Cl_alpha
        self.f_CPloc = lambda a, b: np.array([self.CP_body])

    def setup_wind(self):
        """Set up wind model"""
        wind_models = {
            "power": self.wind_power,
            "power_Gust": self.wind_power_Gust,
            "log": self.wind_log,
            "forecast": self.wind_forecast,
            "statistics": self.wind_statistics,
            "error-statistics": self.wind_error_statistics,
            "power-es-hybrid": self._create_power_es_hybrid,
            "power-forecast-hybrid": self._create_power_forecast_hybrid,
            "log-forecast-hybrid": self._create_log_forecast_hybrid,
            "power-statistics-hybrid": self._create_power_statistics_hybrid,
        }

        if self.wind_model in wind_models:
            if callable(wind_models[self.wind_model]):
                self.wind = wind_models[self.wind_model]()
            else:
                self.wind = wind_models[self.wind_model]
        else:
            raise ParameterDefineError(f"Unknown wind model: {self.wind_model}")

    def _create_power_es_hybrid(self):
        """Create power-error-statistics hybrid wind model"""

        def wind_power_es(h):
            if h < 0.0:
                h = 0.0

            boundary_alt = 300.0

            if h <= boundary_alt:
                # Use power law below boundary
                return self.wind_power(h)
            else:
                # Use error statistics above boundary
                return self.wind_error_statistics(h)

        return wind_power_es

    def _create_power_forecast_hybrid(self):
        """Create power-forecast hybrid wind model"""

        def wind_power_forecast(h):
            if h < 0.0:
                h = 0.0

            boundary_alt = 300.0
            transition = 100.0

            if h <= boundary_alt - transition:
                # Use power law only
                return self.wind_power(h)
            elif h <= boundary_alt + transition:
                # Use weighted average in transition zone
                weight = (h - (boundary_alt - transition)) / (2 * transition)
                return weight * self.wind_forecast(h) + (1 - weight) * self.wind_power(h)
            else:
                # Use forecast only
                return self.wind_forecast(h)

        return wind_power_forecast

    def _create_log_forecast_hybrid(self):
        """Create log-forecast hybrid wind model"""

        def wind_log_forecast(h):
            if h <= 0.1:
                # Avoid log(0)
                h = 0.1

            boundary_alt = 300.0
            transition = 50.0

            if h <= boundary_alt - transition:
                # Use log law only
                return self.wind_log(h)
            elif h <= boundary_alt + transition:
                # Use weighted average in transition zone
                weight = (h - (boundary_alt - transition)) / (2 * transition)
                return weight * self.wind_forecast(h) + (1 - weight) * self.wind_log(h)
            else:
                # Use forecast only
                return self.wind_forecast(h)

        return wind_log_forecast

    def _create_power_statistics_hybrid(self):
        """Create power-statistics hybrid wind model"""

        def wind_power_statistics(h):
            if h < 0.0:
                h = 0.0

            boundary_alt = 400.0
            transition = 100.0

            if h <= boundary_alt - transition:
                # Use power law only
                return self.wind_power(h)
            elif h <= boundary_alt + transition:
                # Use weighted average in transition zone
                weight = (h - (boundary_alt - transition)) / (2 * transition)
                return weight * self.wind_statistics(h) + (1 - weight) * self.wind_power(h)
            else:
                # Use statistics only
                return self.wind_statistics(h)

        return wind_power_statistics

    def setup_error_statistics(self):
        """Set up error statistics wind model"""
        try:
            with open(self.wind_error_statistics_filename, "r") as f:
                params = json.load(f)
        except:
            raise FileNotFoundError("Wind statistics data file not found")

        # Get altitude axis and wind forecast
        alt = params["alt_axis"]
        forecast_wind_array = self.wind_forecast(alt)[:2].T
        n_alt = len(alt)

        # Get statistical wind vector
        wind_tmp = getStatWindVector(
            statistics_parameters=params, wind_direction_deg=self.wind_direction, wind_std=forecast_wind_array
        )

        # Create 3D wind vector and interpolation function
        wind_vec_stat = np.c_[wind_tmp[0], wind_tmp[1], [0] * n_alt].T
        self.wind_error_statistics = interpolate.interp1d(alt, wind_vec_stat, fill_value="extrapolate")

    def setup_forecast(self):
        """Set up forecast wind model from CSV file"""
        try:
            df = pd.read_csv(self.wind_forecast_csvname)
        except:
            raise FileNotFoundError("Wind forecast data file not found")

        # Get altitude and wind components
        alt = np.array(df["altitude"])
        wind_W2E_tmp = np.array(df["Wind (from west)"])
        wind_S2N_tmp = np.array(df["Wind (from south)"])
        wind_UP = np.array(df["Wind (vertical)"])

        # Apply magnetic angle correction
        theta = np.deg2rad(8.9)
        wind_W2E = wind_W2E_tmp * np.cos(theta) + wind_S2N_tmp * np.sin(theta)
        wind_S2N = -wind_W2E_tmp * np.sin(theta) + wind_S2N_tmp * np.cos(theta)

        # Create 3D wind vector and interpolation function
        wind_vec_fore = np.c_[wind_W2E, wind_S2N, wind_UP].T
        self.wind_forecast = interpolate.interp1d(alt, wind_vec_fore, fill_value="extrapolate")

    def setup_statistics(self):
        """Set up statistical wind model from JSON file"""
        try:
            with open(self.wind_statistics_filename, "r") as f:
                params = json.load(f)
        except:
            raise FileNotFoundError("Wind statistics data file not found")

        # Get altitude axis
        alt = params["alt_axis"]
        n_alt = len(alt)

        # Get statistical wind vector
        wind_tmp = getStatWindVector(statistics_parameters=params, wind_direction_deg=self.wind_direction)

        # Create 3D wind vector and interpolation function
        wind_vec_stat = np.c_[wind_tmp[0], wind_tmp[1], [0] * n_alt].T
        self.wind_statistics = interpolate.interp1d(alt, wind_vec_stat, fill_value="extrapolate")

    def wind_log(self, h):
        """
        Calculate wind vector using logarithmic law

        Args:
            h: Height above ground [m]

        Returns:
            Wind vector [m/s]
        """
        if h <= 0.1:
            # Avoid log(0)
            h = 0.1

        # Surface roughness parameter
        roughness_surf = 0.0003

        # Calculate wind vector
        wind_vec = (
            self.wind_unitvec
            * self.wind_speed
            * (np.log10(h / roughness_surf) / np.log10(self.wind_alt_std / roughness_surf))
        )

        return wind_vec

    def wind_power(self, h):
        """
        Calculate wind vector using power law

        Args:
            h: Height above ground [m]

        Returns:
            Wind vector [m/s]
        """
        if h < 0.0:
            h = 0.0

        # Calculate wind vector using power law
        wind_vec = self.wind_unitvec * self.wind_speed * (h / self.wind_alt_std) ** self.Cwind

        return wind_vec

    def wind_power_Gust(self, h):
        """
        Calculate wind vector with gusts using power law

        Args:
            h: Height above ground [m]

        Returns:
            Wind vector with gust effects [m/s]
        """
        if h < 0.0:
            h = 0.0

        # Height boundaries for gust zones
        boundary_alt = 10.0
        boundary_alt2 = 25.0

        # Base wind from power law
        base_wind = self.wind_unitvec * self.wind_speed * (h / self.wind_alt_std) ** self.Cwind

        # Add gust effects based on height
        if h < boundary_alt:
            return base_wind
        elif h < boundary_alt + 10:
            return base_wind + np.array([5, 3, 0])
        elif h < boundary_alt2:
            return base_wind + np.array([5, -3, 0])
        else:
            return base_wind + np.array([-7, -10, 0])
