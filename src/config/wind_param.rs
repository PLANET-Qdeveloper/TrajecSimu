use serde::Deserialize;
use std::fs::File;
use std::io::{BufRead, BufReader};
use std::path::Path;
use uom::si::angle::degree;
use uom::si::f64::*;
use uom::si::length::meter;
use uom::si::velocity::meter_per_second;

use crate::input::schema::Wind;

/// 風速テーブルの1エントリ
#[derive(Debug, Clone, Copy)]
pub struct WindEntry {
    pub altitude: Length, // 高度 (m)
    pub speed: Velocity,  // 風速 (m/s)
    pub direction: Angle, // 風向 (deg)
}

#[derive(Deserialize)]
pub struct WindEntryRaw {
    pub altitude: f64,
    pub speed: f64,
    pub direction: f64,
}

impl From<WindEntryRaw> for WindEntry {
    fn from(value: WindEntryRaw) -> Self {
        Self {
            altitude: Length::new::<meter>(value.altitude),
            speed: Velocity::new::<meter_per_second>(value.speed),
            direction: Angle::new::<degree>(value.direction),
        }
    }
}

/// 統一的な風速テーブル
#[derive(Debug, Clone)]
pub struct WindTable {
    entries: Vec<WindEntry>,
}

impl WindTable {
    /// べき法則からテーブルを生成
    pub fn from_power_law(
        ref_altitude: f64,
        ref_speed: f64,
        direction: f64,
        exponent: f64,
        max_altitude: f64,
        step: f64,
    ) -> Self {
        let entries = std::iter::successors(Some(0.0), |&z| {
            let next = z + step;
            if next <= max_altitude {
                Some(next)
            } else {
                None
            }
        })
        .map(|z| {
            let speed = if z <= 0.0 {
                0.0
            } else {
                ref_speed * (z / ref_altitude).powf(exponent)
            };
            WindEntry {
                altitude: Length::new::<meter>(z),
                speed: Velocity::new::<meter_per_second>(speed),
                direction: Angle::new::<degree>(direction),
            }
        })
        .collect();

        Self { entries }
    }

    /// CSVファイルからテーブルを読み込み
    /// 形式: altitude,speed,direction
    pub fn from_csv(path: &Path) -> Result<Self, WindTableError> {
        let file = File::open(path).map_err(|e| WindTableError::FileOpen(path.to_path_buf(), e))?;

        let mut rdr = csv::Reader::from_reader(file);
        let columns = rdr.headers();
        if let Err(_) = columns {
            return Err(WindTableError::MissingColumns);
        }
        let columns = columns.unwrap();
        if !columns.iter().any(|c| c == "altitude") {
            return Err(WindTableError::MissingAltitude);
        }
        if !columns.iter().any(|c| c == "speed") {
            return Err(WindTableError::MissingSpeed);
        }
        if !columns.iter().any(|c| c == "direction") {
            return Err(WindTableError::MissingAngle);
        }

        let wind_table = rdr
            .deserialize::<WindEntryRaw>()
            .filter_map(|r: Result<WindEntryRaw, _>| r.ok())
            .map(WindEntry::from)
            .collect();

        Ok(Self {
            entries: wind_table,
        })
    }

    /// 設定から適切なソースを選択してテーブルを生成
    pub fn from_config(wind: &Wind, max_altitude: f64, step: f64) -> Result<Self, WindTableError> {
        if wind.use_power_law {
            let pl = wind
                .power_law
                .as_ref()
                .ok_or(WindTableError::MissingPowerLaw)?;

            Ok(Self::from_power_law(
                pl.wind_ref_altitude,
                pl.ground_wind_speed,
                pl.ground_wind_dir,
                pl.wind_power_factor,
                max_altitude,
                step,
            ))
        } else {
            let path = wind
                .winds_table
                .as_ref()
                .ok_or(WindTableError::MissingTable)?;
            Self::from_csv(path)
        }
    }
    /// テーブルの内容を取得（デバッグ・出力用）
    pub fn entries(&self) -> &[WindEntry] {
        &self.entries
    }

    /// テーブルサイズ
    pub fn len(&self) -> usize {
        self.entries.len()
    }
}

/// WindTable関連のエラー
#[derive(Debug)]
pub enum WindTableError {
    FileOpen(std::path::PathBuf, std::io::Error),
    Read(std::io::Error),
    InvalidFormat { line: usize, content: String },
    ParseError { line: usize, field: String },
    Empty,
    MissingPowerLaw,
    MissingAltitude,
    MissingAngle,
    MissingSpeed,
    MissingColumns,
    MissingTable,
}

impl std::fmt::Display for WindTableError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::FileOpen(path, e) => {
                write!(f, "ファイルを開けません: {} ({})", path.display(), e)
            }
            Self::Read(e) => write!(f, "読み込みエラー: {}", e),
            Self::InvalidFormat { line, content } => {
                write!(f, "{}行目: フォーマットが不正です: {}", line, content)
            }
            Self::ParseError { line, field } => {
                write!(f, "{}行目: {}の解析に失敗しました", line, field)
            }
            Self::Empty => write!(f, "テーブルが空です"),
            Self::MissingPowerLaw => write!(f, "べき法則が設定されていません"),
            Self::MissingAltitude => write!(f, "altitudeが設定されていません"),
            Self::MissingAngle => write!(f, "angleが設定されていません"),
            Self::MissingSpeed => write!(f, "speedが設定されていません"),
            Self::MissingColumns => write!(f, "列名が設定されていません"),
            Self::MissingTable => write!(f, "風速テーブルがありません"),
        }
    }
}

impl std::error::Error for WindTableError {}
