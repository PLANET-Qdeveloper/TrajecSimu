# コンフィグ処理実装サマリー

## 実装した内容

### 1. パスバリデーション (src/input/validator.rs)

全ての設定ファイルパスが存在することを確認する機能を追加しました。

**チェック対象:**
- `launcher.range_kmz`
- `wind.winds_table`
- `mass.cp.{x,y,z}_mach_table`
- `thrust.thrust_curve` (必須)
- `aerodynamics.coefficients.*_table`

**使用方法:**
```rust
use trajecsim_rs::input::{loader, validator};

let config = loader::load_config("config.yaml")?;
validator::validate_config(&config)?;  // パス存在チェックを含む
```

### 2. コンフィグ処理アーキテクチャ (Transformer パターン)

#### 構造

```
input/schema.rs (RawConfig)
    ↓ loader::load_config
RawConfig (YAML直接マッピング)
    ↓ validator::validate_config
Validated RawConfig
    ↓ processor::process_config
SimulationConfig (計算済み・型安全)
    ↓
Simulation実行
```

#### モジュール構成

**src/data/** (新規作成)
- `config.rs`: `SimulationConfig` - 処理済みデータ構造
- `processor.rs`: `RawConfig` → `SimulationConfig` 変換ロジック

#### 主な特徴

1. **明確な責務分離**
   - `RawConfig`: YAML構造の直接マッピング
   - `SimulationConfig`: シミュレーション用の最適化された構造

2. **事前計算された値**
   ```rust
   pub struct RocketConfig {
       pub diameter: f64,
       pub reference_area: f64,  // ← π * (diameter/2)² を事前計算
       pub parachute: ParachuteConfig,
   }

   pub struct ParachuteConfig {
       pub area: f64,  // ← terminal_velocity から自動計算済み
   }
   ```

3. **型で表現されたモード切り替え**
   ```rust
   pub enum AerodynamicsMode {
       Coefficients { ... },  // 係数直接指定
       Parameters { ... },    // 形状から自動計算
   }
   ```

4. **計算関数の提供**
   - `compute_reference_area(diameter) -> f64`
   - `compute_parachute_area(v_terminal, Cd, mass) -> f64`
   - `compute_lift_coefficient(fin, body) -> f64`
   - `compute_drag_coefficient(fin, body) -> f64`

## 使用例

```rust
use trajecsim_rs::input::{loader, validator};
use trajecsim_rs::data::processor;

// 1. YAML読み込み
let raw_config = loader::load_config("config.yaml")?;

// 2. バリデーション (パス存在チェック含む)
validator::validate_config(&raw_config)?;

// 3. 処理・変換 (値の計算)
let sim_config = processor::process_config(raw_config)?;

// 4. 使用
println!("Reference area: {} m²", sim_config.rocket.reference_area);
println!("Parachute area: {} m²", sim_config.rocket.parachute.area);
```

## 計算ロジック例

### Reference Area

```rust
pub fn compute_reference_area(diameter: f64) -> f64 {
    std::f64::consts::PI * (diameter / 2.0).powi(2)
}
```

### Parachute Area

```rust
/// Formula: A = (2 * m * g) / (ρ * Cd * v_t²)
pub fn compute_parachute_area(
    terminal_velocity: f64,
    drag_coefficient: f64,
    mass: f64,
) -> f64 {
    const G: f64 = 9.81;      // m/s²
    const RHO: f64 = 1.225;   // kg/m³ (sea level)

    (2.0 * mass * G) / (RHO * drag_coefficient * terminal_velocity.powi(2))
}
```

### Aerodynamic Coefficients

形状パラメータから空力係数を計算（簡略版、実際はより複雑なモデルを使用）:

```rust
pub fn compute_lift_coefficient(fin, body) -> f64 {
    let aspect_ratio = fin_span / mean_chord;
    2.0 * PI * aspect_ratio / (aspect_ratio + 2.0)
}

pub fn compute_drag_coefficient(fin, body) -> f64 {
    let body_drag = match body.nose_shape {
        "ogive" => 0.15,
        "conical" => 0.25,
        // ...
    };
    let fin_drag = 0.01 * fin.number_of_fins * fin.thickness;
    body_drag + fin_drag
}
```

## テスト

```bash
# バリデーションテスト
cargo run --example test_validation

# コンフィグ処理テスト
cargo run --example test_config_processing
```

## 今後の拡張

このアーキテクチャにより、以下の拡張が容易になります:

1. **新しい計算ロジックの追加**
   - `processor.rs` に関数を追加するだけ

2. **中間データ構造の追加**
   - 例: `RawConfig` → `ValidatedConfig` → `SimulationConfig`

3. **計算のカスタマイズ**
   - 計算関数を trait として抽象化
   - ユーザー定義の計算ロジックの注入

4. **キャッシュ戦略**
   - 必要に応じて `SimulationConfig` をシリアライズ/デシリアライズ

## メリット

✅ **型安全性**: コンパイル時に構造の正しさを保証
✅ **パフォーマンス**: 計算は一度だけ
✅ **保守性**: 計算ロジックが一箇所に集約
✅ **テスタビリティ**: 各関数を独立してテスト可能
✅ **拡張性**: 新しい計算の追加が容易
