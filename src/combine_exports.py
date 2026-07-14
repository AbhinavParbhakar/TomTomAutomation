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


def main() -> None:
    exports_dir = Path("exports")
    save_dir = exports_dir / "combined"
    save_dir.mkdir(parents=True, exist_ok=True)

    all_roads_path = save_dir / "all-roads_segments.csv"
    total_rows = 0

    for road_num, road in enumerate(ROADS):
        combined = combine_road_csvs(road, exports_dir)
        save_path = save_dir / f"{road}_segments.csv"
        combined.to_csv(save_path, index=False)
        # first road starts the all-roads file, the rest append without header
        combined.to_csv(
            all_roads_path,
            mode="w" if road_num == 0 else "a",
            header=road_num == 0,
            index=False,
        )
        total_rows += len(combined)
        print(
            f"{road}: {len(combined):,} rows, "
            f"{combined['date_range_name'].nunique()} days, "
            f"{combined['segment_id'].nunique()} segments -> {save_path}"
        )

    print(f"all roads: {total_rows:,} rows -> {all_roads_path}")


if __name__ == "__main__":
    main()
