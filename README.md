# 🚚 APL Logistics Delivery Performance & Delay Risk Analytics

## 📌 Project Overview

**APL Logistics Delivery Performance & Delay Risk Analytics** is an end-to-end data analytics project focused on evaluating delivery performance, identifying major delay drivers, analyzing shipping-mode efficiency, and understanding the business impact of delayed shipments in global supply-chain operations.

The project analyzes **180,519 shipment records** to answer a central business question:

> **Where are delivery delays occurring, which operational factors are associated with those delays, and where should logistics teams prioritize improvement efforts?**

The analysis focuses on delivery performance, delay severity, shipping modes, regions, markets, customer segments, product categories, departments, and financial impact.

An interactive **Streamlit dashboard** was also developed to allow users to dynamically filter and explore the shipment data.

---

## 🎯 Business Problem

In large-scale logistics operations, delivery delays can lead to:

- SLA violations
- Customer dissatisfaction
- Increased operational costs
- Poor shipping-mode selection
- Regional bottlenecks
- Reduced service reliability
- Difficulty identifying high-risk operational areas
- Reactive rather than proactive logistics management

A logistics organization needs to understand not only **how many shipments are delayed**, but also:

1. Which shipping modes have the highest delay rates?
2. Which regions and markets experience higher delivery risk?
3. How severe are the delays?
4. Which factors are strong or weak differentiators?
5. What is the business impact of delayed shipments?
6. Which operational areas should be prioritized for improvement?

This project addresses these questions through exploratory data analysis, feature engineering, aggregation, visualization, and an interactive dashboard.

---

# 🏢 Business Context

The project is based on a supply-chain/logistics analytics scenario involving **APL Logistics**.

APL Logistics operates across multiple markets, regions, customers, products, and transportation/shipping modes. With a large number of shipment records, manual analysis becomes difficult.

The objective of this project is therefore to transform shipment-level operational data into actionable business insights.

---

# 📊 Dataset

The dataset contains **180,519 shipment/order records** and **40 columns**.

### Dataset characteristics

| Attribute | Value |
|---|---:|
| Total Records | 180,519 |
| Total Columns | 40 |
| Duplicate Rows | 0 |
| Date Column | Not available |
| Shipping Modes | 4 |
| Markets | 5 |
| Regions | 23 |
| Product Categories | 55 |
| Customer Segments | 3 |

### Important dataset columns

The dataset contains information related to:

- Shipping performance
- Scheduled vs actual shipping duration
- Delivery status
- Late delivery risk
- Customer information
- Product information
- Order information
- Market
- Region
- Shipping mode
- Sales
- Profit
- Quantity
- Discounts
- Geographic coordinates

### Major fields

```text
Days for shipping (real)
Days for shipment (scheduled)
Delivery Status
Late_delivery_risk
Shipping Mode
Market
Order Region
Customer Segment
Category Name
Department Name
Sales
Order Item Total
Order Profit Per Order
Order Item Quantity
Order Item Discount
Order Item Profit Ratio
```

---

# ⚠️ Dataset Limitation

The dataset **does not contain a date/time field**.

Therefore:

- Date-based filtering is not available.
- Monthly delivery trends cannot be calculated.
- Year-over-year performance cannot be analyzed.
- Seasonal delay patterns cannot be evaluated.
- Time-series forecasting cannot be performed from this dataset alone.

The dashboard therefore focuses on **operational dimensions** such as shipping mode, region, market, customer segment, and delivery performance.

---

# 🗂️ Project Structure

```text
APL_Logistics_Project/
│
├── 01_Raw_Data/
│   └── APL_Logistics.csv
│
├── 02_Notebooks/
│   └── APL_Logistics_Analysis.ipynb
│
├── 03_Cleaned_Data/
│   └── APL_Logistics_Cleaned.csv
│
├── 04_Analysis/
│   ├── APL_Logistics_Analysis.csv
│   ├── Shipping_Mode_Analysis.csv
│   ├── Shipping_Mode_Deep_Dive.csv
│   ├── Regional_Analysis.csv
│   ├── Market_Analysis.csv
│   ├── Market_Shipping_Mode_Analysis.csv
│   ├── Region_Shipping_Mode_Analysis.csv
│   ├── Customer_Segment_Analysis.csv
│   ├── Delay_Severity_Distribution.csv
│   ├── Category_Analysis.csv
│   ├── Department_Analysis.csv
│   ├── Business_Impact_Analysis.csv
│   ├── Final_Risk_Driver_Summary.csv
│   ├── Viz_Delivery_Performance.csv
│   ├── Viz_Delay_Gap_Distribution.csv
│   ├── Viz_Shipping_Mode.csv
│   ├── Viz_Regional_Performance.csv
│   ├── Viz_Market_Performance.csv
│   ├── Viz_Customer_Segment.csv
│   ├── Viz_Delay_Severity.csv
│   └── Viz_Business_Impact.csv
│
├── 05_Visualizations/
│
├── 06_Streamlit_App/
│   └── app.py
│
├── 07_Project_Documentation/
│
└── README.md
```

---

# 🧹 Data Cleaning

The raw dataset was inspected and cleaned before analysis.

### Cleaning activities performed

#### 1. Duplicate check

The dataset contained:

```text
Duplicate rows = 0
```

Therefore, no duplicate records were removed.

#### 2. Missing Customer Last Name

The `Customer Lname` column contained missing values.

These values were replaced with:

```text
Unknown
```

This prevents unnecessary loss of records while clearly identifying unavailable information.

#### 3. Customer Zipcode

Three records contained missing customer zipcodes.

These values were **not artificially generated or guessed**.

They were retained as missing values.

#### 4. Text standardization

Whitespace inconsistencies were cleaned from fields such as:

- Department Name
- Order Region

#### 5. Negative profit values

Negative profit values were retained because they can represent legitimate loss-making transactions.

They were not treated as data-entry errors.

---

# ⚙️ Feature Engineering

A major derived variable used in the analysis is the **Delay Gap**.

```python
df["Delay Gap"] = (
    df["Days for shipping (real)"]
    - df["Days for shipment (scheduled)"]
)
```

### Interpretation

```text
Delay Gap < 0  → Shipment arrived earlier than scheduled
Delay Gap = 0  → Shipment was on time
Delay Gap > 0  → Shipment was delayed
```

For example:

| Actual | Scheduled | Delay Gap | Interpretation |
|---:|---:|---:|---|
| 2 | 4 | -2 | Early |
| 3 | 3 | 0 | On-Time |
| 4 | 3 | +1 | Delayed |
| 6 | 2 | +4 | Severely Delayed |

---

# 🚦 Delivery Performance Classification

A new `Delivery Performance` classification was created.

```python
df["Delivery Performance"] = "On-Time"

df.loc[
    df["Delivery Status"] == "Shipping canceled",
    "Delivery Performance"
] = "Canceled"

df.loc[
    (df["Delay Gap"] < 0) &
    (df["Delivery Status"] != "Shipping canceled"),
    "Delivery Performance"
] = "Early"

df.loc[
    (df["Delay Gap"] > 0) &
    (df["Delivery Status"] != "Shipping canceled"),
    "Delivery Performance"
] = "Delayed"
```

This produced four operational categories:

- Delayed
- Early
- On-Time
- Canceled

---

# 📈 Executive KPI Summary

The dataset contains:

| KPI | Value |
|---|---:|
| Total Shipments | 180,519 |
| Delayed Shipments | 98,977 |
| On-Time Shipments | 32,196 |
| Early Shipments | 41,592 |
| Canceled Shipments | 7,754 |
| Overall Delay Rate | 57.29% |
| On-Time Rate among Non-Canceled | 18.64% |
| Early Rate among Non-Canceled | 24.07% |
| Cancellation Rate | 4.30% |
| Average Overall Delay Gap | 0.57 days |
| Average Delay When Delayed | 1.62 days |

### Key observation

More than half of all shipments were classified as delayed.

This makes delivery performance the primary operational issue identified in the dataset.

---

# ⏱️ Delay Gap Analysis

The distribution of delay gaps was:

| Delay Gap | Shipments | Share |
|---:|---:|---:|
| -2 days | 21,666 | 12.00% |
| -1 day | 21,700 | 12.02% |
| 0 days | 33,753 | 18.70% |
| +1 day | 60,647 | 33.60% |
| +2 days | 28,718 | 15.91% |
| +3 days | 7,052 | 3.91% |
| +4 days | 6,983 | 3.87% |

### Important finding

The most common delay is **+1 day**, representing approximately **33.60% of all shipments**.

Among delayed shipments:

- 1–2 day delays account for approximately **86.42%**
- 3–4 day delays account for approximately **13.57%**

This suggests that the majority of delays are relatively small, but a meaningful minority experience more severe delays.

---

# 🚢 Shipping Mode Analysis

Four shipping modes were analyzed:

| Shipping Mode | Shipments | Share |
|---|---:|---:|
| Standard Class | 107,752 | 59.69% |
| Second Class | 35,216 | 19.51% |
| First Class | 27,814 | 15.41% |
| Same Day | 9,737 | 5.39% |

---

## Shipping Mode Performance

| Shipping Mode | Delay Rate | On-Time Rate |
|---|---:|---:|
| First Class | 95.32% | 0.00% |
| Second Class | 76.63% | 20.17% |
| Same Day | 47.93% | 52.07% |
| Standard Class | 39.77% | 19.91% |

### Major finding

**Shipping mode is the strongest differentiating operational factor identified in the analysis.**

The delay-rate range between the best and worst modes is approximately:

```text
100% - 39.77% = 60.23 percentage points
```

This is substantially larger than the differences observed across markets and customer segments.

---

# 📊 Shipping Mode Efficiency Index

A project-specific diagnostic metric was created:

```text
Efficiency Index =
On-Time Rate - Delay Rate
```

Higher values indicate relatively better delivery performance.

| Shipping Mode | Efficiency Index |
|---|---:|
| Same Day | +4.14 |
| Standard Class | -19.86 |
| Second Class | -59.66 |
| First Class | -100.00 |

> **Note:** This is a project-specific diagnostic metric and is not presented as a standard logistics industry KPI.

---

# 🌍 Regional Analysis

The dataset contains **23 order regions**.

Regional analysis was performed using:

- Shipment volume
- Delay rate
- On-time rate
- Cancellation rate
- Late-delivery risk
- Risk contribution

### Highest observed regional delay-risk areas

Some of the highest regional risk rates were observed in:

1. Central Africa
2. South Asia
3. East Africa
4. Western Europe
5. South of USA
6. East of USA
7. Eastern Europe
8. Southeast Asia
9. Central Asia
10. West Asia

### Important consideration

A high percentage alone does not necessarily mean the region has the largest operational burden.

For example, **Central Africa** had a high delay rate but relatively low shipment volume.

Therefore, both:

```text
Risk Rate
+
Shipment Volume
```

should be considered when prioritizing operational improvements.

---

# 🎯 Risk Concentration

Risk contribution was also analyzed.

### Top risk contributors

| Region | Risk Shipments | Risk Contribution |
|---|---:|---:|
| Central America | 15,518 | 15.68% |
| Western Europe | 15,140 | 15.30% |
| South America | 8,111 | 8.19% |

The top three regions together contribute approximately:

```text
39.17% of all risk shipments
```

Central America and Western Europe alone account for approximately:

```text
30.98%
```

of risk shipments.

This makes these regions important candidates for operational investigation.

---

# 🌐 Market Analysis

Five markets were analyzed:

| Market | Shipments | Delay Rate |
|---|---:|---:|
| Europe | 50,252 | 57.69% |
| USCA | 25,799 | 57.41% |
| Pacific Asia | 41,260 | 57.38% |
| LATAM | 51,594 | 56.87% |
| Africa | 11,614 | 56.84% |

### Key finding

Market-level delay rates are highly similar.

The difference between the highest and lowest market delay rates is only approximately:

```text
57.69% - 56.84% = 0.85 percentage points
```

Therefore, **market is a weak differentiator of delivery delays** compared with shipping mode.

---

# 👥 Customer Segment Analysis

Three customer segments were analyzed:

- Consumer
- Corporate
- Home Office

| Segment | Shipments | Delay Rate |
|---|---:|---:|
| Consumer | 93,504 | 57.31% |
| Corporate | 54,789 | 57.08% |
| Home Office | 32,226 | 57.59% |

The range is only:

```text
57.59% - 57.08% = 0.51 percentage points
```

### Conclusion

Customer segment has a **weak relationship with delivery delay performance** in this dataset.

---

# 🛍️ Product Category Analysis

The dataset contains **55 product categories**.

Observed category delay rates ranged from approximately:

```text
49.27% to 68.85%
```

This represents a range of:

```text
19.58 percentage points
```

Category therefore shows a **moderate differentiating effect**.

However, category-level extremes should be interpreted carefully because some categories have relatively smaller shipment volumes.

---

# 🏢 Department Analysis

Department-level delay rates were also analyzed.

The observed range was approximately:

```text
56.77% to 61.44%
```

A few departments with comparatively higher delay rates include:

- Pet Shop
- Book Shop
- Health & Beauty
- Fitness
- Outdoors
- Technology

However, the total range is only approximately:

```text
4.67 percentage points
```

Therefore, department is considered a **weak differentiator** compared with shipping mode.

---

# 💰 Business Impact Analysis

Delayed shipments were analyzed from a business-impact perspective.

### Delayed shipments

```text
Delayed shipments = 98,977
```

### Sales associated with delayed shipments

```text
20,126,394.88
```

### Share of total sales

Approximately:

```text
54.71%
```

of observed sales were associated with delayed shipments.

### Profit

Total profit associated with delayed shipments:

```text
2,140,051.68
```

Average profit per delayed shipment:

```text
21.62
```

The analysis is **associational** and does not establish that delays caused the observed financial outcomes.

---

# 🧠 Final Risk Driver Analysis

The major operational dimensions were compared based on their observed delay-rate range.

| Driver | Observed Range | Assessment |
|---|---:|---|
| Shipping Mode | 60.23 pp | 🔴 Strong |
| Category | 19.58 pp | 🟠 Moderate |
| Department | 4.67 pp | 🟡 Weak |
| Market | 0.85 pp | 🟢 Weak |
| Customer Segment | 0.51 pp | 🟢 Weak |

### Priority order

```text
Shipping Mode
      ↓
Product Category
      ↓
Department
      ↓
Market
      ↓
Customer Segment
```

This prioritization indicates that logistics teams should investigate **shipping-mode selection and operational execution first**, before focusing heavily on customer-segment or market-level differences.

---

# 🔍 Key Business Insights

## 1. Delivery delay is the dominant issue

Approximately **57.29% of non-canceled shipments were delayed**.

This indicates a significant delivery-performance challenge.

---

## 2. Shipping mode is the strongest differentiator

Shipping mode shows a much larger difference in delay rates than:

- Market
- Customer segment
- Department

First Class and Second Class show particularly high delay rates in this dataset.

---

## 3. Same Day performs relatively better

Same Day had:

```text
Delay Rate = 47.93%
On-Time Rate = 52.07%
```

It is the only mode where the observed on-time rate exceeds the delay rate.

---

## 4. Most delays are relatively short

Approximately **86.42% of delayed shipments were delayed by only 1–2 days**.

This suggests that improving operational processes around small schedule deviations may have a substantial overall impact.

---

## 5. Severe delays still require attention

Shipments delayed by 3–4 days represent approximately **13.57% of delayed shipments**.

These cases may represent higher operational risk and should be investigated separately.

---

## 6. Market differences are relatively small

The five markets have delay rates clustered within approximately **0.85 percentage points**.

Therefore, market alone does not explain much of the observed delay variation.

---

## 7. Risk is concentrated geographically

Central America and Western Europe together contribute approximately **30.98% of risk shipments**.

This makes them useful targets for deeper operational investigation.

---

## 8. Customer segment is not a major differentiator

Consumer, Corporate, and Home Office segments have very similar delay rates.

Therefore, customer segment should not be the first priority for delay-reduction initiatives.

---

# 💡 Business Recommendations

## Recommendation 1: Review Shipping Mode Allocation

Because shipping mode is the strongest observed differentiator, logistics teams should investigate:

- Shipping-mode assignment rules
- Capacity availability
- Carrier performance
- Route suitability
- Service-level expectations
- Handover processes
- Mode-specific bottlenecks

---

## Recommendation 2: Investigate Second Class Operations

Second Class shows a high delay rate and a high severe-delay rate.

Particular attention should be given to:

- Routes using Second Class
- Regions with high Second Class delay rates
- Carrier-level performance
- Scheduled delivery assumptions
- Capacity constraints

---

## Recommendation 3: Investigate First Class Anomaly

First Class shows an unusually high delay rate in the dataset.

Before making operational decisions, the organization should validate:

- Data definitions
- Shipping-mode mapping
- Service-level rules
- Carrier assignment
- Business process interpretation

This is especially important because the result is counterintuitive for a premium shipping category.

---

## Recommendation 4: Prioritize High-Volume High-Risk Regions

Regional prioritization should consider both:

```text
Risk Rate × Shipment Volume
```

rather than looking only at the highest percentage.

Central America and Western Europe are important examples.

---

## Recommendation 5: Reduce 1-Day Delays

Since +1 day is the largest delay-gap category, even a small improvement in this category could potentially affect a large number of shipments.

Operational teams could investigate:

- Warehouse processing time
- Carrier handoff
- Order release timing
- Transportation scheduling
- Last-mile coordination

---

## Recommendation 6: Separate Severe Delays from Minor Delays

A dashboard should distinguish:

```text
Minor Delay     → +1 day
Moderate Delay  → +2 days
Severe Delay    → +3 to +4 days
```

This helps management focus resources on high-impact cases.

---

# 📊 Interactive Streamlit Dashboard

An interactive dashboard was developed using **Streamlit**.

The dashboard provides dynamic filtering and KPI analysis.

### Dashboard filters

Users can filter the dataset using:

- 🚚 Shipping Mode
- 🌍 Order Region
- 🌐 Market
- 👥 Customer Segment

The dashboard dynamically recalculates KPIs and visualizations based on the selected filters.

---

# 📈 Dashboard Sections

## Executive Overview

Displays:

- Total Shipments
- Delay Rate
- On-Time Rate
- Average Delay
- Cancellation Rate
- Delayed Shipment Count
- On-Time Shipment Count

---

## Delivery Performance

Visualizes:

- Delayed shipments
- Early shipments
- On-time shipments
- Canceled shipments

---

## Delay Risk

Analyzes:

- Late delivery risk
- Delay severity
- Delay-gap distribution
- Risk concentration

---

## Shipping Mode

Compares:

- Shipment volume
- Delay rate
- On-time rate
- Shipping-mode efficiency

---

## Regional & Market Analysis

Provides:

- Regional performance
- Market performance
- High-risk regions
- Risk contribution

---

## Customer Segment

Compares delivery performance across:

- Consumer
- Corporate
- Home Office

---

## Business Impact

Analyzes:

- Sales
- Profit
- Shipment volume
- Delayed shipment contribution

---

# 🛠️ Technologies Used

### Programming

- Python

### Data Analysis

- Pandas
- NumPy

### Visualization

- Plotly
- Matplotlib

### Dashboard

- Streamlit

### Development Environment

- Jupyter Notebook
- VS Code

### Version Control

- Git
- GitHub

---

# 🔄 End-to-End Workflow

```text
Raw Dataset
     ↓
Data Understanding
     ↓
Data Quality Checks
     ↓
Data Cleaning
     ↓
Feature Engineering
     ↓
Delivery Performance Classification
     ↓
Exploratory Data Analysis
     ↓
Shipping Mode Analysis
     ↓
Regional & Market Analysis
     ↓
Delay Severity Analysis
     ↓
Category & Department Analysis
     ↓
Business Impact Analysis
     ↓
Risk Driver Identification
     ↓
Visualization Tables
     ↓
Streamlit Dashboard
     ↓
Business Recommendations
```

---

# 📁 Important Output Files

### Cleaned dataset

```text
03_Cleaned_Data/
└── APL_Logistics_Cleaned.csv
```

### Main analysis dataset

```text
04_Analysis/
└── APL_Logistics_Analysis.csv
```

### Shipping analysis

```text
Shipping_Mode_Analysis.csv
Shipping_Mode_Deep_Dive.csv
Region_Mode_Severity.csv
Delivery_Status_Shipping_Mode.csv
```

### Regional and market analysis

```text
Regional_Analysis.csv
Market_Analysis.csv
Market_Shipping_Mode_Analysis.csv
Region_Shipping_Mode_Analysis.csv
Regional_Risk_Diagnostics.csv
Regional_Risk_Priority.csv
Regional_Risk_Concentration.csv
```

### Delay analysis

```text
Delay_Severity_Distribution.csv
Viz_Delay_Gap_Distribution.csv
```

### Business analysis

```text
Business_Impact_Analysis.csv
Viz_Business_Impact.csv
```

### Risk analysis

```text
Final_Risk_Driver_Summary.csv
```

---

# ▶️ How to Run the Streamlit Dashboard

## 1. Clone the repository

```bash
git clone https://github.com/swapnilsapkal/APL-Logistics-Delivery-Performance-Analytics.git
```

## 2. Navigate into the project

```bash
cd APL-Logistics-Delivery-Performance-Analytics
```

## 3. Install required libraries

```bash
pip install pandas numpy plotly streamlit
```

## 4. Run the application

```bash
streamlit run 06_Streamlit_App/app.py
```

The dashboard will open in your browser.

---

# 🧪 Example Analytical Questions Answered

This project answers questions such as:

### Delivery Performance

- What percentage of shipments are delayed?
- How many shipments are on time?
- How many shipments were canceled?
- What is the average delay?

### Shipping Mode

- Which shipping mode has the highest delay rate?
- Which shipping mode performs relatively better?
- Which modes experience severe delays?

### Geography

- Which regions have high delay risk?
- Which regions contribute the largest number of delayed shipments?
- Are market-level differences significant?

### Customer

- Does customer segment affect delivery performance?
- Which customer segment has the highest delay rate?

### Products

- Which categories show higher delay rates?
- Are department-level differences significant?

### Business

- How much sales are associated with delayed shipments?
- What is the profit associated with delayed shipments?
- Which operational factors should management prioritize?

---

# ⚠️ Important Analytical Considerations

## Late Delivery Risk Is Not a Prediction

The `Late_delivery_risk` field was compared with actual delivery performance.

In this dataset, the risk label aligns directly with delayed shipments.

Therefore, it should be treated as an **observed/derived label**, not as an independent predictive model output.

A future machine-learning project could instead predict delay risk **before shipment completion** using variables available at order/shipment initiation.

---

## Correlation Does Not Mean Causation

The analysis identifies associations between delivery performance and operational dimensions.

For example:

> Shipping mode is strongly associated with observed delay rates.

This does **not automatically prove that shipping mode causes delays**.

Further operational investigation would be required to establish causality.

---

# 🚀 Future Improvements

Several extensions could make this project more advanced.

## 1. Machine Learning Delay Prediction

Build a model to predict whether a shipment is likely to be delayed.

Possible algorithms:

- Logistic Regression
- Decision Tree
- Random Forest
- XGBoost
- LightGBM

---

## 2. Predict Delay Severity

Instead of binary prediction:

```text
Delayed / Not Delayed
```

predict:

```text
0 = On-Time
1 = 1 Day Late
2 = 2 Days Late
3 = 3 Days Late
4 = 4 Days Late
```

---

## 3. Carrier-Level Analysis

If carrier information becomes available, analyze:

- Carrier delay rate
- Carrier reliability
- Carrier-region interaction
- Carrier-shipping-mode performance

---

## 4. Time-Series Analysis

If shipment dates become available, analyze:

- Monthly delay trends
- Seasonal patterns
- Year-over-year performance
- Peak-period bottlenecks
- Forecasted delivery demand

---

## 5. Route-Level Analysis

Analyze:

```text
Origin → Destination
```

to identify problematic transportation routes.

---

## 6. Automated Alert System

Build a monitoring system that flags:

```text
High-risk region
        ↓
High-risk shipping mode
        ↓
High-risk shipment
        ↓
Operational alert
```

This would move the project from **descriptive analytics** toward **predictive and prescriptive analytics**.

---

# 📌 Project Outcome

The project transformed raw shipment-level data into a structured logistics analytics solution.

The analysis identified:

- High overall delivery-delay levels
- Shipping mode as the strongest differentiating factor
- Second Class as a high-risk mode
- First Class as an anomalous high-delay category requiring validation
- 1-day delays as the most common delay pattern
- Significant risk concentration in selected regions
- Relatively small market-level differences
- Weak customer-segment differentiation
- Meaningful sales exposure associated with delayed shipments

The resulting dashboard provides management with an interactive way to investigate delivery performance and identify operational areas requiring deeper attention.

---

# 👨‍💻 Author

**Swapnil Sapkal**

B.Tech Computer Science & Engineering  
**Data Science**

### Areas of Interest

- Data Analytics
- Business Intelligence
- SQL
- Python
- Power BI
- Data Visualization
- Machine Learning
- Supply Chain Analytics

---

# ⭐ If You Find This Project Useful

If you find this project useful or interesting, consider giving the repository a ⭐ on GitHub.

---

## 📜 License

This project is licensed under the **MIT License**.
