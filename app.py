import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="APL Logistics | Delivery Analytics",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main {
        padding-top: 1rem;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    .metric-card {
        padding: 10px;
        border-radius: 10px;
    }

    h1 {
        font-weight: 700;
    }

    h2 {
        font-weight: 650;
    }

    h3 {
        font-weight: 600;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# LOAD DATA
# ============================================================

analysis_file = (
    r"D:\APL_Logistics_Project"
    r"\04_Analysis"
    r"\APL_Logistics_Analysis.csv"
)


if not os.path.exists(analysis_file):

    st.error("❌ Analysis dataset was not found.")

    st.write("Expected file location:")
    st.code(analysis_file)

    st.stop()


@st.cache_data
def load_data():

    data = pd.read_csv(
        analysis_file,
        encoding="utf-8-sig"
    )

    return data


df = load_data()


# ============================================================
# BASIC DATA VALIDATION
# ============================================================

required_columns = [
    "Shipping Mode",
    "Order Region",
    "Market",
    "Customer Segment",
    "Delivery Performance",
    "Delay Gap",
    "Days for shipping (real)",
    "Days for shipment (scheduled)",
    "Late_delivery_risk",
    "Sales",
    "Order Profit Per Order",
    "Order Item Quantity",
    "Order Item Discount Rate"
]


missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]


if missing_columns:

    st.error("❌ Required columns are missing from the dataset.")

    st.write(missing_columns)

    st.stop()


# ============================================================
# TITLE
# ============================================================

st.title("🚚 APL Logistics")

st.subheader(
    "Delivery Performance, Delay Risk & Logistics Efficiency Dashboard"
)

st.markdown(
    """
    **Global Supply Chain Operations Analytics**

    This dashboard evaluates delivery performance, delay severity,
    shipping-mode efficiency, regional and market risk,
    customer-segment exposure, and business impact.
    """
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🔎 Dashboard Filters")

st.sidebar.markdown("Filter from top to bottom. Each list updates from selections above it.")


def available_values(data, column):
    """Return valid display-ready values for a filter."""
    return sorted(data[column].dropna().unique().tolist())


def reconcile_selection(key, options):
    """Remove selections invalidated by an upstream filter."""
    if key not in st.session_state:
        st.session_state[key] = options
    else:
        st.session_state[key] = [value for value in st.session_state[key] if value in options]


all_shipping_modes = available_values(df, "Shipping Mode")
all_regions = available_values(df, "Order Region")
all_markets = available_values(df, "Market")
all_segments = available_values(df, "Customer Segment")

if st.sidebar.button("Reset all filters", use_container_width=True):
    st.session_state["shipping_mode_filter"] = all_shipping_modes
    st.session_state["region_filter"] = all_regions
    st.session_state["market_filter"] = all_markets
    st.session_state["segment_filter"] = all_segments

reconcile_selection("shipping_mode_filter", all_shipping_modes)
selected_shipping_modes = st.sidebar.multiselect(
    "Shipping Mode", all_shipping_modes, key="shipping_mode_filter",
    placeholder="Select one or more shipping modes"
)

region_source = df[df["Shipping Mode"].isin(selected_shipping_modes)]
regions = available_values(region_source, "Order Region")
reconcile_selection("region_filter", regions)
selected_regions = st.sidebar.multiselect(
    "Order Region", regions, key="region_filter",
    placeholder="Select one or more regions"
)

market_source = region_source[region_source["Order Region"].isin(selected_regions)]
markets = available_values(market_source, "Market")
reconcile_selection("market_filter", markets)
selected_markets = st.sidebar.multiselect(
    "Market", markets, key="market_filter",
    placeholder="Select one or more markets"
)

segment_source = market_source[market_source["Market"].isin(selected_markets)]
segments = available_values(segment_source, "Customer Segment")
reconcile_selection("segment_filter", segments)
selected_segments = st.sidebar.multiselect(
    "Customer Segment", segments, key="segment_filter",
    placeholder="Select one or more customer segments"
)


# ============================================================
# APPLY FILTERS
# ============================================================

filtered_df = df[
    (df["Shipping Mode"].isin(selected_shipping_modes))
    &
    (df["Order Region"].isin(selected_regions))
    &
    (df["Market"].isin(selected_markets))
    &
    (df["Customer Segment"].isin(selected_segments))
].copy()


# ============================================================
# FILTER SUMMARY
# ============================================================

st.sidebar.markdown("---")

st.sidebar.metric(
    "Filtered Shipments",
    f"{len(filtered_df):,}"
)

st.sidebar.metric(
    "Original Shipments",
    f"{len(df):,}"
)


# ============================================================
# EMPTY FILTER CHECK
# ============================================================

if filtered_df.empty:

    st.warning(
        "⚠️ No shipments match the selected filters. "
        "Please select at least one option in each filter."
    )

    st.stop()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def calculate_kpis(data):

    total = len(data)

    delayed = (
        data["Delivery Performance"] == "Delayed"
    ).sum()

    on_time = (
        data["Delivery Performance"] == "On-Time"
    ).sum()

    early = (
        data["Delivery Performance"] == "Early"
    ).sum()

    canceled = (
        data["Delivery Performance"] == "Canceled"
    ).sum()

    non_canceled = total - canceled

    if non_canceled > 0:

        delay_rate = (
            delayed / non_canceled
        ) * 100

        on_time_rate = (
            on_time / non_canceled
        ) * 100

        early_rate = (
            early / non_canceled
        ) * 100

    else:

        delay_rate = 0
        on_time_rate = 0
        early_rate = 0

    if total > 0:

        cancellation_rate = (
            canceled / total
        ) * 100

    else:

        cancellation_rate = 0

    delayed_data = data[
        data["Delivery Performance"] == "Delayed"
    ]

    if len(delayed_data) > 0:

        avg_delay = delayed_data[
            "Delay Gap"
        ].mean()

    else:

        avg_delay = 0

    return {
        "total": total,
        "delayed": delayed,
        "on_time": on_time,
        "early": early,
        "canceled": canceled,
        "delay_rate": delay_rate,
        "on_time_rate": on_time_rate,
        "early_rate": early_rate,
        "cancellation_rate": cancellation_rate,
        "avg_delay": avg_delay
    }


kpis = calculate_kpis(filtered_df)


# ============================================================
# EXECUTIVE OVERVIEW
# ============================================================

st.header("📊 Executive Overview")


# ------------------------------------------------------------
# Main KPI Cards
# ------------------------------------------------------------

col1, col2, col3, col4, col5 = st.columns(5)


with col1:

    st.metric(
        "📦 Total Shipments",
        f"{kpis['total']:,}"
    )


with col2:

    st.metric(
        "⚠️ Delay Rate",
        f"{kpis['delay_rate']:.2f}%"
    )


with col3:

    st.metric(
        "✅ On-Time Rate",
        f"{kpis['on_time_rate']:.2f}%"
    )


with col4:

    st.metric(
        "⏱️ Avg Delay",
        f"{kpis['avg_delay']:.2f} days"
    )


with col5:

    st.metric(
        "❌ Cancellation Rate",
        f"{kpis['cancellation_rate']:.2f}%"
    )


# ============================================================
# SECOND KPI ROW
# ============================================================

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Delayed",
        f"{kpis['delayed']:,}"
    )


with col2:

    st.metric(
        "On-Time",
        f"{kpis['on_time']:,}"
    )


with col3:

    st.metric(
        "Early",
        f"{kpis['early']:,}"
    )


with col4:

    st.metric(
        "Canceled",
        f"{kpis['canceled']:,}"
    )


# ============================================================
# TABS
# ============================================================

(
    tab_delivery,
    tab_risk,
    tab_shipping,
    tab_region,
    tab_segment,
    tab_business
) = st.tabs(
    [
        "📦 Delivery Performance",
        "⚠️ Delay Risk",
        "🚚 Shipping Mode",
        "🌍 Regional & Market",
        "👥 Customer Segment",
        "💰 Business Impact"
    ]
)


# ============================================================
# TAB 1
# DELIVERY PERFORMANCE
# ============================================================

with tab_delivery:

    st.header("📦 Delivery Performance")

    st.markdown(
        "Overall delivery-status distribution for the selected filters."
    )


    # --------------------------------------------------------
    # Delivery Performance Summary
    # --------------------------------------------------------

    delivery_summary = (
        filtered_df[
            "Delivery Performance"
        ]
        .value_counts()
        .reset_index()
    )

    delivery_summary.columns = [
        "Delivery Performance",
        "Shipments"
    ]


    delivery_summary["Percentage"] = (
        delivery_summary["Shipments"]
        / delivery_summary["Shipments"].sum()
        * 100
    )


    col1, col2 = st.columns(2)


    with col1:

        fig = px.pie(
            delivery_summary,
            names="Delivery Performance",
            values="Shipments",
            title="Delivery Performance Distribution",
            hole=0.45
        )

        fig.update_traces(
            textinfo="percent+label"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    with col2:

        fig = px.bar(
            delivery_summary,
            x="Delivery Performance",
            y="Shipments",
            text="Shipments",
            title="Shipment Count by Delivery Performance"
        )

        fig.update_traces(
            textposition="outside"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # --------------------------------------------------------
    # Shipping Time Comparison
    # --------------------------------------------------------

    st.subheader(
        "Planned vs Actual Shipping Time"
    )


    shipping_time = (
        filtered_df
        .groupby("Delivery Performance")
        .agg(
            Actual_Shipping_Days=(
                "Days for shipping (real)",
                "mean"
            ),
            Scheduled_Shipping_Days=(
                "Days for shipment (scheduled)",
                "mean"
            )
        )
        .reset_index()
    )


    fig = go.Figure()


    fig.add_trace(
        go.Bar(
            x=shipping_time[
                "Delivery Performance"
            ],
            y=shipping_time[
                "Actual_Shipping_Days"
            ],
            name="Actual Shipping Days"
        )
    )


    fig.add_trace(
        go.Bar(
            x=shipping_time[
                "Delivery Performance"
            ],
            y=shipping_time[
                "Scheduled_Shipping_Days"
            ],
            name="Scheduled Shipping Days"
        )
    )


    fig.update_layout(
        title="Average Actual vs Scheduled Shipping Days",
        barmode="group",
        yaxis_title="Days"
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# TAB 2
# DELAY RISK
# ============================================================

with tab_risk:

    st.header("⚠️ Delay Risk Analysis")


    # --------------------------------------------------------
    # Late Delivery Risk
    # --------------------------------------------------------

    risk_summary = (
        filtered_df[
            "Late_delivery_risk"
        ]
        .value_counts()
        .sort_index()
        .reset_index()
    )


    risk_summary.columns = [
        "Risk",
        "Shipments"
    ]


    risk_summary["Risk Label"] = (
        risk_summary["Risk"]
        .map({
            0: "No Observed Late Risk",
            1: "Observed Late Risk"
        })
    )


    col1, col2 = st.columns(2)


    with col1:

        fig = px.pie(
            risk_summary,
            names="Risk Label",
            values="Shipments",
            title="Late Delivery Risk Distribution",
            hole=0.45
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    with col2:

        fig = px.bar(
            risk_summary,
            x="Risk Label",
            y="Shipments",
            text="Shipments",
            title="Late Delivery Risk Exposure"
        )

        fig.update_traces(
            textposition="outside"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # --------------------------------------------------------
    # Delay Gap Distribution
    # --------------------------------------------------------

    st.subheader(
        "Delay Gap Distribution"
    )


    delay_distribution = (
        filtered_df
        .groupby("Delay Gap")
        .size()
        .reset_index(
            name="Shipments"
        )
        .sort_values("Delay Gap")
    )


    fig = px.bar(
        delay_distribution,
        x="Delay Gap",
        y="Shipments",
        text="Shipments",
        title="Shipment Distribution by Delay Gap"
    )


    fig.update_layout(
        xaxis_title="Delay Gap (Days)",
        yaxis_title="Number of Shipments"
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # --------------------------------------------------------
    # Delayed Shipment Severity
    # --------------------------------------------------------

    st.subheader(
        "Delayed Shipment Severity"
    )


    severity_data = filtered_df[
        filtered_df["Delay Gap"] > 0
    ].copy()


    if not severity_data.empty:

        severity_summary = (
            severity_data
            .groupby("Delay Gap")
            .size()
            .reset_index(
                name="Delayed Shipments"
            )
        )


        severity_summary["Severity"] = (
            severity_summary["Delay Gap"]
            .apply(
                lambda x:
                "Minor Delay"
                if x == 1
                else
                "Moderate Delay"
                if x == 2
                else
                "Severe Delay"
            )
        )


        fig = px.bar(
            severity_summary,
            x="Delay Gap",
            y="Delayed Shipments",
            color="Severity",
            text="Delayed Shipments",
            title="Delay Severity Distribution"
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


    else:

        st.info(
            "No delayed shipments exist for the selected filters."
        )


    # --------------------------------------------------------
    # Important Interpretation
    # --------------------------------------------------------

    st.info(
        """
        **Important:** `Late_delivery_risk` in this dataset exactly
        mirrors the observed delayed-delivery status. Therefore it is
        treated as an observed risk/exposure indicator, not as an
        independent predictive model.
        """
    )


# ============================================================
# TAB 3
# SHIPPING MODE
# ============================================================

with tab_shipping:

    st.header("🚚 Shipping Mode Analysis")


    # --------------------------------------------------------
    # Shipping Mode Summary
    # --------------------------------------------------------

    mode_summary = (
        filtered_df
        .groupby("Shipping Mode")
        .agg(
            Total_Shipments=(
                "Shipping Mode",
                "size"
            ),
            Delayed=(
                "Delivery Performance",
                lambda x:
                (x == "Delayed").sum()
            ),
            On_Time=(
                "Delivery Performance",
                lambda x:
                (x == "On-Time").sum()
            ),
            Early=(
                "Delivery Performance",
                lambda x:
                (x == "Early").sum()
            ),
            Canceled=(
                "Delivery Performance",
                lambda x:
                (x == "Canceled").sum()
            )
        )
        .reset_index()
    )


    mode_summary["Non_Canceled"] = (
        mode_summary["Total_Shipments"]
        - mode_summary["Canceled"]
    )


    mode_summary["Delay_Rate_%"] = (
        mode_summary["Delayed"]
        / mode_summary["Non_Canceled"]
        * 100
    )


    mode_summary["On_Time_Rate_%"] = (
        mode_summary["On_Time"]
        / mode_summary["Non_Canceled"]
        * 100
    )


    mode_summary["Efficiency_Index"] = (
        mode_summary["On_Time_Rate_%"]
        - mode_summary["Delay_Rate_%"]
    )


    # --------------------------------------------------------
    # Delay Rate
    # --------------------------------------------------------

    col1, col2 = st.columns(2)


    with col1:

        fig = px.bar(
            mode_summary.sort_values(
                "Delay_Rate_%",
                ascending=False
            ),
            x="Shipping Mode",
            y="Delay_Rate_%",
            text="Delay_Rate_%",
            title="Delay Rate by Shipping Mode"
        )

        fig.update_traces(
            texttemplate="%{text:.2f}%",
            textposition="outside"
        )

        fig.update_layout(
            yaxis_title="Delay Rate (%)"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    with col2:

        fig = px.bar(
            mode_summary.sort_values(
                "On_Time_Rate_%",
                ascending=False
            ),
            x="Shipping Mode",
            y="On_Time_Rate_%",
            text="On_Time_Rate_%",
            title="On-Time Rate by Shipping Mode"
        )

        fig.update_traces(
            texttemplate="%{text:.2f}%",
            textposition="outside"
        )

        fig.update_layout(
            yaxis_title="On-Time Rate (%)"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # --------------------------------------------------------
    # Efficiency Index
    # --------------------------------------------------------

    st.subheader(
        "Shipping Mode Efficiency Index"
    )


    st.caption(
        """
        Efficiency Index = On-Time Rate − Delay Rate.
        This is a project-specific diagnostic index, not a standard
        industry KPI. Higher values indicate better observed delivery
        balance.
        """
    )


    fig = px.bar(
        mode_summary.sort_values(
            "Efficiency_Index"
        ),
        x="Shipping Mode",
        y="Efficiency_Index",
        text="Efficiency_Index",
        title="Shipping Mode Efficiency"
    )


    fig.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside"
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # --------------------------------------------------------
    # Mode Table
    # --------------------------------------------------------

    st.subheader(
        "Shipping Mode Performance Table"
    )


    display_mode = mode_summary.copy()


    for column in [
        "Delay_Rate_%",
        "On_Time_Rate_%",
        "Efficiency_Index"
    ]:

        display_mode[column] = (
            display_mode[column]
            .round(2)
        )


    st.dataframe(
        display_mode,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# TAB 4
# REGIONAL & MARKET
# ============================================================

with tab_region:

    st.header("🌍 Regional & Market Analysis")


    # --------------------------------------------------------
    # Regional Analysis
    # --------------------------------------------------------

    regional_summary = (
        filtered_df
        .groupby("Order Region")
        .agg(
            Total_Shipments=(
                "Order Region",
                "size"
            ),
            Delayed=(
                "Delivery Performance",
                lambda x:
                (x == "Delayed").sum()
            ),
            On_Time=(
                "Delivery Performance",
                lambda x:
                (x == "On-Time").sum()
            ),
            Early=(
                "Delivery Performance",
                lambda x:
                (x == "Early").sum()
            ),
            Canceled=(
                "Delivery Performance",
                lambda x:
                (x == "Canceled").sum()
            ),
            Average_Delay_Gap=(
                "Delay Gap",
                "mean"
            )
        )
        .reset_index()
    )


    regional_summary["Non_Canceled"] = (
        regional_summary["Total_Shipments"]
        - regional_summary["Canceled"]
    )


    regional_summary["Delay_Rate_%"] = (
        regional_summary["Delayed"]
        / regional_summary["Non_Canceled"]
        * 100
    )


    regional_summary["On_Time_Rate_%"] = (
        regional_summary["On_Time"]
        / regional_summary["Non_Canceled"]
        * 100
    )


    # --------------------------------------------------------
    # Top Regional Risk
    # --------------------------------------------------------

    st.subheader(
        "Regional Delay Risk"
    )


    top_regions = regional_summary.sort_values(
        "Delay_Rate_%",
        ascending=False
    )


    fig = px.bar(
        top_regions.head(15),
        x="Delay_Rate_%",
        y="Order Region",
        orientation="h",
        text="Delay_Rate_%",
        title="Top 15 Regions by Delay Rate"
    )


    fig.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside"
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # --------------------------------------------------------
    # Regional Volume vs Delay Rate
    # --------------------------------------------------------

    st.subheader(
        "Regional Volume vs Delay Rate"
    )


    fig = px.scatter(
        regional_summary,
        x="Total_Shipments",
        y="Delay_Rate_%",
        size="Delayed",
        hover_name="Order Region",
        title="Regional Shipment Volume vs Delay Rate"
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # --------------------------------------------------------
    # Market Analysis
    # --------------------------------------------------------

    st.subheader(
        "Market Performance"
    )


    market_summary = (
        filtered_df
        .groupby("Market")
        .agg(
            Total_Shipments=(
                "Market",
                "size"
            ),
            Delayed=(
                "Delivery Performance",
                lambda x:
                (x == "Delayed").sum()
            ),
            On_Time=(
                "Delivery Performance",
                lambda x:
                (x == "On-Time").sum()
            ),
            Early=(
                "Delivery Performance",
                lambda x:
                (x == "Early").sum()
            ),
            Canceled=(
                "Delivery Performance",
                lambda x:
                (x == "Canceled").sum()
            ),
            Average_Delay_Gap=(
                "Delay Gap",
                "mean"
            )
        )
        .reset_index()
    )


    market_summary["Non_Canceled"] = (
        market_summary["Total_Shipments"]
        - market_summary["Canceled"]
    )


    market_summary["Delay_Rate_%"] = (
        market_summary["Delayed"]
        / market_summary["Non_Canceled"]
        * 100
    )


    market_summary["On_Time_Rate_%"] = (
        market_summary["On_Time"]
        / market_summary["Non_Canceled"]
        * 100
    )


    col1, col2 = st.columns(2)


    with col1:

        fig = px.bar(
            market_summary.sort_values(
                "Delay_Rate_%",
                ascending=False
            ),
            x="Market",
            y="Delay_Rate_%",
            text="Delay_Rate_%",
            title="Market Delay Rate"
        )


        fig.update_traces(
            texttemplate="%{text:.2f}%",
            textposition="outside"
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


    with col2:

        fig = px.bar(
            market_summary.sort_values(
                "On_Time_Rate_%",
                ascending=False
            ),
            x="Market",
            y="On_Time_Rate_%",
            text="On_Time_Rate_%",
            title="Market On-Time Rate"
        )


        fig.update_traces(
            texttemplate="%{text:.2f}%",
            textposition="outside"
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # --------------------------------------------------------
    # Regional Table
    # --------------------------------------------------------

    st.subheader(
        "Regional Performance Table"
    )


    regional_display = regional_summary.copy()


    for column in [
        "Average_Delay_Gap",
        "Delay_Rate_%",
        "On_Time_Rate_%"
    ]:

        regional_display[column] = (
            regional_display[column]
            .round(2)
        )


    st.dataframe(
        regional_display.sort_values(
            "Delay_Rate_%",
            ascending=False
        ),
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# TAB 5
# CUSTOMER SEGMENT
# ============================================================

with tab_segment:

    st.header("👥 Customer Segment Analysis")


    segment_summary = (
        filtered_df
        .groupby("Customer Segment")
        .agg(
            Total_Shipments=(
                "Customer Segment",
                "size"
            ),
            Delayed=(
                "Delivery Performance",
                lambda x:
                (x == "Delayed").sum()
            ),
            On_Time=(
                "Delivery Performance",
                lambda x:
                (x == "On-Time").sum()
            ),
            Early=(
                "Delivery Performance",
                lambda x:
                (x == "Early").sum()
            ),
            Canceled=(
                "Delivery Performance",
                lambda x:
                (x == "Canceled").sum()
            )
        )
        .reset_index()
    )


    segment_summary["Non_Canceled"] = (
        segment_summary["Total_Shipments"]
        - segment_summary["Canceled"]
    )


    segment_summary["Delay_Rate_%"] = (
        segment_summary["Delayed"]
        / segment_summary["Non_Canceled"]
        * 100
    )


    segment_summary["On_Time_Rate_%"] = (
        segment_summary["On_Time"]
        / segment_summary["Non_Canceled"]
        * 100
    )


    # --------------------------------------------------------
    # Segment Delay Rate
    # --------------------------------------------------------

    col1, col2 = st.columns(2)


    with col1:

        fig = px.bar(
            segment_summary,
            x="Customer Segment",
            y="Delay_Rate_%",
            text="Delay_Rate_%",
            title="Delay Rate by Customer Segment"
        )


        fig.update_traces(
            texttemplate="%{text:.2f}%",
            textposition="outside"
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


    with col2:

        fig = px.bar(
            segment_summary,
            x="Customer Segment",
            y="On_Time_Rate_%",
            text="On_Time_Rate_%",
            title="On-Time Rate by Customer Segment"
        )


        fig.update_traces(
            texttemplate="%{text:.2f}%",
            textposition="outside"
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # --------------------------------------------------------
    # Segment Shipment Distribution
    # --------------------------------------------------------

    fig = px.pie(
        segment_summary,
        names="Customer Segment",
        values="Total_Shipments",
        title="Shipment Distribution by Customer Segment",
        hole=0.45
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # --------------------------------------------------------
    # Segment Table
    # --------------------------------------------------------

    st.dataframe(
        segment_summary,
        use_container_width=True,
        hide_index=True
    )


    st.info(
        """
        Customer segment shows relatively small differences in observed
        delay rates. Therefore, segment appears to be a weaker risk
        differentiator than shipping mode.
        """
    )


# ============================================================
# TAB 6
# BUSINESS IMPACT
# ============================================================

with tab_business:

    st.header("💰 Business Impact Analysis")


    # --------------------------------------------------------
    # Business Impact by Delivery Performance
    # --------------------------------------------------------

    business_summary = (
        filtered_df
        .groupby("Delivery Performance")
        .agg(
            Shipments=(
                "Delivery Performance",
                "size"
            ),
            Total_Sales=(
                "Sales",
                "sum"
            ),
            Average_Sales=(
                "Sales",
                "mean"
            ),
            Total_Profit=(
                "Order Profit Per Order",
                "sum"
            ),
            Average_Profit=(
                "Order Profit Per Order",
                "mean"
            ),
            Average_Quantity=(
                "Order Item Quantity",
                "mean"
            ),
            Average_Discount_Rate=(
                "Order Item Discount Rate",
                "mean"
            )
        )
        .reset_index()
    )


    business_summary["Shipment_Share_%"] = (
        business_summary["Shipments"]
        / business_summary["Shipments"].sum()
        * 100
    )


    business_summary["Sales_Share_%"] = (
        business_summary["Total_Sales"]
        / business_summary["Total_Sales"].sum()
        * 100
    )


    # --------------------------------------------------------
    # Sales Exposure
    # --------------------------------------------------------

    col1, col2 = st.columns(2)


    with col1:

        fig = px.bar(
            business_summary.sort_values(
                "Total_Sales",
                ascending=False
            ),
            x="Delivery Performance",
            y="Total_Sales",
            text="Total_Sales",
            title="Total Sales by Delivery Performance"
        )


        fig.update_traces(
            texttemplate="%{text:,.0f}",
            textposition="outside"
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


    with col2:

        fig = px.bar(
            business_summary,
            x="Delivery Performance",
            y="Total_Profit",
            text="Total_Profit",
            title="Total Profit by Delivery Performance"
        )


        fig.update_traces(
            texttemplate="%{text:,.0f}",
            textposition="outside"
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # --------------------------------------------------------
    # Average Profit
    # --------------------------------------------------------

    st.subheader(
        "Average Profit per Shipment"
    )


    fig = px.bar(
        business_summary,
        x="Delivery Performance",
        y="Average_Profit",
        text="Average_Profit",
        title="Average Profit by Delivery Performance"
    )


    fig.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside"
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # --------------------------------------------------------
    # Business Impact Table
    # --------------------------------------------------------

    st.subheader(
        "Business Impact Summary"
    )


    business_display = business_summary.copy()


    for column in [
        "Total_Sales",
        "Average_Sales",
        "Total_Profit",
        "Average_Profit"
    ]:

        business_display[column] = (
            business_display[column]
            .round(2)
        )


    business_display[
        "Shipment_Share_%"
    ] = (
        business_display[
            "Shipment_Share_%"
        ].round(2)
    )


    business_display[
        "Sales_Share_%"
    ] = (
        business_display[
            "Sales_Share_%"
        ].round(2)
    )


    st.dataframe(
        business_display,
        use_container_width=True,
        hide_index=True
    )


    # --------------------------------------------------------
    # Delayed Business Exposure
    # --------------------------------------------------------

    delayed_business = business_summary[
        business_summary[
            "Delivery Performance"
        ] == "Delayed"
    ]


    if not delayed_business.empty:

        delayed_sales = delayed_business[
            "Total_Sales"
        ].iloc[0]

        delayed_sales_share = delayed_business[
            "Sales_Share_%"
        ].iloc[0]


        st.success(
            f"""
            **Delayed shipment exposure:** {delayed_sales_share:.2f}%
            of filtered sales are associated with delayed shipments,
            representing approximately ₹{delayed_sales:,.2f} in sales
            within the dataset's sales units.
            """
        )


    st.warning(
        """
        Business impact results represent associations in the dataset.
        They should not be interpreted as proof that delivery delays
        directly caused changes in sales or profit.
        """
    )


# ============================================================
# DATASET LIMITATION
# ============================================================

st.markdown("---")

st.header("ℹ️ Dataset Limitation")

st.info(
    """
    **Date filter unavailable:** The provided APL Logistics dataset
    does not contain a date field. Therefore, this dashboard does
    not include time-based date filtering or time-series analysis.
    """
)


# ============================================================
# FILTERED DATA DOWNLOAD
# ============================================================

st.markdown("---")

st.header("⬇️ Download Filtered Data")

csv_data = filtered_df.to_csv(
    index=False
).encode("utf-8-sig")


st.download_button(
    label="📥 Download Filtered Dataset",
    data=csv_data,
    file_name="APL_Logistics_Filtered_Data.csv",
    mime="text/csv"
)


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "APL Logistics | Delivery Performance & Delay Risk Analytics"
)

st.caption(
    f"Dashboard currently displaying {len(filtered_df):,} "
    f"of {len(df):,} shipments."
)
