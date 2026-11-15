
from pathlib import Path
from itertools import combinations
import math

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Schmitt Trigger PUF | Paper Replication",
    page_icon="🔐",
    layout="wide"
)

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"


# ============================================================
# CUSTOM STYLING
# ============================================================

st.markdown("""
<style>
.main-title {
    font-size: 34px;
    font-weight: 750;
    margin-bottom: 0;
}
.subtitle {
    color: #777777;
    font-size: 15px;
    margin-bottom: 20px;
}
.metric-card {
    padding: 15px;
    border-radius: 10px;
    border: 1px solid rgba(128,128,128,0.3);
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# DATA LOADING
# ============================================================

@st.cache_data
def load_csv(filename):
    path = RESULTS / filename

    if not path.exists():
        return pd.DataFrame()

    try:
        return pd.read_csv(path, low_memory=False)
    except Exception as error:
        st.error(f"Could not read {filename}: {error}")
        return pd.DataFrame()


def safe_dataframe(df, height=350):
    """
    Convert all displayed values to strings.
    Prevents Arrow conversion errors with very large integers.
    Original data is not changed.
    """
    if df is None or df.empty:
        st.info("No data available.")
        return

    display_df = df.copy().astype(str)

    st.dataframe(
        display_df,
        use_container_width=True,
        height=height,
        hide_index=True
    )


def get_numeric_columns(df):
    """
    Safely identify numeric columns, including columns
    that pandas may have loaded as strings.
    """
    result = {}

    for column in df.columns:
        values = pd.to_numeric(df[column], errors="coerce")

        if values.notna().sum() > 0:
            result[column] = values

    return result


# ============================================================
# METRIC CALCULATIONS
# ============================================================

def calculate_full_crp_metrics(df):
    """
    Calculates:
    - Uniformity
    - Randomness
    - Uniqueness

    Expected CSV columns:
    crp_id, device_id, response_bits
    """

    required = {"crp_id", "device_id", "response_bits"}

    if not required.issubset(df.columns):
        return None

    work = df[["crp_id", "device_id", "response_bits"]].copy()

    work["response_bits"] = (
        work["response_bits"].astype(str).str.strip()
    )

    # Keep valid 128-bit binary responses.
    valid = work[
        work["response_bits"].str.fullmatch(r"[01]{128}", na=False)
    ].copy()

    if valid.empty:
        return None

    all_bits = "".join(valid["response_bits"].tolist())

    ones = all_bits.count("1")
    total_bits = len(all_bits)

    p = ones / total_bits if total_bits else 0.0

    uniformity = p * 100

    if p == 0 or p == 1:
        randomness = 0.0
    else:
        randomness = -100 * math.log2(max(p, 1 - p))

    # Calculate mean pairwise inter-device Hamming distance.
    distances = []

    for crp_id, group in valid.groupby("crp_id"):
        responses = group["response_bits"].tolist()

        if len(responses) < 2:
            continue

        for response_a, response_b in combinations(responses, 2):
            distance = sum(
                bit_a != bit_b
                for bit_a, bit_b in zip(response_a, response_b)
            )

            distances.append(distance / 128 * 100)

    uniqueness = (
        sum(distances) / len(distances)
        if distances else float("nan")
    )

    return {
        "valid_rows": len(valid),
        "unique_crps": valid["crp_id"].nunique(),
        "devices": valid["device_id"].nunique(),
        "total_bits": total_bits,
        "uniformity": uniformity,
        "randomness": randomness,
        "uniqueness": uniqueness
    }


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<p class="main-title">🔐 Schmitt-Trigger PUF</p>',
    unsafe_allow_html=True
)

st.markdown(
    '<p class="subtitle">'
    'Software-Based Paper Replication and Experimental Results Dashboard'
    '</p>',
    unsafe_allow_html=True
)


# ============================================================
# LOAD MAIN DATA
# ============================================================

full_crp = load_csv("full_crp_responses.csv")
challenges = load_csv("temperature_challenges.csv")
periods = load_csv("oscillator_periods.csv")

metrics = calculate_full_crp_metrics(full_crp)


# ============================================================
# TOP-LEVEL METRICS
# ============================================================

st.header("Project Overview")

if metrics:

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Challenge-response pairs",
        f'{metrics["unique_crps"]:,}'
    )

    c2.metric(
        "Virtual devices",
        f'{metrics["devices"]:,}'
    )

    c3.metric(
        "Response bits",
        "128"
    )

    c4.metric(
        "Total valid response bits",
        f'{metrics["total_bits"]:,}'
    )

    st.subheader("Main PUF Performance Metrics")

    a, b, c = st.columns(3)

    a.metric(
        "Uniqueness",
        f'{metrics["uniqueness"]:.4f}%'
    )

    b.metric(
        "Uniformity",
        f'{metrics["uniformity"]:.4f}%'
    )

    c.metric(
        "Randomness",
        f'{metrics["randomness"]:.4f}%'
    )

else:
    st.error(
        "Could not calculate main metrics. "
        "Check results/full_crp_responses.csv."
    )


# ============================================================
# NAVIGATION TABS
# ============================================================

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Overview",
    "CRP Explorer",
    "Oscillator Analysis",
    "Experiments",
    "Paper Comparison",
    "CSV Results"
])


# ============================================================
# TAB 1: OVERVIEW
# ============================================================

with tab1:

    st.header("Experimental Overview")

    st.markdown("""
    This project models a Schmitt-trigger-based Physical
    Unclonable Function (PUF).

    The software replication includes:

    - Five virtual devices
    - Thirty virtual oscillator pins per device
    - 10,000 challenge sequences
    - 128 response bits per challenge
    - RC oscillator period modelling
    - Pairwise response generation
    - Uniqueness and uniformity analysis
    - Randomness and entropy analysis
    - Temperature reliability experiments
    - Steadiness and averaging experiments
    - Error probability analysis
    """)

    st.subheader("Project Configuration")

    config = pd.DataFrame({
        "Parameter": [
            "Virtual devices",
            "Virtual pins per device",
            "Challenge-response pairs",
            "Response bits",
            "Resistance",
            "Capacitance",
            "Supply voltage",
            "Counter clock",
            "Reference temperature",
            "Model type"
        ],
        "Value": [
            "5",
            "30",
            "10,000",
            "128",
            "22 kΩ",
            "1 nF",
            "3.3 V",
            "100 MHz",
            "25 °C",
            "Synthetic software model"
        ]
    })

    safe_dataframe(config)

    st.subheader("Main Response Dataset")

    if not full_crp.empty:
        safe_dataframe(full_crp.head(10))


# ============================================================
# TAB 2: CRP EXPLORER
# ============================================================

with tab2:

    st.header("Challenge-Response Pair Explorer")

    if not full_crp.empty:

        crp_ids = sorted(
            full_crp["crp_id"].dropna().unique(),
            key=lambda x: int(x)
        )

        selected_crp = st.selectbox(
            "Select CRP ID",
            crp_ids
        )

        selected_rows = full_crp[
            full_crp["crp_id"].astype(str)
            == str(selected_crp)
        ]

        st.subheader(f"Responses for CRP {selected_crp}")

        safe_dataframe(selected_rows, height=300)

        if not selected_rows.empty:

            st.subheader("Response Bit Distribution")

            bit_counts = {"0": 0, "1": 0}

            for response in selected_rows["response_bits"].astype(str):
                bit_counts["0"] += response.count("0")
                bit_counts["1"] += response.count("1")

            bit_df = pd.DataFrame({
                "Bit": ["0", "1"],
                "Count": [
                    bit_counts["0"],
                    bit_counts["1"]
                ]
            })

            fig = px.bar(
                bit_df,
                x="Bit",
                y="Count",
                title="Response Bit Distribution"
            )

            st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("Full CRP response file not found.")

    st.divider()

    st.subheader("Challenge Sequence Explorer")

    if not challenges.empty:

        challenge_ids = sorted(
            challenges["crp_id"].dropna().unique(),
            key=lambda x: int(x)
        )

        selected_challenge = st.selectbox(
            "Select challenge ID",
            challenge_ids,
            key="challenge_selector"
        )

        challenge_row = challenges[
            challenges["crp_id"].astype(str)
            == str(selected_challenge)
        ]

        safe_dataframe(challenge_row, height=200)

    else:
        st.info("Temperature challenge file not found.")


# ============================================================
# TAB 3: OSCILLATOR ANALYSIS
# ============================================================

with tab3:

    st.header("RC Oscillator Analysis")

    st.markdown("""
    The Schmitt-trigger oscillator period is modelled using
    Equation (5):

    \[
    P_i = RC \\ln\\left(
    \\frac{V_{iH}(V_{DD}-V_{iL})}
    {V_{iL}(V_{DD}-V_{iH})}
    \\right)
    \]
    """)

    if not periods.empty:

        st.subheader("Oscillator Period Dataset")

        safe_dataframe(periods, height=350)

        numeric = get_numeric_columns(periods)

        if numeric:

            column = st.selectbox(
                "Select numeric parameter to plot",
                list(numeric.keys())
            )

            plot_df = pd.DataFrame({
                "Value": numeric[column]
            }).dropna()

            fig = px.histogram(
                plot_df,
                x="Value",
                title=f"Distribution of {column}",
                nbins=30
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:
            st.info("No numeric columns available for plotting.")

    else:
        st.info("Oscillator period CSV not found.")


# ============================================================
# TAB 4: EXPERIMENTS
# ============================================================

with tab4:

    st.header("Experimental Results")

    experiment_files = [
        "averaging_results.csv",
        "steadiness_results.csv",
        "exact_steadiness_results.csv",
        "temperature_reliability_results.csv",
        "error_probability_results.csv",
        "minimum_entropy_results.csv",
        "error_probability_per_crp.csv",
        "temperature_coefficients.csv",
        "pairwise_responses.csv"
    ]

    for filename in experiment_files:

        df = load_csv(filename)

        with st.expander(
            f"{filename} — {len(df):,} rows",
            expanded=False
        ):

            if df.empty:
                st.info("File unavailable.")
                continue

            safe_dataframe(df.head(100), height=300)

            numeric = get_numeric_columns(df)

            if numeric:

                possible_columns = list(numeric.keys())

                column = st.selectbox(
                    f"Select parameter to plot from {filename}",
                    possible_columns,
                    key=f"plot_{filename}"
                )

                plot_df = pd.DataFrame({
                    "Observation": range(len(numeric[column])),
                    "Value": numeric[column]
                }).dropna()

                if len(plot_df) > 5000:
                    plot_df = plot_df.head(5000)

                fig = px.line(
                    plot_df,
                    x="Observation",
                    y="Value",
                    title=f"{filename}: {column}"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )


# ============================================================
# TAB 5: PAPER COMPARISON
# ============================================================

with tab5:

    st.header("Paper Reference Comparison")

    st.markdown("""
    The following reference values are taken from the
    paper's reported evaluation. They are comparison
    references, not targets forced into the simulation.
    """)

    if metrics:

        comparison = pd.DataFrame({
            "Metric": [
                "Uniqueness",
                "Uniformity",
                "Randomness"
            ],
            "Software Result (%)": [
                metrics["uniqueness"],
                metrics["uniformity"],
                metrics["randomness"]
            ],
            "Paper Reference (%)": [
                49.75,
                50.00,
                99.73
            ]
        })

        safe_dataframe(comparison)

        fig = go.Figure()

        fig.add_trace(go.Bar(
            name="Software Result",
            x=comparison["Metric"],
            y=comparison["Software Result (%)"]
        ))

        fig.add_trace(go.Bar(
            name="Paper Reference",
            x=comparison["Metric"],
            y=comparison["Paper Reference (%)"]
        ))

        fig.update_layout(
            title="Software Results vs Paper Reference",
            barmode="group",
            yaxis_title="Percentage (%)"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    entropy = load_csv("minimum_entropy_results.csv")

    if not entropy.empty:

        st.subheader("Minimum Entropy Results")

        safe_dataframe(entropy.head(20))

        entropy_numeric = get_numeric_columns(entropy)

        entropy_columns = [
            name for name in entropy_numeric
            if "entropy" in name.lower()
        ]

        if entropy_columns:

            selected_entropy = entropy_columns[0]

            entropy_values = entropy_numeric[selected_entropy].dropna()

            if not entropy_values.empty:

                st.metric(
                    "Mean Minimum Entropy",
                    f"{entropy_values.mean():.6f}"
                )

                st.metric(
                    "Population Standard Deviation",
                    f"{entropy_values.std(ddof=0):.6f}"
                )


# ============================================================
# TAB 6: CSV RESULTS
# ============================================================

with tab6:

    st.header("All Experiment Result Files")

    csv_files = sorted(RESULTS.glob("*.csv"))

    if not csv_files:

        st.warning("No CSV files found in the results folder.")

    else:

        st.success(
            f"{len(csv_files)} CSV result files detected."
        )

        for path in csv_files:

            df = load_csv(path.name)

            with st.expander(
                f"{path.name} — {len(df):,} rows"
            ):

                if df.empty:
                    st.info("File unavailable.")
                    continue

                safe_dataframe(
                    df.head(100),
                    height=300
                )

                st.download_button(
                    label=f"Download {path.name}",
                    data=path.read_bytes(),
                    file_name=path.name,
                    mime="text/csv",
                    key=f"download_{path.name}"
                )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Schmitt-Trigger PUF Software Paper Replication | "
    "Synthetic simulation results | Physical FPGA validation pending"
)
