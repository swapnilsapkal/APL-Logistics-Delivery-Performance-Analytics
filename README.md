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

A new `Delivery Performance` classification was created
