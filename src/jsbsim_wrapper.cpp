#include "FGFDMExec.h"
#include <string>

extern "C" {
    // FDMExecの作成と破棄
    void* jsbsim_create() {
        return new JSBSim::FGFDMExec();
    }

    void jsbsim_destroy(void* ptr) {
        delete static_cast<JSBSim::FGFDMExec*>(ptr);
    }

    // モデルのロード
    bool jsbsim_load_model(void* ptr, const char* model_name) {
        auto fdm = static_cast<JSBSim::FGFDMExec*>(ptr);
        return fdm->LoadModel(model_name);
    }

    // スクリプトのロード
    bool jsbsim_load_script(void* ptr, const char* script_path, double delta_t) {
        auto fdm = static_cast<JSBSim::FGFDMExec*>(ptr);
        return fdm->LoadScript(SGPath(script_path), delta_t);
    }

    // シミュレーション実行
    bool jsbsim_run(void* ptr) {
        auto fdm = static_cast<JSBSim::FGFDMExec*>(ptr);
        return fdm->Run();
    }

    bool jsbsim_run_ic(void* ptr) {
        auto fdm = static_cast<JSBSim::FGFDMExec*>(ptr);
        return fdm->RunIC();
    }

    // プロパティアクセス
    double jsbsim_get_property_value(void* ptr, const char* property) {
        auto fdm = static_cast<JSBSim::FGFDMExec*>(ptr);
        return fdm->GetPropertyValue(property);
    }

    void jsbsim_set_property_value(void* ptr, const char* property, double value) {
        auto fdm = static_cast<JSBSim::FGFDMExec*>(ptr);
        fdm->SetPropertyValue(property, value);
    }

    // 時間関連
    double jsbsim_get_sim_time(void* ptr) {
        auto fdm = static_cast<JSBSim::FGFDMExec*>(ptr);
        return fdm->GetSimTime();
    }

    double jsbsim_get_delta_t(void* ptr) {
        auto fdm = static_cast<JSBSim::FGFDMExec*>(ptr);
        return fdm->GetDeltaT();
    }

    void jsbsim_set_dt(void* ptr, double dt) {
        auto fdm = static_cast<JSBSim::FGFDMExec*>(ptr);
        fdm->Setdt(dt);
    }

    // パス設定
    bool jsbsim_set_root_dir(void* ptr, const char* path) {
        auto fdm = static_cast<JSBSim::FGFDMExec*>(ptr);
        fdm->SetRootDir(SGPath(path));
        return true;
    }

    bool jsbsim_set_aircraft_path(void* ptr, const char* path) {
        auto fdm = static_cast<JSBSim::FGFDMExec*>(ptr);
        return fdm->SetAircraftPath(SGPath(path));
    }

    bool jsbsim_set_engine_path(void* ptr, const char* path) {
        auto fdm = static_cast<JSBSim::FGFDMExec*>(ptr);
        return fdm->SetEnginePath(SGPath(path));
    }

    bool jsbsim_set_systems_path(void* ptr, const char* path) {
        auto fdm = static_cast<JSBSim::FGFDMExec*>(ptr);
        return fdm->SetSystemsPath(SGPath(path));
    }

    bool jsbsim_set_output_path(void* ptr, const char* path) {
        auto fdm = static_cast<JSBSim::FGFDMExec*>(ptr);
        return fdm->SetOutputPath(SGPath(path));
    }

    // 出力制御
    void jsbsim_disable_output(void* ptr) {
        auto fdm = static_cast<JSBSim::FGFDMExec*>(ptr);
        fdm->DisableOutput();
    }

    void jsbsim_enable_output(void* ptr) {
        auto fdm = static_cast<JSBSim::FGFDMExec*>(ptr);
        fdm->EnableOutput();
    }

    void jsbsim_hold(void* ptr) {
        auto fdm = static_cast<JSBSim::FGFDMExec*>(ptr);
        fdm->Hold();
    }

    void jsbsim_resume(void* ptr) {
        auto fdm = static_cast<JSBSim::FGFDMExec*>(ptr);
        fdm->Resume();
    }

    bool jsbsim_holding(void* ptr) {
        auto fdm = static_cast<JSBSim::FGFDMExec*>(ptr);
        return fdm->Holding();
    }
}
