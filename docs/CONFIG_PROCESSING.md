# コンフィグ値算出処理のアーキテクチャ案

## 要件

- YAMLから読み込んだ値を用いて、他の値を算出する（例: `reference_area = π * (diameter/2)²`）
- パラシュート面積の自動計算（終端速度から）
- 空力係数の自動計算（パラメータから）
- 計算は一度だけ行い、結果はキャッシュする
- 型安全性を保つ

## アーキテクチャ案

### 案1: Transformer パターン (推奨)

```
RawConfig (YAML直接マッピング)
    ↓ transform
ProcessedConfig (計算済み・検証済み)
    ↓ use
Simulation
```

**メリット:**
- YAMLの構造と実際に使う構造を明確に分離
- 計算ロジックを一箇所に集約
- 不変性を保ちやすい（RawConfigは変更しない）
- テストが容易

**デメリット:**
- 構造体が2セット必要
- 若干のコード量増加

**実装方針:**
```rust
// input/schema.rs - YAML直接マッピング
pub struct RawConfig { ... }

// config/config.rs - 処理済みコンフィグ
pub struct SimulationConfig {
    pub reference_area: f64,  // 計算済み
    pub parachute_area: f64,  // 計算済み
    ...
}

// config/processor.rs - 変換ロジック
impl SimulationConfig {
    pub fn from_raw(raw: RawConfig) -> Result<Self> {
        let reference_area = compute_reference_area(&raw);
        let parachute_area = compute_parachute_area(&raw)?;
        ...
    }
}
```

### 案2: Enricher パターン

```
Config (YAML直接マッピング + Option<計算値>)
    ↓ enrich
Config (全フィールド埋まった状態)
```

**メリット:**
- 構造体は1つだけ
- 段階的な処理が可能

**デメリット:**
- Option型が多くなり煩雑
- 「生データ」と「処理済みデータ」の区別が曖昧

**実装方針:**
```rust
pub struct Config {
    pub diameter: f64,  // YAML直接
    pub reference_area: Option<f64>,  // YAMLまたは計算
}

impl Config {
    pub fn enrich(mut self) -> Result<Self> {
        if self.reference_area.is_none() {
            self.reference_area = Some(compute_reference_area(self.diameter));
        }
        Ok(self)
    }
}
```

### 案3: Builder パターン

```
ConfigBuilder
    ↓ set_from_yaml
    ↓ compute_derived_values
    ↓ build
Config (immutable, 全て計算済み)
```

**メリット:**
- 構築プロセスが明確
- 段階的なバリデーション可能

**デメリット:**
- ボイラープレートが多い
- Builderコードの保守

### 案4: Computed Properties (Getter メソッド)

```rust
impl Config {
    pub fn reference_area(&self) -> f64 {
        std::f64::consts::PI * (self.diameter / 2.0).powi(2)
    }
}
```

**メリット:**
- 最もシンプル
- 元データを保持

**デメリット:**
- 毎回計算が必要（パフォーマンス）
- キャッシュが必要な場合は複雑化

## 推奨アプローチ: Transformer パターン

最もRustらしく、型安全で保守性が高い**案1: Transformer パターン**を推奨します。

### ディレクトリ構成

```
src/
├── input/           # YAML読み込み・バリデーション
│   ├── schema.rs    # RawConfig (YAMLマッピング)
│   ├── loader.rs    # YAML読み込み
│   └── validator.rs # 基本的なバリデーション
├── data/            # 処理済みデータ構造 (新規)
│   ├── mod.rs
│   ├── config.rs    # SimulationConfig (処理済み)
│   └── processor.rs # RawConfig -> SimulationConfig 変換
└── simulation/      # シミュレーション実行
    └── runner.rs    # SimulationConfigを使用
```

### 処理フロー

```
1. YAML読み込み
   loader::load_config() -> RawConfig

2. 基本バリデーション
   validator::validate_config(&RawConfig) -> Result<()>

3. 変換・計算
   processor::process_config(RawConfig) -> Result<SimulationConfig>
   - reference_area計算
   - parachute_area計算
   - 空力係数計算
   - その他の導出値計算

4. シミュレーション実行
   runner.run(SimulationConfig)
```

### メリット

1. **明確な責務分離**
   - `input`: 外部データの取り込み
   - `data`: 内部データ構造とビジネスロジック
   - `simulation`: シミュレーション実行

2. **型安全性**
   - RawConfigには計算値がないことが保証される
   - SimulationConfigには全ての必要な値があることが保証される

3. **テスタビリティ**
   - 各変換関数を個別にテスト可能
   - モックデータの作成が容易

4. **拡張性**
   - 新しい計算ロジックの追加が容易
   - 中間フォーマットの追加も可能

## 実装例

具体的な実装例は `src/data/` を参照してください。
