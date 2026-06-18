import streamlit as st
import pandas as pd
import numpy as np
import pickle
import warnings

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GSE Availability Prediction System",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM CSS  —  Airport Ground Operations Control System theme
# Dark Navy Blue / White / Sky Blue / Grey palette
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* ── Global reset ──────────────────────────────────────────────── */
    html, body, [data-testid="stApp"] {
        background-color: #0b1a2e;
        color: #e8edf5;
        font-family: 'Segoe UI', 'Inter', sans-serif;
    }

    /* ── Hide sidebar toggle ──────────────────────────────────────── */
    [data-testid="stSidebar"]         { display: none; }
    [data-testid="collapsedControl"]  { display: none; }

    /* ── Header banner ────────────────────────────────────────────── */
    .gse-header {
        background: linear-gradient(135deg, #0d2044 0%, #112d5c 60%, #1a3a6b 100%);
        border-bottom: 2px solid #2c78d4;
        padding: 28px 40px 22px 40px;
        border-radius: 0 0 12px 12px;
        margin-bottom: 28px;
    }
    .gse-header h1 {
        font-size: 1.75rem;
        font-weight: 700;
        color: #ffffff;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        margin: 0 0 4px 0;
    }
    .gse-header .subtitle {
        font-size: 0.85rem;
        color: #7fb3e8;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }
    .status-badge {
        display: inline-block;
        background: #133a6a;
        border: 1px solid #2c78d4;
        border-radius: 20px;
        padding: 3px 14px;
        font-size: 0.75rem;
        color: #7fb3e8;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        margin-top: 8px;
    }

    /* ── Section cards ────────────────────────────────────────────── */
    .section-card {
        background: #0f2340;
        border: 1px solid #1e3a5f;
        border-radius: 10px;
        padding: 22px 26px;
        margin-bottom: 20px;
    }
    .section-title {
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: #4ea0e0;
        border-left: 3px solid #2c78d4;
        padding-left: 10px;
        margin-bottom: 18px;
    }

    /* ── Streamlit widget overrides ───────────────────────────────── */
    [data-testid="stSelectbox"] label,
    [data-testid="stSlider"] label,
    [data-testid="stNumberInput"] label,
    [data-testid="stRadio"] label,
    .stSlider label,
    label {
        color: #a8c4e0 !important;
        font-size: 0.82rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.03em;
    }

    div[data-baseweb="select"] > div {
        background-color: #0d2044 !important;
        border-color: #1e3a5f !important;
        color: #e8edf5 !important;
    }
    div[data-baseweb="input"] input {
        background-color: #0d2044 !important;
        border-color: #1e3a5f !important;
        color: #e8edf5 !important;
    }
    [data-testid="stNumberInput"] input {
        background-color: #0d2044 !important;
        color: #e8edf5 !important;
    }

    /* Slider track */
    [data-testid="stSlider"] [data-testid="stThumbValue"] {
        color: #4ea0e0;
    }

    /* ── Predict button ───────────────────────────────────────────── */
    [data-testid="stFormSubmitButton"] > button,
    .stButton > button {
        background: linear-gradient(90deg, #1a5bbf, #2c78d4) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 0.92rem !important;
        letter-spacing: 0.08em !important;
        text-transform: uppercase !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 14px 0 !important;
        width: 100% !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stFormSubmitButton"] > button:hover,
    .stButton > button:hover {
        background: linear-gradient(90deg, #2166cc, #3d8be0) !important;
        box-shadow: 0 0 18px rgba(44,120,212,0.45) !important;
    }

    /* ── Result cards ─────────────────────────────────────────────── */
    .result-available {
        background: linear-gradient(135deg, #0a2e1a 0%, #0d3d22 100%);
        border: 2px solid #1e8c4a;
        border-radius: 14px;
        padding: 36px 40px;
        text-align: center;
        box-shadow: 0 0 40px rgba(30,140,74,0.30);
        margin: 28px 0;
    }
    .result-available .result-label {
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: #52c47a;
        margin-bottom: 10px;
    }
    .result-available .result-text {
        font-size: 1.6rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }
    .result-available .result-icon {
        font-size: 2.8rem;
        margin-bottom: 12px;
        color: #1e8c4a;
    }

    .result-shortage {
        background: linear-gradient(135deg, #2e0a0a 0%, #3d1010 100%);
        border: 2px solid #c0392b;
        border-radius: 14px;
        padding: 36px 40px;
        text-align: center;
        box-shadow: 0 0 40px rgba(192,57,43,0.35);
        margin: 28px 0;
    }
    .result-shortage .result-label {
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: #e57373;
        margin-bottom: 10px;
    }
    .result-shortage .result-text {
        font-size: 1.6rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }
    .result-shortage .result-icon {
        font-size: 2.8rem;
        margin-bottom: 12px;
        color: #c0392b;
    }

    /* ── Divider ──────────────────────────────────────────────────── */
    hr {
        border: none;
        border-top: 1px solid #1e3a5f;
        margin: 24px 0;
    }

    /* ── Footer ───────────────────────────────────────────────────── */
    .gse-footer {
        text-align: center;
        font-size: 0.72rem;
        color: #3d5a7a;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        padding: 18px 0 8px 0;
    }

    /* ── Error / info overrides ───────────────────────────────────── */
    [data-testid="stAlert"] {
        border-radius: 8px;
    }
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
        <div class="status-badge">System Active</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# MODEL LOADING
# Expected feature order (OHE, no timestamp):
#   arrival_delay_mins, required_pushback_tugs, required_belt_loaders,
#   required_gpus, concurrent_arrivals_30min, total_zone_baggage_volume,
#   avail_tugs_zone, avail_loaders_zone, avail_gpus_zone,
#   avg_battery_soc_zone, fleet_utilization_ratio,
#   gse_operator_on_duty_count, active_fault_code_count_zone,
#   ambient_temperature_c, precipitation_intensity, wind_speed_knots,
#   aircraft_type_Narrowbody, aircraft_type_Widebody,
#   terminal_zone_Terminal_A, terminal_zone_Terminal_B,
#   terminal_zone_Terminal_C
# ─────────────────────────────────────────────────────────────────────────────
MODEL_PATH = "gse_traditional_model.pkl"

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
# HELPER — build feature dataframe from raw inputs
# ─────────────────────────────────────────────────────────────────────────────

def build_feature_dataframe(
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
    """
    Apply the same feature transformation used during training.
    Categorical columns are one-hot encoded.
    No scaling is applied.
    No label encoding is applied.
    Returns a single-row DataFrame with columns in FEATURE_COLUMNS order.
    """
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
    df = pd.DataFrame([row], columns=FEATURE_COLUMNS)
    return df


# ─────────────────────────────────────────────────────────────────────────────
# INPUT FORM
# ─────────────────────────────────────────────────────────────────────────────
with st.form("gse_prediction_form"):

    # ── Section 1: Flight Information ────────────────────────────────────────
    st.markdown('<div class="section-title">01 — Flight Information</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        aircraft_type = st.selectbox(
            "Aircraft Type",
            options=["Narrowbody", "Widebody"],
            index=0,
            help="Widebody aircraft require significantly more GSE resources.",
        )
    with col2:
        terminal_zone = st.selectbox(
            "Terminal Zone",
            options=["Terminal_A", "Terminal_B", "Terminal_C"],
            index=0,
            help="Terminal zone determines the local GSE asset sub-pool.",
        )

    col3, col4 = st.columns(2)
    with col3:
        arrival_delay_mins = st.slider(
            "Arrival Delay (minutes)",
            min_value=-15,
            max_value=180,
            value=30,
            step=1,
            help="Negative values indicate early arrival.",
        )
    with col4:
        concurrent_arrivals_30min = st.slider(
            "Concurrent Arrivals — 30-Minute Window",
            min_value=0,
            max_value=11,
            value=4,
            step=1,
            help="Number of aircraft arriving within a 30-minute window in the same zone.",
        )

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Section 2: GSE Requirement Information ───────────────────────────────
    st.markdown('<div class="section-title">02 — GSE Requirement Information</div>', unsafe_allow_html=True)

    col5, col6, col7 = st.columns(3)
    with col5:
        required_pushback_tugs = st.radio(
            "Required Pushback Tugs",
            options=[1, 2],
            index=0,
            horizontal=True,
        )
    with col6:
        required_belt_loaders = st.radio(
            "Required Belt Loaders",
            options=[1, 2, 3, 4],
            index=1,
            horizontal=True,
        )
    with col7:
        required_gpus = st.radio(
            "Required GPUs (Ground Power Units)",
            options=[1, 2],
            index=0,
            horizontal=True,
        )

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Section 3: Available Equipment Information ───────────────────────────
    st.markdown('<div class="section-title">03 — Available Equipment Information</div>', unsafe_allow_html=True)

    col8, col9, col10 = st.columns(3)
    with col8:
        avail_tugs_zone = st.number_input(
            "Available Tugs in Zone",
            min_value=2,
            max_value=25,
            value=12,
            step=1,
        )
    with col9:
        avail_loaders_zone = st.number_input(
            "Available Belt Loaders in Zone",
            min_value=3,
            max_value=30,
            value=16,
            step=1,
        )
    with col10:
        avail_gpus_zone = st.number_input(
            "Available GPUs in Zone",
            min_value=2,
            max_value=20,
            value=10,
            step=1,
        )

    col11, col12 = st.columns(2)
    with col11:
        avg_battery_soc_zone = st.slider(
            "Average Battery State-of-Charge — Zone (%)",
            min_value=2.0,
            max_value=100.0,
            value=62.0,
            step=0.5,
            help="Average SOC across all electric GSE assets in the zone.",
        )
    with col12:
        fleet_utilization_ratio = st.slider(
            "Fleet Utilization Ratio",
            min_value=0.05,
            max_value=0.90,
            value=0.43,
            step=0.01,
            help="Ratio of fleet actively engaged in operations. 1.0 = 100% utilization.",
        )

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Section 4: Operational Condition Information ──────────────────────────
    st.markdown('<div class="section-title">04 — Operational Condition Information</div>', unsafe_allow_html=True)

    col13, col14 = st.columns(2)
    with col13:
        gse_operator_on_duty_count = st.number_input(
            "GSE Operators On Duty",
            min_value=6,
            max_value=37,
            value=18,
            step=1,
        )
    with col14:
        active_fault_code_count_zone = st.slider(
            "Active Fault Code Count — Zone",
            min_value=0,
            max_value=12,
            value=6,
            step=1,
            help="Number of active telematics warning flags across zone equipment.",
        )

    col15, col16, col17 = st.columns(3)
    with col15:
        precipitation_intensity = st.slider(
            "Precipitation Intensity (mm/hr)",
            min_value=0.0,
            max_value=30.0,
            value=3.0,
            step=0.5,
        )
    with col16:
        wind_speed_knots = st.slider(
            "Wind Speed (knots)",
            min_value=0.0,
            max_value=50.0,
            value=25.0,
            step=0.5,
            help="Wind speeds above 30 knots restrict high-lift loader extension.",
        )
    with col17:
        ambient_temperature_c = st.slider(
            "Ambient Temperature (C)",
            min_value=-10.0,
            max_value=48.0,
            value=19.0,
            step=0.5,
            help="Temperatures above 40 C degrade battery and hydraulic performance.",
        )

    col18, _ = st.columns([1, 1])
    with col18:
        total_zone_baggage_volume = st.number_input(
            "Total Zone Baggage Volume (bags)",
            min_value=50,
            max_value=2500,
            value=924,
            step=10,
            help="Total number of bags scheduled for the zone in the current shift.",
        )

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Submit button ─────────────────────────────────────────────────────────
    predict_btn = st.form_submit_button(
        "CHECK EQUIPMENT AVAILABILITY",
        use_container_width=True,
        type="primary",
    )


# ─────────────────────────────────────────────────────────────────────────────
# PREDICTION  —  triggered only when the button is clicked
# ─────────────────────────────────────────────────────────────────────────────
if predict_btn:

    # Input validation
    validation_errors = []
    if avail_tugs_zone < 0:
        validation_errors.append("Available Tugs in Zone must be zero or greater.")
    if avail_loaders_zone < 0:
        validation_errors.append("Available Belt Loaders must be zero or greater.")
    if avail_gpus_zone < 0:
        validation_errors.append("Available GPUs must be zero or greater.")

    if validation_errors:
        for err in validation_errors:
            st.error(err)
        st.stop()

    # Build feature dataframe with the same transformations applied at training time
    try:
        input_df = build_feature_dataframe(
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

    # Run model inference
    try:
        prediction = int(voting_ensemble.predict(input_df)[0])
    except Exception as exc:
        st.error(f"Prediction failed: {exc}")
        st.stop()

    # ── Display result card ───────────────────────────────────────────────────
    _, result_col, _ = st.columns([1, 3, 1])
    with result_col:
        if prediction == 0:
            st.markdown(
                """
                <div class="result-available">
                    <div class="result-label">Equipment Status</div>
                    <div class="result-text">GSE Equipment Available</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div class="result-shortage">
                    <div class="result-label">Equipment Status</div>
                    <div class="result-text">GSE Equipment Not Available</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="gse-footer">
        Ground Support Equipment Availability Prediction System
        &nbsp;|&nbsp;
        Soft Voting Ensemble: CatBoost &middot; LightGBM &middot; XGBoost &middot; ExtraTrees
        &nbsp;|&nbsp;
        Airport Ramp Operations Decision Support
    </div>
    """,
    unsafe_allow_html=True,
)