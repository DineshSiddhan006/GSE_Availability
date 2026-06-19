import streamlit as st
import pandas as pd
import pickle
import warnings

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GSE Availability Prediction System",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    html, body, [data-testid="stApp"] {
        background-color: #0b1a2e;
        color: #e8edf5;
        font-family: 'Segoe UI', 'Inter', sans-serif;
    }

    [data-testid="stSidebar"]        { display: none; }
    [data-testid="collapsedControl"] { display: none; }

    /* ── Header ─────────────────────────────────────────────────── */
    .gse-header {
        background: linear-gradient(135deg, #0d2044 0%, #112d5c 60%, #1a3a6b 100%);
        border-bottom: 2px solid #2c78d4;
        padding: 26px 40px 20px 40px;
        border-radius: 0 0 12px 12px;
        margin-bottom: 26px;
    }
    .gse-header h1 {
        font-size: 1.65rem;
        font-weight: 700;
        color: #ffffff;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        margin: 0 0 4px 0;
    }
    .gse-header .subtitle {
        font-size: 0.82rem;
        color: #7fb3e8;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    /* ── Section label ───────────────────────────────────────────── */
    .section-title {
        font-size: 0.70rem;
        font-weight: 700;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: #4ea0e0;
        border-left: 3px solid #2c78d4;
        padding-left: 10px;
        margin-bottom: 16px;
        margin-top: 4px;
    }

    /* ── Widget label overrides ──────────────────────────────────── */
    label, [data-testid="stSelectbox"] label,
    [data-testid="stSlider"] label,
    [data-testid="stNumberInput"] label,
    [data-testid="stRadio"] label {
        color: #a8c4e0 !important;
        font-size: 0.81rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.03em;
    }

    div[data-baseweb="select"] > div {
        background-color: #0d2044 !important;
        border-color: #1e3a5f !important;
        color: #e8edf5 !important;
    }
    div[data-baseweb="input"] input,
    [data-testid="stNumberInput"] input {
        background-color: #0d2044 !important;
        border-color: #1e3a5f !important;
        color: #e8edf5 !important;
    }

    /* ── Divider ─────────────────────────────────────────────────── */
    hr {
        border: none;
        border-top: 1px solid #1e3a5f;
        margin: 20px 0;
    }

    /* ── Submit button ───────────────────────────────────────────── */
    [data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(90deg, #1a5bbf, #2c78d4) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 0.90rem !important;
        letter-spacing: 0.10em !important;
        text-transform: uppercase !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 14px 0 !important;
        width: 100% !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stFormSubmitButton"] > button:hover {
        background: linear-gradient(90deg, #2166cc, #3d8be0) !important;
        box-shadow: 0 0 18px rgba(44,120,212,0.45) !important;
    }

    /* ── Result cards ────────────────────────────────────────────── */
    .result-available {
        background: linear-gradient(135deg, #0a2e1a 0%, #0d3d22 100%);
        border: 2px solid #1e8c4a;
        border-radius: 14px;
        padding: 40px 40px;
        text-align: center;
        box-shadow: 0 0 40px rgba(30,140,74,0.30);
        margin: 28px 0;
    }
    .result-available .result-text {
        font-size: 1.7rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }

    .result-shortage {
        background: linear-gradient(135deg, #2e0a0a 0%, #3d1010 100%);
        border: 2px solid #c0392b;
        border-radius: 14px;
        padding: 40px 40px;
        text-align: center;
        box-shadow: 0 0 40px rgba(192,57,43,0.35);
        margin: 28px 0;
    }
    .result-shortage .result-text {
        font-size: 1.7rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }

    [data-testid="stAlert"] { border-radius: 8px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="gse-header">
        <h1>Ground Support Equipment Availability Prediction System</h1>
        <div class="subtitle">Airport Ramp &amp; Ground Handling Operations — Decision Support Tool</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# FEATURE COLUMN ORDER  (matches model training exactly)
# OHE applied to aircraft_type and terminal_zone; no timestamp; no scaling
# ─────────────────────────────────────────────────────────────────────────────
FEATURE_COLUMNS = [
    "arrival_delay_mins",
    "required_pushback_tugs",
    "required_belt_loaders",
    "required_gpus",
    "concurrent_arrivals_30min",
    "total_zone_baggage_volume",
    "avail_tugs_zone",
    "avail_loaders_zone",
    "avail_gpus_zone",
    "avg_battery_soc_zone",
    "fleet_utilization_ratio",
    "gse_operator_on_duty_count",
    "active_fault_code_count_zone",
    "ambient_temperature_c",
    "precipitation_intensity",
    "wind_speed_knots",
    "aircraft_type_Narrowbody",
    "aircraft_type_Widebody",
    "terminal_zone_Terminal_A",
    "terminal_zone_Terminal_B",
    "terminal_zone_Terminal_C",
]

# ─────────────────────────────────────────────────────────────────────────────
# MODEL LOADING
# ─────────────────────────────────────────────────────────────────────────────
MODEL_PATH = "gse_traditional_model.pkl"


@st.cache_resource(show_spinner="Loading prediction model...")
def load_model(path: str):
    with open(path, "rb") as f:
        pkg = pickle.load(f)
    if isinstance(pkg, dict):
        return pkg["model"]
    return pkg


try:
    voting_ensemble = load_model(MODEL_PATH)
except FileNotFoundError:
    st.error(
        f"Model file not found: '{MODEL_PATH}'. "
        "Place gse_traditional_model.pkl in the same directory as app.py and restart."
    )
    st.stop()
except Exception as exc:
    st.error(f"Failed to load model: {exc}")
    st.stop()


# ─────────────────────────────────────────────────────────────────────────────
# FEATURE BUILDER
# Applies the same transformation used at training time:
#   - aircraft_type  → one-hot (Narrowbody / Widebody)
#   - terminal_zone  → one-hot (Terminal_A / Terminal_B / Terminal_C)
#   - actual_arrival_timestamp is NOT passed (model does not use it)
#   - No scaling, no manual label encoding
# ─────────────────────────────────────────────────────────────────────────────
def build_input_df(
    aircraft_type: str,
    terminal_zone: str,
    arrival_delay_mins: int,
    concurrent_arrivals_30min: int,
    required_pushback_tugs: int,
    required_belt_loaders: int,
    required_gpus: int,
    avail_tugs_zone: int,
    avail_loaders_zone: int,
    avail_gpus_zone: int,
    gse_operator_on_duty_count: int,
    active_fault_code_count_zone: int,
    precipitation_intensity: float,
    wind_speed_knots: float,
    fleet_utilization_ratio: float,
    avg_battery_soc_zone: float,
    total_zone_baggage_volume: int,
    ambient_temperature_c: float,
) -> pd.DataFrame:
    row = {
        "arrival_delay_mins":           int(arrival_delay_mins),
        "required_pushback_tugs":       int(required_pushback_tugs),
        "required_belt_loaders":        int(required_belt_loaders),
        "required_gpus":                int(required_gpus),
        "concurrent_arrivals_30min":    int(concurrent_arrivals_30min),
        "total_zone_baggage_volume":    int(total_zone_baggage_volume),
        "avail_tugs_zone":              int(avail_tugs_zone),
        "avail_loaders_zone":           int(avail_loaders_zone),
        "avail_gpus_zone":              int(avail_gpus_zone),
        "avg_battery_soc_zone":         float(avg_battery_soc_zone),
        "fleet_utilization_ratio":      float(fleet_utilization_ratio),
        "gse_operator_on_duty_count":   int(gse_operator_on_duty_count),
        "active_fault_code_count_zone": int(active_fault_code_count_zone),
        "ambient_temperature_c":        float(ambient_temperature_c),
        "precipitation_intensity":      float(precipitation_intensity),
        "wind_speed_knots":             float(wind_speed_knots),
        # One-hot: aircraft_type
        "aircraft_type_Narrowbody":     int(aircraft_type == "Narrowbody"),
        "aircraft_type_Widebody":       int(aircraft_type == "Widebody"),
        # One-hot: terminal_zone
        "terminal_zone_Terminal_A":     int(terminal_zone == "Terminal_A"),
        "terminal_zone_Terminal_B":     int(terminal_zone == "Terminal_B"),
        "terminal_zone_Terminal_C":     int(terminal_zone == "Terminal_C"),
    }
    return pd.DataFrame([row], columns=FEATURE_COLUMNS)


# ─────────────────────────────────────────────────────────────────────────────
# INPUT FORM  —  18 features in 6 rows x 3 columns
#
# Row 1  | Aircraft Type          | Terminal Zone          | Arrival Delay (mins)
# Row 2  | Concurrent Arrivals    | Required Pushback Tugs | Required Belt Loaders
# Row 3  | Required GPUs          | Avail Tugs Zone        | Avail Loaders Zone
# Row 4  | Avail GPUs Zone        | GSE Operators On Duty  | Active Fault Code Count
# Row 5  | Precipitation Intensity| Wind Speed (knots)     | Ambient Temperature
# Row 6  | Fleet Utilization Ratio| Battery SOC (%)        | Total Baggage Volume
# ─────────────────────────────────────────────────────────────────────────────
with st.form("gse_prediction_form"):

    # ── Section 1: Flight Information ────────────────────────────────────────
    st.markdown('<div class="section-title">Flight Information</div>', unsafe_allow_html=True)

    # Row 1
    r1c1, r1c2, r1c3 = st.columns(3)
    with r1c1:
        aircraft_type = st.selectbox(
            "Aircraft Type",
            options=["Narrowbody", "Widebody"],
            index=0,
        )
    with r1c2:
        terminal_zone = st.selectbox(
            "Terminal Zone",
            options=["Terminal_A", "Terminal_B", "Terminal_C"],
            index=0,
        )
    with r1c3:
        arrival_delay_mins = st.slider(
            "Arrival Delay (minutes)",
            min_value=-15,
            max_value=180,
            value=30,
            step=1,
        )

    # Row 2
    r2c1, r2c2, r2c3 = st.columns(3)
    with r2c1:
        concurrent_arrivals_30min = st.slider(
            "Concurrent Arrivals — 30 Min Window",
            min_value=0,
            max_value=11,
            value=4,
            step=1,
        )
    with r2c2:
        required_pushback_tugs = st.radio(
            "Required Pushback Tugs",
            options=[1, 2],
            index=0,
            horizontal=True,
        )
    with r2c3:
        required_belt_loaders = st.radio(
            "Required Belt Loaders",
            options=[1, 2, 3, 4],
            index=1,
            horizontal=True,
        )

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Section 2: GSE Requirements & Available Equipment ────────────────────
    st.markdown('<div class="section-title">GSE Requirements &amp; Available Equipment</div>', unsafe_allow_html=True)

    # Row 3
    r3c1, r3c2, r3c3 = st.columns(3)
    with r3c1:
        required_gpus = st.radio(
            "Required GPUs (Ground Power Units)",
            options=[1, 2],
            index=0,
            horizontal=True,
        )
    with r3c2:
        avail_tugs_zone = st.number_input(
            "Available Tugs in Zone",
            min_value=2,
            max_value=25,
            value=12,
            step=1,
        )
    with r3c3:
        avail_loaders_zone = st.number_input(
            "Available Belt Loaders in Zone",
            min_value=3,
            max_value=30,
            value=16,
            step=1,
        )

    # Row 4
    r4c1, r4c2, r4c3 = st.columns(3)
    with r4c1:
        avail_gpus_zone = st.number_input(
            "Available GPUs in Zone",
            min_value=2,
            max_value=20,
            value=10,
            step=1,
        )
    with r4c2:
        gse_operator_on_duty_count = st.number_input(
            "GSE Operators On Duty",
            min_value=6,
            max_value=37,
            value=18,
            step=1,
        )
    with r4c3:
        active_fault_code_count_zone = st.slider(
            "Active Fault Code Count — Zone",
            min_value=0,
            max_value=12,
            value=6,
            step=1,
        )

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Section 3: Operational Conditions ────────────────────────────────────
    st.markdown('<div class="section-title">Operational Conditions</div>', unsafe_allow_html=True)

    # Row 5
    r5c1, r5c2, r5c3 = st.columns(3)
    with r5c1:
        precipitation_intensity = st.slider(
            "Precipitation Intensity (mm/hr)",
            min_value=0.0,
            max_value=30.0,
            value=3.0,
            step=0.5,
        )
    with r5c2:
        wind_speed_knots = st.slider(
            "Wind Speed (knots)",
            min_value=0.0,
            max_value=50.0,
            value=25.0,
            step=0.5,
        )
    with r5c3:
        ambient_temperature_c = st.slider(
            "Ambient Temperature (C)",
            min_value=-10.0,
            max_value=48.0,
            value=19.0,
            step=0.5,
        )

    # Row 6
    r6c1, r6c2, r6c3 = st.columns(3)
    with r6c1:
        fleet_utilization_ratio = st.slider(
            "Fleet Utilization Ratio",
            min_value=0.05,
            max_value=0.90,
            value=0.43,
            step=0.01,
        )
    with r6c2:
        avg_battery_soc_zone = st.slider(
            "Average Battery State-of-Charge (%)",
            min_value=2.0,
            max_value=100.0,
            value=62.0,
            step=0.5,
        )
    with r6c3:
        total_zone_baggage_volume = st.number_input(
            "Total Zone Baggage Volume (bags)",
            min_value=50,
            max_value=2500,
            value=924,
            step=10,
        )

    st.markdown("<hr>", unsafe_allow_html=True)

    predict_btn = st.form_submit_button(
        "CHECK EQUIPMENT AVAILABILITY",
        use_container_width=True,
        type="primary",
    )


# ─────────────────────────────────────────────────────────────────────────────
# PREDICTION
# ─────────────────────────────────────────────────────────────────────────────
if predict_btn:

    try:
        input_df = build_input_df(
            aircraft_type=aircraft_type,
            terminal_zone=terminal_zone,
            arrival_delay_mins=arrival_delay_mins,
            concurrent_arrivals_30min=concurrent_arrivals_30min,
            required_pushback_tugs=required_pushback_tugs,
            required_belt_loaders=required_belt_loaders,
            required_gpus=required_gpus,
            avail_tugs_zone=avail_tugs_zone,
            avail_loaders_zone=avail_loaders_zone,
            avail_gpus_zone=avail_gpus_zone,
            gse_operator_on_duty_count=gse_operator_on_duty_count,
            active_fault_code_count_zone=active_fault_code_count_zone,
            precipitation_intensity=precipitation_intensity,
            wind_speed_knots=wind_speed_knots,
            fleet_utilization_ratio=fleet_utilization_ratio,
            avg_battery_soc_zone=avg_battery_soc_zone,
            total_zone_baggage_volume=total_zone_baggage_volume,
            ambient_temperature_c=ambient_temperature_c,
        )
    except Exception as exc:
        st.error(f"Input preparation error: {exc}")
        st.stop()

    try:
        prediction = int(voting_ensemble.predict(input_df)[0])
    except Exception as exc:
        st.error(f"Prediction failed: {exc}")
        st.stop()

    _, result_col, _ = st.columns([1, 3, 1])
    with result_col:
        if prediction == 0:
            st.markdown(
                '<div class="result-available">'
                '<div class="result-text">GSE Equipment Available</div>'
                "</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="result-shortage">'
                '<div class="result-text">GSE Equipment Not Available</div>'
                "</div>",
                unsafe_allow_html=True,
            )