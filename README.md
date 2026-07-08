# 🎯 RecoIQ 2.0 – Enterprise Multi-Tenant Recommendation Intelligence Platform

> **An enterprise-scale recommendation intelligence platform built on Databricks, Apache Spark, MLlib FP-Growth, Item-Based Collaborative Filtering (IBCF), SQL Analytics, and Streamlit.**

---

## 📌 Overview

RecoIQ 2.0 is a multi-tenant recommendation intelligence platform designed to help organizations identify **next-best products**, **cross-selling opportunities**, and **customer growth potential** through explainable recommendation models.

Unlike traditional recommender systems that rely on a single algorithm, RecoIQ evaluates and compares two independent recommendation engines:

* 📈 FP-Growth (Association Rule Mining)
* 🤝 Item-Based Collaborative Filtering (IBCF)

The platform provides complete recommendation explainability, customer intelligence, executive analytics, and interactive dashboards while maintaining strict tenant isolation.

---

# 🚀 Key Features

* Multi-Tenant Architecture
* Enterprise-scale Synthetic Dataset
* Tenant-Isolated Recommendation Engines
* FP-Growth Association Rule Mining
* Item-Based Collaborative Filtering
* Recommendation Intelligence Layer
* Customer 360 Profiles
* Executive Analytics Dashboard
* Product Intelligence
* Segment Intelligence
* Recommendation Explainability
* Interactive Streamlit Dashboard
* Databricks SQL Integration

---

# 🏗 System Architecture

```text
                         ┌─────────────────────────┐
                         │   Synthetic Data Layer  │
                         └─────────────┬───────────┘
                                       │
                                       ▼
                         ┌─────────────────────────┐
                         │ Databricks Delta Tables │
                         └─────────────┬───────────┘
                                       │
          ┌────────────────────────────┼─────────────────────────────┐
          ▼                            ▼                             ▼
  FP-Growth Engine             IBCF Recommendation Engine      Customer Intelligence
          │                            │                             │
          └──────────────┬─────────────┴──────────────┐
                         ▼                            ▼
               Recommendation Intelligence Layer
                         │
                         ▼
                 Analytics Layer
                         │
                         ▼
             Streamlit Executive Dashboard
```

---

# 🏢 Supported Industries

RecoIQ simulates recommendation systems for multiple industries.

| Tenant | Industry  |
| ------ | --------- |
| T001   | Banking   |
| T002   | Insurance |
| T003   | Telecom   |
| T004   | Retail    |

Each tenant maintains:

* Independent customers
* Independent product catalog
* Independent recommendation engines
* Independent analytics

No recommendation crosses tenant boundaries.

---

# 📊 Dataset Scale

| Metric                         |   Value |
| ------------------------------ | ------: |
| Tenants                        |       4 |
| Customers                      |   8,000 |
| Customers per Tenant           |   2,000 |
| Products                       |   1,200 |
| Products per Tenant            |     300 |
| Customer-Product Relationships | ~62,000 |
| Recommendations Generated      | ~80,000 |

---

# 🧠 Recommendation Engines

## 1. FP-Growth

Association rule mining using Apache Spark MLlib.

### Purpose

* Cross-selling
* Customer progression
* Product adoption
* Explainable recommendations

Example

```text
Savings Account + Debit Card
        ↓
Mobile Banking
```

Generated metrics include:

* Support
* Confidence
* Lift
* Rule explanations

---

## 2. Item-Based Collaborative Filtering (IBCF)

Similarity-based recommendation engine.

### Purpose

* Product similarity discovery
* Catalog exploration
* Long-tail recommendations

Generated metrics include:

* Similarity strength
* Supporting products
* Recommendation score

Example

```text
Customers owning

Credit Card

↓

Often own

Travel Card
```

---

# 🧩 Recommendation Intelligence Layer

RecoIQ intentionally **does not create a hybrid recommendation score**.

Instead, FP-Growth and IBCF remain independent and are compared using:

* Customer Coverage
* Product Coverage
* Catalog Utilization
* Recommendation Diversity
* Recommendation Volume
* Recommendation Quality

This enables transparent evaluation of recommendation strategies.

---

# 👤 Customer 360

The Customer 360 module consolidates customer information into a single profile.

Includes:

* Customer demographics
* Portfolio summary
* Customer health score
* Segment
* Risk score
* Engagement score
* FP opportunities
* IBCF opportunities
* Recommendation summary

---

# 📈 Analytics Layer

The analytics layer powers executive reporting.

Generated datasets include:

* KPI Summary
* Recommendation Engine Comparison
* Tenant Performance
* Segment Performance
* Product Recommendation Comparison
* Product Concentration
* Product Coverage
* Customer Coverage
* Recommendation Diversity
* Category Coverage
* Top Opportunity Customers

---

# 📊 Dashboard Modules

The Streamlit dashboard includes:

### Executive Overview

* Total Customers
* Total Recommendations
* Customer Coverage
* Product Coverage
* Catalog Utilization

---

### Recommendation Engine Comparison

Compare:

* FP-Growth
* IBCF

Across:

* Recommendation volume
* Coverage
* Diversity
* Utilization

---

### Tenant Intelligence

Per-tenant analysis including:

* Recommendations
* Customer health
* Opportunities
* Coverage

---

### Segment Intelligence

Analyze recommendation performance by customer segment.

---

### Product Intelligence

Visualize:

* Most recommended products
* Product concentration
* Category coverage
* Recommendation distribution

---

### Customer 360 Explorer

Interactive drill-down into:

* Customer profile
* Portfolio
* Recommendation history
* Explainability

---

### Top Opportunity Customers

Identify customers with the highest cross-selling potential.

---

# 🗄 Database

Database:

```text
recoiq_2_0
```

Key tables:

```text
tenants
products
customers
customer_products

fp_filtered_rules
fp_top_recommendations

ibcf_item_similarity
ibcf_top_recommendations

customer_360_profile
customer_recommendation_view
customer_recommendation_intelligence

recommendation_engine_comparison
recommendation_summary

tenant_performance
segment_performance

catalog_utilization
product_concentration

recommendation_diversity_metrics

top_opportunity_customers
```

---

# 🛠 Technology Stack

### Big Data

* Apache Spark
* Spark SQL
* Databricks

### Machine Learning

* Spark MLlib FP-Growth
* Item-Based Collaborative Filtering

### Backend

* Python
* Pandas

### Visualization

* Streamlit
* Plotly

### Storage

* Delta Tables

---

# 📂 Project Structure

```text
RecoIQ-2.0/

│
├── notebooks/
│   ├── 01_data_validation.ipynb
│   ├── 02_data_ingestion.ipynb
│   ├── 03_multitenant_fp_growth.ipynb
│   ├── 04_multitenant_ibcf.ipynb
│   ├── 05_recommendation_intelligence.ipynb
│   ├── 06_customer_360.ipynb
│   ├── 07_analytics_layer.ipynb
│   └── 08_streamlit_dashboard.ipynb
│
├── streamlit/
│   ├── app.py
│   ├── app.yml
│   └── requirements.txt
│
├── datasets/
│
├── documentation/
│
└── README.md
```

---

# 🚀 Running the Project

## 1. Clone the repository

```bash
git clone https://github.com/<username>/RecoIQ-2.0.git
```

---

## 2. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 3. Prepare Databricks

* Create the `recoiq_2_0` database.
* Run the notebooks in numerical order.
* Verify all analytics tables are generated.

---

## 4. Configure Streamlit

Provide access to your Databricks SQL Warehouse (or your chosen deployment method).

---

## 5. Launch the dashboard

```bash
streamlit run app.py
```

---

# 📌 Project Status

| Module                      |     Status     |
| --------------------------- | :------------: |
| Data Validation             |        ✅       |
| Data Ingestion              |        ✅       |
| FP-Growth Engine            |        ✅       |
| IBCF Engine                 |        ✅       |
| Recommendation Intelligence |        ✅       |
| Customer 360                |        ✅       |
| Analytics Layer             |        ✅       |
| Streamlit Dashboard         | 🚧 In Progress |
| Deployment                  | 🚧 In Progress |

---

# 🔮 Future Enhancements

* Real-time recommendation generation
* User authentication and RBAC
* Recommendation feedback loop
* Model performance monitoring
* A/B testing of recommendation strategies
* REST API integration
* Automated retraining pipelines
* Cloud-native CI/CD deployment
* LLM-powered recommendation explanations
* Multi-language dashboard support

---

# 📄 License

This project is intended for educational, research, and portfolio purposes. You are free to fork, study, and extend it with appropriate attribution.

---

# 👨‍💻 Author

**Pradhi Raj**

If you found this project useful, consider giving it a ⭐ on GitHub.
