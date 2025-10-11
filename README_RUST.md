# TrajecSimu Rust Implementation

Rustへの移植版TrajecSimu - ロケット軌道シミュレーションツール

## プロジェクト構成

```
src/
├── main.rs              # エントリーポイント
├── lib.rs               # ライブラリルート
├── input/               # 入力処理モジュール
│   ├── mod.rs
│   ├── schema.rs        # 入力データ構造定義（serde）
│   ├── loader.rs        # YAML設定ファイルの読み込み
│   └── validator.rs     # 入力バリデーション
├── simulation/          # シミュレーション実行モジュール
│   ├── mod.rs
│   ├── template.rs      # Handlebarsテンプレートレンダリング
│   └── runner.rs        # JSBSim実行と並列処理
└── output/              # 出力処理モジュール
    ├── mod.rs
    ├── processor.rs     # CSV入出力
    └── analyzer.rs      # 結果解析（最高高度、着地点等）
```

## Pythonバージョンからの主な変更点

### アーキテクチャの変更

1. **パラメータ積の削除**
   - `parameter_product`機能を削除
   - 実行時に単一のパラメータセットのみを受け付ける

2. **責務の明確な分離**
   - **input**: 設定の読み込み、バリデーション、データ構造定義
   - **simulation**: テンプレートレンダリング、JSBSim並列実行のみ
   - **output**: JSBSim出力の変形・解釈

3. **テンプレートシステムの簡素化**
   - テンプレート内での演算を最小化
   - 入力スキーマに合わせたテンプレート構造
   - Handlebarsを使用したシンプルなレンダリング

### スキーマ設計

- Pydanticの代わりにserdeを使用
- `input::schema`に全てのデータ構造を集約
- Rustの型システムを活用した堅牢なバリデーション

## ビルドと実行

### 依存関係のインストール

```bash
cargo build --release
```

### 実行

```bash
cargo run --release -- \
  --config config/input/landed_area.yaml \
  --output-dir config/result \
  --template-dir param-xml-template
```

または短縮形：

```bash
cargo run --release -- -c config/input/landed_area.yaml -o config/result
```

## 使用ライブラリ

- **serde / serde_yaml**: YAML設定のデシリアライズ
- **handlebars**: XMLテンプレートレンダリング
- **clap**: CLIパーサー
- **anyhow**: エラーハンドリング
- **rayon**: 並列処理（将来の拡張用）
- **csv**: CSV入出力

## 開発状況

### 完了

- [x] プロジェクト構成の確立
- [x] 入力スキーマ定義
- [x] YAML設定ローダー
- [x] バリデーション機能
- [x] テンプレートレンダリング
- [x] JSBSim実行ランナー
- [x] 出力処理・解析

### TODO

- [ ] テンプレートファイルの作成（aircraft.xml.hbs, simulation.xml.hbs）
- [ ] JSBSim出力フォーマットに合わせたCSV構造体の調整
- [ ] エラーハンドリングの強化
- [ ] ログ機能の追加
- [ ] テストの作成
- [ ] ドキュメント整備

## Python版との互換性

既存のPythonコードは`src/`以外のディレクトリに保持されています。
YAMLファイルフォーマットは互換性を保つように設計されています。

## ライセンス

（元のプロジェクトに準ずる）
