import asyncio
import glob
from pathlib import Path

import pandas as pd

# Columns kept in the combined per-road Excel files (subset of the ~51 columns
# in the platform's segment csvs)
EXPORT_COLUMNS = [
    "route_name",
    "date_range_name",
    "time_set_name",
    "segment_geometry",
    "segment_start_point",
    "segment_end_point",
    "segment_id",
    "bearing",
    "speed_limit",
    "street_name",
    "distance",
    "harmonic_average_speed",
    "median_speed",
    "average_speed",
    "standard_deviation_speed",
    "travel_time_standard_deviation",
    "sample_size",
    "average_travel_time",
    "spd_p_50",
    "spd_p_55",
    "spd_p_60",
    "spd_p_65",
    "spd_p_70",
    "spd_p_75",
    "spd_p_80",
    "spd_p_85",
    "spd_p_90",
    "spd_p_95",
]

EXCEL_MAX_ROWS_PER_SHEET = 1_048_575  # sheet limit of 1,048,576 minus the header row

# filename stem of each road's segment csvs in the exports directory
ROADS = ["whitemud-dr", "calgary-trail", "23-ave"]


def combine_road_csvs(road: str, exports_dir: Path) -> pd.DataFrame:
    """
    Vertically concatenates the road's template-copy segment csvs (the
    "-updated-" files, which together cover the full date span). The original
    single-day study is excluded: its day is already inside the first copy.
    """
    csv_paths = sorted(glob.glob(str(exports_dir / f"{road}-updated-*_segment.csv")))
    if not csv_paths:
        raise Exception(f"No segment csvs found for road {road!r} in {exports_dir}")

    frames = [pd.read_csv(path, usecols=EXPORT_COLUMNS) for path in csv_paths]
    combined = pd.concat(frames, ignore_index=True)
    return combined[EXPORT_COLUMNS]


def write_excel(df: pd.DataFrame, save_path: Path) -> None:
    """
    Writes the dataframe to xlsx, splitting across sheets when it exceeds
    Excel's per-sheet row limit.
    """
    with pd.ExcelWriter(save_path, engine="xlsxwriter") as writer:
        for sheet_num, start in enumerate(range(0, len(df), EXCEL_MAX_ROWS_PER_SHEET), 1):
            chunk = df.iloc[start : start + EXCEL_MAX_ROWS_PER_SHEET]
            chunk.to_excel(writer, sheet_name=f"data_{sheet_num}", index=False)


def main() -> None:
    exports_dir = Path("exports")
    save_dir = exports_dir / "combined"
    save_dir.mkdir(parents=True, exist_ok=True)

    for road in ROADS:
        combined = combine_road_csvs(road, exports_dir)
        save_path = save_dir / f"{road}_segments.xlsx"
        write_excel(combined, save_path)
        print(
            f"{road}: {len(combined):,} rows, "
            f"{combined['date_range_name'].nunique()} days, "
            f"{combined['segment_id'].nunique()} segments -> {save_path}"
        )


if __name__ == "__main__":
    main()
