# ============================================================
# APL LOGISTICS
# Delivery Performance, Delay Risk & Logistics Efficiency
# Streamlit Dashboard
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path


# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="APL Logistics Analytics Dashboard",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# 2. CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main {
        padding-top: 1rem;
    }

    .dashboard-title {
        font-size: 36px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .dashboard-subtitle {
        font-size: 17px;
        color: #6c757d;
        margin-bottom: 25px;
    }

    .kpi-card {
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        justify-content: center;
        background: #ffffff;
        padding: 20px 16px;
        border-radius: 14px;
        border: 1px solid #dbe3ee;
        border-top: 4px solid #2f80ed;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.12);
        text-align: center;
        min-height: 132px;
        color: #0f172a !important;
    }

    .kpi-title {
        font-size: 14px;
        line-height: 1.4;
        color: #475569 !important;
        font-weight: 600;
    }

    .kpi-value {
        font-size: clamp(22px, 2vw, 30px);
        line-height: 1.2;
        color: #0f172a !important;
        font-weight: 700;
        margin-top: 10px;
    }

    .section-title {
        font-size: 23px;
        font-weight: 700;
        margin-top: 20px;
        margin-bottom: 10px;
    }

    .info-box {
        background-color: #eef6ff;
        color: #17324d !important;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #2f80ed;
        margin-bottom: 15px;
    }

    .warning-box {
        background-color: #fff8e6;
        color: #594411 !important;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #f2c94c;
        margin-bottom: 15px;
    }

    .info-box *, .warning-box * {
        color: inherit !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 3. DATA PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_PATH = BASE_DIR / "03_Cleaned_Data" / "APL_Logistics_Cleaned_sample.csv"


# ============================================================
# 4. CHECK DATASET
# ============================================================

if not DATA_PATH.exists():

    st.error("❌ Dataset not found.")

    st.write("Streamlit is looking for the file at:")

    st.code(str(DATA_PATH))

    st.warning(
        """
        Make sure your folder structure is exactly:

        D:\\APL_Logistics_Project\\
        ├── app.py
        └── data\\
            └── APL_Logistics_Cleaned_sample.csv
        """
    )

    st.stop()


# ============================================================
# 5. LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    df = pd.read_csv(
        DATA_PATH,
        encoding="utf-8-sig"
    )

    return df


df = load_data()


# ============================================================
# 6. REQUIRED COLUMNS
# ============================================================

required_columns = [
    "Days for shipping (real)",
    "Days for shipment (scheduled)",
    "Delivery Status",
    "Late_delivery_risk",
    "Shipping Mode",
    "Order Region",
    "Market",
    "Customer Segment",
    "Sales",
    "Order Profit Per Order",
    "Order Item Total",
    "Order Item Quantity"
]


missing_columns = [
    column for column in required_columns
    if column not in df.columns
]


if missing_columns:

    st.error("❌ Required columns are missing from the dataset.")

    st.write("Missing columns:")

    for column in missing_columns:
        st.write(f"- {column}")

    st.stop()


# ============================================================
# 7. FEATURE ENGINEERING
# ============================================================

# Delay Gap
df["Delay Gap"] = (
    df["Days for shipping (real)"]
    - df["Days for shipment (scheduled)"]
)


# Delivery Performance
df["Delivery Performance"] = "On-Time"


# Canceled
df.loc[
    df["Delivery Status"] == "Shipping canceled",
    "Delivery Performance"
] = "Canceled"


# Early
df.loc[
    (df["Delay Gap"] < 0)
    & (df["Delivery Status"] != "Shipping canceled"),
    "Delivery Performance"
] = "Early"


# Delayed
df.loc[
    (df["Delay Gap"] > 0)
    & (df["Delivery Status"] != "Shipping canceled"),
    "Delivery Performance"
] = "Delayed"


# Delay Severity
df["Delay Severity"] = "On-Time / Early"


df.loc[
    df["Delay Gap"] == 1,
    "Delay Severity"
] = "Minor Delay"


df.loc[
    df["Delay Gap"] == 2,
    "Delay Severity"
] = "Moderate Delay"


df.loc[
    df["Delay Gap"] >= 3,
    "Delay Severity"
] = "Severe Delay"


# ============================================================
# 8. SIDEBAR
# ============================================================

st.sidebar.title("🚚 APL Logistics")

st.sidebar.markdown(
    "### Dashboard Filters"
)

st.sidebar.markdown(
    "Use the filters below to analyze logistics performance."
)


# Shipping Mode
shipping_modes = sorted(
    df["Shipping Mode"]
    .dropna()
    .unique()
    .tolist()
)

selected_shipping_modes = st.sidebar.multiselect(
    "Shipping Mode",
    options=shipping_modes,
    default=shipping_modes
)


# Region
regions = sorted(
    df["Order Region"]
    .dropna()
    .unique()
    .tolist()
)

selected_regions = st.sidebar.multiselect(
    "Order Region",
    options=regions,
    default=regions
)


# Market
markets = sorted(
    df["Market"]
    .dropna()
    .unique()
    .tolist()
)

selected_markets = st.sidebar.multiselect(
    "Market",
    options=markets,
    default=markets
)


# Customer Segment
segments = sorted(
    df["Customer Segment"]
    .dropna()
    .unique()
    .tolist()
)

selected_segments = st.sidebar.multiselect(
    "Customer Segment",
    options=segments,
    default=segments
)


# ============================================================
# 9. APPLY FILTERS
# ============================================================

filtered_df = df[
    df["Shipping Mode"].isin(selected_shipping_modes)
    &
    df["Order Region"].isin(selected_regions)
    &
    df["Market"].isin(selected_markets)
    &
    df["Customer Segment"].isin(selected_segments)
].copy()

if filtered_df.empty:
    st.warning(
        "No shipments match the selected filters. Select at least one "
        "value in each sidebar filter to display the dashboard."
    )
    st.stop()


# ============================================================
# 10. HEADER
# ============================================================

st.markdown(
    '<div class="dashboard-title">🚚 APL Logistics Analytics Dashboard</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="dashboard-subtitle">
    Delivery Performance, Delay Risk & Logistics Efficiency Analysis
    </div>
    """,
    unsafe_allow_html=True
)


st.markdown(
    f"""
    <div class="info-box">
    <b>Filtered Shipments:</b> {len(filtered_df):,}
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 11. DATASET LIMITATION NOTICE
# ============================================================

st.markdown(
    """
    <div class="warning-box">
    <b>Dataset Limitation:</b>
    This dataset does not contain a shipment/order date field.
    Therefore, this dashboard focuses on operational performance,
    delay risk, shipping modes, regions, markets and business impact.
    Date-based trend analysis is not available.
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 12. KPI CALCULATIONS
# ============================================================

total_shipments = len(filtered_df)


delayed_shipments = (
    filtered_df["Delivery Performance"]
    == "Delayed"
).sum()


on_time_shipments = (
    filtered_df["Delivery Performance"]
    == "On-Time"
).sum()


early_shipments = (
    filtered_df["Delivery Performance"]
    == "Early"
).sum()


canceled_shipments = (
    filtered_df["Delivery Performance"]
    == "Canceled"
).sum()


non_cancelled = total_shipments - canceled_shipments


if non_cancelled > 0:

    delay_rate = (
        delayed_shipments
        / non_cancelled
        * 100
    )

    on_time_rate = (
        on_time_shipments
        / non_cancelled
        * 100
    )

    early_rate = (
        early_shipments
        / non_cancelled
        * 100
    )

else:

    delay_rate = 0
    on_time_rate = 0
    early_rate = 0


cancellation_rate = (
    canceled_shipments
    / total_shipments
    * 100
    if total_shipments > 0
    else 0
)


average_delay_gap = (
    filtered_df["Delay Gap"].mean()
    if total_shipments > 0
    else 0
)


delayed_only = filtered_df[
    filtered_df["Delivery Performance"] == "Delayed"
]


average_delay_when_delayed = (
    delayed_only["Delay Gap"].mean()
    if len(delayed_only) > 0
    else 0
)


total_sales = filtered_df["Sales"].sum()


total_profit = (
    filtered_df["Order Profit Per Order"].sum()
)


# ============================================================
# 13. KPI CARDS
# ============================================================

kpi1, kpi2, kpi3, kpi4 = st.columns(4)


with kpi1:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Shipments</div>
            <div class="kpi-value">{total_shipments:,}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


with kpi2:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Delay Rate</div>
            <div class="kpi-value">{delay_rate:.2f}%</div>
        </div>
        """,
        unsafe_allow_html=True
    )


with kpi3:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">On-Time Rate</div>
            <div class="kpi-value">{on_time_rate:.2f}%</div>
        </div>
        """,
        unsafe_allow_html=True
    )


with kpi4:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Cancellation Rate</div>
            <div class="kpi-value">{cancellation_rate:.2f}%</div>
        </div>
        """,
        unsafe_allow_html=True
    )


st.write("")


kpi5, kpi6, kpi7, kpi8 = st.columns(4)


with kpi5:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Delayed Shipments</div>
            <div class="kpi-value">{delayed_shipments:,}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


with kpi6:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Average Delay Gap</div>
            <div class="kpi-value">{average_delay_gap:.2f} days</div>
        </div>
        """,
        unsafe_allow_html=True
    )


with kpi7:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Sales</div>
            <div class="kpi-value">₹{total_sales:,.0f}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


with kpi8:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Profit</div>
            <div class="kpi-value">₹{total_profit:,.0f}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# 14. TABS
# ============================================================

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
    [
        "📊 Overview",
        "⚠️ Delay Risk",
        "🚢 Shipping Mode",
        "🌍 Regional Analysis",
        "👥 Customer Segment",
        "💰 Business Impact",
        "📋 Data"
    ]
)


# ============================================================
# TAB 1: OVERVIEW
# ============================================================

with tab1:

    st.markdown(
        '<div class="section-title">Delivery Performance Overview</div>',
        unsafe_allow_html=True
    )


    col1, col2 = st.columns(2)


    # --------------------------------------------------------
    # Delivery Performance
    # --------------------------------------------------------

    with col1:

        performance_counts = (
            filtered_df["Delivery Performance"]
            .value_counts()
            .reset_index()
        )

        performance_counts.columns = [
            "Delivery Performance",
            "Shipments"
        ]


        fig = px.bar(
            performance_counts,
            x="Delivery Performance",
            y="Shipments",
            title="Delivery Performance Distribution",
            text="Shipments"
        )


        fig.update_traces(
            texttemplate="%{text:,}",
            textposition="outside"
        )


        fig.update_layout(
            height=450,
            showlegend=False
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # --------------------------------------------------------
    # Delivery Performance Pie
    # --------------------------------------------------------

    with col2:

        fig = px.pie(
            performance_counts,
            names="Delivery Performance",
            values="Shipments",
            title="Shipment Share by Delivery Performance",
            hole=0.45
        )


        fig.update_layout(
            height=450
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # --------------------------------------------------------
    # Delay Gap Distribution
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">Delay Gap Distribution</div>',
        unsafe_allow_html=True
    )


    delay_distribution = (
        filtered_df["Delay Gap"]
        .value_counts()
        .sort_index()
        .reset_index()
    )

    delay_distribution.columns = [
        "Delay Gap",
        "Shipments"
    ]


    delay_distribution["Delay Gap"] = (
        delay_distribution["Delay Gap"]
        .astype(int)
    )


    fig = px.bar(
        delay_distribution,
        x="Delay Gap",
        y="Shipments",
        title="Actual Shipping Days vs Scheduled Shipping Days",
        text="Shipments"
    )


    fig.update_traces(
        texttemplate="%{text:,}",
        textposition="outside"
    )


    fig.update_layout(
        height=450,
        xaxis_title="Delay Gap (Days)",
        yaxis_title="Number of Shipments"
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# TAB 2: DELAY RISK
# ============================================================

with tab2:

    st.markdown(
        '<div class="section-title">⚠️ Delay Risk Analysis</div>',
        unsafe_allow_html=True
    )


    risk_counts = (
        filtered_df["Late_delivery_risk"]
        .value_counts()
        .sort_index()
        .reset_index()
    )


    risk_counts.columns = [
        "Late Delivery Risk",
        "Shipments"
    ]


    risk_counts["Risk Label"] = (
        risk_counts["Late Delivery Risk"]
        .map({
            0: "No Risk",
            1: "Risk"
        })
    )


    col1, col2 = st.columns(2)


    with col1:

        fig = px.pie(
            risk_counts,
            names="Risk Label",
            values="Shipments",
            title="Late Delivery Risk Distribution",
            hole=0.45
        )


        fig.update_layout(
            height=450
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


    with col2:

        severity_counts = (
            filtered_df["Delay Severity"]
            .value_counts()
            .reset_index()
        )


        severity_counts.columns = [
            "Delay Severity",
            "Shipments"
        ]


        fig = px.bar(
            severity_counts,
            x="Delay Severity",
            y="Shipments",
            title="Delay Severity Distribution",
            text="Shipments"
        )


        fig.update_traces(
            texttemplate="%{text:,}",
            textposition="outside"
        )


        fig.update_layout(
            height=450
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # --------------------------------------------------------
    # Delay severity table
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">Delay Severity Details</div>',
        unsafe_allow_html=True
    )


    severity_summary = (
        filtered_df
        .groupby("Delay Severity")
        .agg(
            Shipments=("Delay Gap", "size"),
            Average_Gap=("Delay Gap", "mean"),
            Maximum_Gap=("Delay Gap", "max")
        )
        .reset_index()
    )


    severity_summary["Share (%)"] = (
        severity_summary["Shipments"]
        / total_shipments
        * 100
    )


    severity_summary["Average_Gap"] = (
        severity_summary["Average_Gap"]
        .round(2)
    )


    severity_summary["Share (%)"] = (
        severity_summary["Share (%)"]
        .round(2)
    )


    st.dataframe(
        severity_summary,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# TAB 3: SHIPPING MODE
# ============================================================

with tab3:

    st.markdown(
        '<div class="section-title">🚢 Shipping Mode Analysis</div>',
        unsafe_allow_html=True
    )


    mode_analysis = (
        filtered_df
        .groupby("Shipping Mode")
        .agg(
            Total_Shipments=("Shipping Mode", "size"),
            Delayed=("Delivery Performance", lambda x: (x == "Delayed").sum()),
            On_Time=("Delivery Performance", lambda x: (x == "On-Time").sum()),
            Early=("Delivery Performance", lambda x: (x == "Early").sum()),
            Canceled=("Delivery Performance", lambda x: (x == "Canceled").sum()),
            Average_Delay_Gap=("Delay Gap", "mean")
        )
        .reset_index()
    )


    mode_analysis["Non_Canceled"] = (
        mode_analysis["Total_Shipments"]
        - mode_analysis["Canceled"]
    )


    mode_analysis["Delay Rate (%)"] = (
        mode_analysis["Delayed"]
        / mode_analysis["Non_Canceled"]
        * 100
    )


    mode_analysis["On-Time Rate (%)"] = (
        mode_analysis["On_Time"]
        / mode_analysis["Non_Canceled"]
        * 100
    )


    mode_analysis["Efficiency Index"] = (
        mode_analysis["On-Time Rate (%)"]
        - mode_analysis["Delay Rate (%)"]
    )


    mode_analysis = mode_analysis.round(2)


    col1, col2 = st.columns(2)


    # --------------------------------------------------------
    # Delay by Shipping Mode
    # --------------------------------------------------------

    with col1:

        fig = px.bar(
            mode_analysis.sort_values(
                "Delay Rate (%)",
                ascending=False
            ),
            x="Shipping Mode",
            y="Delay Rate (%)",
            title="Delay Rate by Shipping Mode",
            text="Delay Rate (%)"
        )


        fig.update_traces(
            texttemplate="%{text:.2f}%",
            textposition="outside"
        )


        fig.update_layout(
            height=450,
            yaxis_title="Delay Rate (%)"
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # --------------------------------------------------------
    # On-Time by Shipping Mode
    # --------------------------------------------------------

    with col2:

        fig = px.bar(
            mode_analysis.sort_values(
                "On-Time Rate (%)",
                ascending=False
            ),
            x="Shipping Mode",
            y="On-Time Rate (%)",
            title="On-Time Rate by Shipping Mode",
            text="On-Time Rate (%)"
        )


        fig.update_traces(
            texttemplate="%{text:.2f}%",
            textposition="outside"
        )


        fig.update_layout(
            height=450,
            yaxis_title="On-Time Rate (%)"
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # --------------------------------------------------------
    # Efficiency Index
    # --------------------------------------------------------

    fig = px.bar(
        mode_analysis.sort_values(
            "Efficiency Index",
            ascending=False
        ),
        x="Shipping Mode",
        y="Efficiency Index",
        title="Shipping Mode Efficiency Index",
        text="Efficiency Index"
    )


    fig.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside"
    )


    fig.update_layout(
        height=450,
        yaxis_title="On-Time Rate - Delay Rate"
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # --------------------------------------------------------
    # Shipping mode table
    # --------------------------------------------------------

    st.dataframe(
        mode_analysis,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# TAB 4: REGIONAL ANALYSIS
# ============================================================

with tab4:

    st.markdown(
        '<div class="section-title">🌍 Regional Performance</div>',
        unsafe_allow_html=True
    )


    regional_analysis = (
        filtered_df
        .groupby("Order Region")
        .agg(
            Total_Shipments=("Order Region", "size"),
            Delayed=("Delivery Performance", lambda x: (x == "Delayed").sum()),
            On_Time=("Delivery Performance", lambda x: (x == "On-Time").sum()),
            Canceled=("Delivery Performance", lambda x: (x == "Canceled").sum()),
            Average_Delay_Gap=("Delay Gap", "mean")
        )
        .reset_index()
    )


    regional_analysis["Non_Canceled"] = (
        regional_analysis["Total_Shipments"]
        - regional_analysis["Canceled"]
    )


    regional_analysis["Delay Rate (%)"] = (
        regional_analysis["Delayed"]
        / regional_analysis["Non_Canceled"]
        * 100
    )


    regional_analysis["On-Time Rate (%)"] = (
        regional_analysis["On_Time"]
        / regional_analysis["Non_Canceled"]
        * 100
    )


    regional_analysis = regional_analysis.round(2)


    # --------------------------------------------------------
    # Top Risk Regions
    # --------------------------------------------------------

    top_regions = (
        regional_analysis
        .sort_values(
            "Delay Rate (%)",
            ascending=False
        )
        .head(10)
    )


    fig = px.bar(
        top_regions.sort_values(
            "Delay Rate (%)"
        ),
        x="Delay Rate (%)",
        y="Order Region",
        orientation="h",
        title="Top 10 Regions by Delay Rate",
        text="Delay Rate (%)"
    )


    fig.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside"
    )


    fig.update_layout(
        height=550,
        yaxis_title=""
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # --------------------------------------------------------
    # Market Analysis
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">Market Performance</div>',
        unsafe_allow_html=True
    )


    market_analysis = (
        filtered_df
        .groupby("Market")
        .agg(
            Total_Shipments=("Market", "size"),
            Delayed=("Delivery Performance", lambda x: (x == "Delayed").sum()),
            On_Time=("Delivery Performance", lambda x: (x == "On-Time").sum()),
            Canceled=("Delivery Performance", lambda x: (x == "Canceled").sum())
        )
        .reset_index()
    )


    market_analysis["Non_Canceled"] = (
        market_analysis["Total_Shipments"]
        - market_analysis["Canceled"]
    )


    market_analysis["Delay Rate (%)"] = (
        market_analysis["Delayed"]
        / market_analysis["Non_Canceled"]
        * 100
    )


    market_analysis["On-Time Rate (%)"] = (
        market_analysis["On_Time"]
        / market_analysis["Non_Canceled"]
        * 100
    )


    market_analysis = market_analysis.round(2)


    fig = px.bar(
        market_analysis.sort_values(
            "Delay Rate (%)",
            ascending=False
        ),
        x="Market",
        y="Delay Rate (%)",
        title="Delay Rate by Market",
        text="Delay Rate (%)"
    )


    fig.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside"
    )


    fig.update_layout(
        height=450
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # --------------------------------------------------------
    # Regional Table
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">Regional Performance Table</div>',
        unsafe_allow_html=True
    )


    st.dataframe(
        regional_analysis.sort_values(
            "Delay Rate (%)",
            ascending=False
        ),
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# TAB 5: CUSTOMER SEGMENT
# ============================================================

with tab5:

    st.markdown(
        '<div class="section-title">👥 Customer Segment Analysis</div>',
        unsafe_allow_html=True
    )


    segment_analysis = (
        filtered_df
        .groupby("Customer Segment")
        .agg(
            Total_Shipments=("Customer Segment", "size"),
            Delayed=("Delivery Performance", lambda x: (x == "Delayed").sum()),
            On_Time=("Delivery Performance", lambda x: (x == "On-Time").sum()),
            Canceled=("Delivery Performance", lambda x: (x == "Canceled").sum()),
            Average_Delay_Gap=("Delay Gap", "mean")
        )
        .reset_index()
    )


    segment_analysis["Non_Canceled"] = (
        segment_analysis["Total_Shipments"]
        - segment_analysis["Canceled"]
    )


    segment_analysis["Delay Rate (%)"] = (
        segment_analysis["Delayed"]
        / segment_analysis["Non_Canceled"]
        * 100
    )


    segment_analysis["On-Time Rate (%)"] = (
        segment_analysis["On_Time"]
        / segment_analysis["Non_Canceled"]
        * 100
    )


    segment_analysis = segment_analysis.round(2)


    col1, col2 = st.columns(2)


    with col1:

        fig = px.bar(
            segment_analysis,
            x="Customer Segment",
            y="Delay Rate (%)",
            title="Delay Rate by Customer Segment",
            text="Delay Rate (%)"
        )


        fig.update_traces(
            texttemplate="%{text:.2f}%",
            textposition="outside"
        )


        fig.update_layout(
            height=450
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


    with col2:

        fig = px.bar(
            segment_analysis,
            x="Customer Segment",
            y="On-Time Rate (%)",
            title="On-Time Rate by Customer Segment",
            text="On-Time Rate (%)"
        )


        fig.update_traces(
            texttemplate="%{text:.2f}%",
            textposition="outside"
        )


        fig.update_layout(
            height=450
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


    st.dataframe(
        segment_analysis,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# TAB 6: BUSINESS IMPACT
# ============================================================

with tab6:

    st.markdown(
        '<div class="section-title">💰 Business Impact Analysis</div>',
        unsafe_allow_html=True
    )


    business_analysis = (
        filtered_df
        .groupby("Delivery Performance")
        .agg(
            Shipments=("Delivery Performance", "size"),
            Sales=("Sales", "sum"),
            Average_Sales=("Sales", "mean"),
            Total_Profit=("Order Profit Per Order", "sum"),
            Average_Profit=("Order Profit Per Order", "mean"),
            Average_Order_Value=("Order Item Total", "mean"),
            Average_Quantity=("Order Item Quantity", "mean")
        )
        .reset_index()
    )


    business_analysis["Shipment Share (%)"] = (
        business_analysis["Shipments"]
        / total_shipments
        * 100
    )


    business_analysis["Sales Share (%)"] = (
        business_analysis["Sales"]
        / total_sales
        * 100
        if total_sales != 0
        else 0
    )


    business_analysis = business_analysis.round(2)


    col1, col2 = st.columns(2)


    # --------------------------------------------------------
    # Sales by Delivery Performance
    # --------------------------------------------------------

    with col1:

        fig = px.bar(
            business_analysis,
            x="Delivery Performance",
            y="Sales",
            title="Sales by Delivery Performance",
            text="Sales"
        )


        fig.update_traces(
            texttemplate="₹%{text:,.0f}",
            textposition="outside"
        )


        fig.update_layout(
            height=450
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # --------------------------------------------------------
    # Profit by Delivery Performance
    # --------------------------------------------------------

    with col2:

        fig = px.bar(
            business_analysis,
            x="Delivery Performance",
            y="Total_Profit",
            title="Total Profit by Delivery Performance",
            text="Total_Profit"
        )


        fig.update_traces(
            texttemplate="₹%{text:,.0f}",
            textposition="outside"
        )


        fig.update_layout(
            height=450
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # --------------------------------------------------------
    # Business Impact KPIs
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">Business Impact Summary</div>',
        unsafe_allow_html=True
    )


    delayed_sales = (
        filtered_df.loc[
            filtered_df["Delivery Performance"] == "Delayed",
            "Sales"
        ].sum()
    )


    delayed_sales_share = (
        delayed_sales
        / total_sales
        * 100
        if total_sales != 0
        else 0
    )


    b1, b2, b3 = st.columns(3)


    with b1:

        st.metric(
            "Delayed Shipment Sales",
            f"₹{delayed_sales:,.0f}"
        )


    with b2:

        st.metric(
            "Delayed Sales Share",
            f"{delayed_sales_share:.2f}%"
        )


    with b3:

        st.metric(
            "Average Profit per Delayed Shipment",
            f"₹{(
                delayed_only['Order Profit Per Order'].mean()
                if len(delayed_only) > 0
                else 0
            ):,.2f}"
        )


    st.dataframe(
        business_analysis,
        use_container_width=True,
        hide_index=True
    )


    st.info(
        """
        Business impact figures show association between delivery
        performance and sales/profit. They should not be interpreted
        as proof that delays directly caused changes in financial
        performance.
        """
    )


# ============================================================
# TAB 7: DATA
# ============================================================

with tab7:

    st.markdown(
        '<div class="section-title">📋 Filtered Dataset</div>',
        unsafe_allow_html=True
    )


    st.write(
        f"Showing {len(filtered_df):,} records after applying filters."
    )


    # Search columns
    search_columns = [
        "Shipping Mode",
        "Order Region",
        "Market",
        "Customer Segment",
        "Delivery Status",
        "Delivery Performance",
        "Delay Severity"
    ]


    available_search_columns = [
        column
        for column in search_columns
        if column in filtered_df.columns
    ]


    selected_search_column = st.selectbox(
        "Search Column",
        available_search_columns
    )


    search_value = st.text_input(
        "Search Value",
        placeholder="Type a value..."
    )


    display_df = filtered_df.copy()


    if search_value.strip():

        search_text = search_value.strip().lower()

        display_df = display_df[
            display_df[selected_search_column]
            .astype(str)
            .str.lower()
            .str.contains(
                search_text,
                na=False
            )
        ]


    st.write(
        f"Records displayed: {len(display_df):,}"
    )


    st.dataframe(
        display_df,
        use_container_width=True,
        height=550,
        hide_index=True
    )


    # --------------------------------------------------------
    # Download filtered data
    # --------------------------------------------------------

    csv_data = display_df.to_csv(
        index=False
    ).encode("utf-8-sig")


    st.download_button(
        label="⬇️ Download Filtered Data",
        data=csv_data,
        file_name="APL_Logistics_Filtered_Data.csv",
        mime="text/csv"
    )


# ============================================================
# 15. SIDEBAR PROJECT INFORMATION
# ============================================================

st.sidebar.markdown("---")

st.sidebar.markdown(
    """
    ### 📌 Project Information

    **Project:**  
    APL Logistics Delivery Performance & Delay Risk Analytics

    **Dataset:**  
    APL Logistics Supply Chain Dataset

    **Analytics Focus:**
    - Delivery performance
    - Delay risk
    - Shipping mode efficiency
    - Regional bottlenecks
    - Market performance
    - Customer segments
    - Delay severity
    - Business impact

    **Technologies:**
    - Python
    - Pandas
    - NumPy
    - Plotly
    - Streamlit

    **Important:**
    No date field is available in the dataset, so
    time-series analysis is not included.
    """
)


# ============================================================
# 16. FOOTER
# ============================================================

st.markdown("---")

st.markdown(
    """
    <div style="text-align:center; color:#777;">
        APL Logistics Delivery Performance & Delay Risk Analytics
        <br>
        Built with Python, Pandas, Plotly & Streamlit
    </div>
    """,
    unsafe_allow_html=True
)
