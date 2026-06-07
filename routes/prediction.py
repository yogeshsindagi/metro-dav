from fastapi import APIRouter, HTTPException, Query
import joblib
import pandas as pd
import numpy as np
import os
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

router = APIRouter(prefix="/api/authority", tags=["Metro Authority"])

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "passenger_prediction.joblib")
STATION_NAME_CSV = os.path.join(BASE_DIR, "station_name.csv")
STATION_DATA_XLSX = os.path.join(BASE_DIR, "station_data.xlsx")

# ── Load ML model ─────────────────────────────────────────────────────────────
loaded_model = joblib.load(MODEL_PATH)
FEATURE_COLUMNS = loaded_model.feature_names_in_.tolist()

# ── Load station names (handles commas inside station names) ───────────────────
station_names = {}
with open(STATION_NAME_CSV, "r", encoding="utf-8") as f:
    header = f.readline()  # skip header
    for line in f:
        line = line.strip()
        if not line:
            continue
        parts = line.split(",", 1)  # split only on first comma
        if len(parts) == 2:
            station_names[parts[0].strip()] = parts[1].strip()

# ── Load historical station data (for rolling features) ───────────────────────
df_clean = pd.DataFrame(columns=["STATION", "BUSINESS DATE", "total_passengers"])
try:
    import openpyxl
    wb = openpyxl.load_workbook(STATION_DATA_XLSX, read_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    wb.close()

    if len(rows) > 1:
        header = rows[0]
        df_raw = pd.DataFrame(rows[1:], columns=header)

        # Destination station columns start at index 2
        dest_cols = [c for c in header[2:] if c is not None]

        # Compute total_passengers = sum of all destination columns
        df_raw[dest_cols] = df_raw[dest_cols].apply(pd.to_numeric, errors="coerce").fillna(0)
        df_raw["total_passengers"] = df_raw[dest_cols].sum(axis=1)

        # Parse date and hour from "2025-08-01-04Hrs-5hrs" format
        def parse_business_date(val):
            """Extract (date, hour) from e.g. '2025-08-01-04Hrs-5hrs'."""
            try:
                parts = str(val).split("-")
                date_str = "-".join(parts[:3])        # '2025-08-01'
                hour = int(parts[3].replace("Hrs", ""))  # 4
                return pd.to_datetime(date_str), hour
            except Exception:
                return pd.NaT, 0

        parsed = df_raw["BUSINESS DATE"].apply(parse_business_date)
        df_raw["BUSINESS DATE"] = parsed.apply(lambda x: x[0])
        df_raw["hour"] = parsed.apply(lambda x: x[1])

        # Keep only what we need
        df_clean = df_raw[["STATION", "BUSINESS DATE", "hour", "total_passengers"]].copy()
        df_clean = df_clean.dropna(subset=["STATION"])
        print(f"[prediction] OK: Loaded station_data.xlsx - {len(df_clean)} rows, {df_clean['STATION'].nunique()} stations")
except Exception as e:
    print(f"[prediction] WARN: Could not load station_data.xlsx ({e}) - rolling features will default to 0")


# ── Core prediction function ──────────────────────────────────────────────────
def create_test_row_with_time(station_code: str, date_str: str, hour: int) -> pd.DataFrame:
    """Build a single-row DataFrame matching the model's training schema."""
    date = pd.to_datetime(date_str)

    # Temporal features
    day_of_week = date.dayofweek
    day_of_month = date.day
    month = date.month
    quarter = date.quarter
    is_weekend = int(day_of_week in [5, 6])
    is_peak_morning = int(hour in range(7, 11))   # 7-10 AM
    is_peak_evening = int(hour in range(17, 21))   # 5-8 PM
    is_peak_any = max(is_peak_morning, is_peak_evening)

    # Rolling features from historical data
    station_data = df_clean[df_clean["STATION"] == station_code].sort_values("BUSINESS DATE")
    last_counts = station_data["total_passengers"].values if "total_passengers" in df_clean.columns else np.array([])

    rolling_1h = float(last_counts[-1]) if len(last_counts) >= 1 else 0.0
    rolling_3h = float(last_counts[-3:].mean()) if len(last_counts) >= 3 else rolling_1h
    rolling_6h = float(last_counts[-6:].mean()) if len(last_counts) >= 6 else rolling_1h

    # Base numeric features
    sample_row = pd.DataFrame({
        "hour": [hour],
        "day_of_week": [day_of_week],
        "day_of_month": [day_of_month],
        "month": [month],
        "quarter": [quarter],
        "is_weekend": [is_weekend],
        "is_peak_morning": [is_peak_morning],
        "is_peak_evening": [is_peak_evening],
        "is_peak_any": [is_peak_any],
        "rolling_1h": [rolling_1h],
        "rolling_3h": [rolling_3h],
        "rolling_6h": [rolling_6h],
    })

    # One-hot encode station
    station_col = f"station_{station_code}"
    if station_col in FEATURE_COLUMNS:
        sample_row[station_col] = 1

    # Fill remaining station columns with 0
    for col in FEATURE_COLUMNS:
        if col not in sample_row.columns:
            sample_row[col] = 0

    # Reorder to match training
    sample_row = sample_row[FEATURE_COLUMNS]
    return sample_row


def _predict(station_code: str, date_str: str, hour: int) -> dict:
    """Run prediction and return a result dict."""
    row = create_test_row_with_time(station_code, date_str, hour)
    predicted_log = loaded_model.predict(row)
    predicted_passengers = int(np.expm1(predicted_log)[0])
    return {
        "station_code": station_code,
        "station_name": station_names.get(station_code, station_code),
        "date": date_str,
        "hour": hour,
        "predicted_passengers": max(predicted_passengers, 0),
    }


# ── GET all station codes + names ─────────────────────────────────────────────
@router.get("/stations")
def get_station_list():
    """Return every station the model knows about, with its human-readable name."""
    model_stations = [c.replace("station_", "") for c in FEATURE_COLUMNS if c.startswith("station_")]
    return [
        {"code": code, "name": station_names.get(code, code)}
        for code in sorted(model_stations)
    ]


# ── Single prediction ─────────────────────────────────────────────────────────
@router.get("/predict")
def predict_single(
    station_code: str = Query(..., description="Station code, e.g. AGPP"),
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    hour: int = Query(..., ge=0, le=23, description="Hour of day (0-23)"),
):
    """Predict passenger count for one station at a given date & hour."""
    # Validate station
    if f"station_{station_code}" not in FEATURE_COLUMNS:
        raise HTTPException(status_code=404, detail=f"Unknown station code: {station_code}")
    try:
        return _predict(station_code, date, hour)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Bulk: predict for ALL stations at a given date & hour ──────────────────────
@router.get("/predict/bulk")
def predict_bulk(
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    hour: int = Query(..., ge=0, le=23, description="Hour of day (0-23)"),
):
    """Predict passenger count for every station at a given date & hour."""
    model_stations = [c.replace("station_", "") for c in FEATURE_COLUMNS if c.startswith("station_")]
    results = []
    for code in model_stations:
        try:
            results.append(_predict(code, date, hour))
        except Exception:
            continue
    # Sort by predicted passengers descending
    results.sort(key=lambda r: r["predicted_passengers"], reverse=True)
    return results


# ── Hourly: predict all 24 hours for one station on a date ────────────────────
@router.get("/predict/hourly")
def predict_hourly(
    station_code: str = Query(..., description="Station code, e.g. AGPP"),
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
):
    """Predict passenger count for every hour (0-23) at a station on a date."""
    valid_stations = [c.replace("station_", "") for c in FEATURE_COLUMNS if c.startswith("station_")]
    if station_code not in valid_stations:
        raise HTTPException(status_code=404, detail=f"Unknown station code: {station_code}")
    results = []
    for h in range(24):
        try:
            results.append(_predict(station_code, date, h))
        except Exception:
            continue
    return results
