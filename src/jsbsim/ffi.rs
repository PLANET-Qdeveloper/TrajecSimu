// JSBSim C API FFI declarations
use std::ffi::c_void;
use std::os::raw::c_char;

extern "C" {
    // FDMExecの作成と破棄
    pub fn jsbsim_create() -> *mut c_void;
    pub fn jsbsim_destroy(ptr: *mut c_void);

    // モデルのロード
    pub fn jsbsim_load_model(ptr: *mut c_void, model_name: *const c_char) -> bool;
    pub fn jsbsim_load_script(ptr: *mut c_void, script_path: *const c_char, delta_t: f64) -> bool;

    // シミュレーション実行
    pub fn jsbsim_run(ptr: *mut c_void) -> bool;
    pub fn jsbsim_run_ic(ptr: *mut c_void) -> bool;

    // プロパティアクセス
    pub fn jsbsim_get_property_value(ptr: *mut c_void, property: *const c_char) -> f64;
    pub fn jsbsim_set_property_value(ptr: *mut c_void, property: *const c_char, value: f64);

    // 時間関連
    pub fn jsbsim_get_sim_time(ptr: *mut c_void) -> f64;
    pub fn jsbsim_get_delta_t(ptr: *mut c_void) -> f64;
    pub fn jsbsim_set_dt(ptr: *mut c_void, dt: f64);

    // パス設定
    pub fn jsbsim_set_root_dir(ptr: *mut c_void, path: *const c_char) -> bool;
    pub fn jsbsim_set_aircraft_path(ptr: *mut c_void, path: *const c_char) -> bool;
    pub fn jsbsim_set_engine_path(ptr: *mut c_void, path: *const c_char) -> bool;
    pub fn jsbsim_set_systems_path(ptr: *mut c_void, path: *const c_char) -> bool;
    pub fn jsbsim_set_output_path(ptr: *mut c_void, path: *const c_char) -> bool;

    // 出力制御
    pub fn jsbsim_disable_output(ptr: *mut c_void);
    pub fn jsbsim_enable_output(ptr: *mut c_void);
    pub fn jsbsim_hold(ptr: *mut c_void);
    pub fn jsbsim_resume(ptr: *mut c_void);
    pub fn jsbsim_holding(ptr: *mut c_void) -> bool;
}
