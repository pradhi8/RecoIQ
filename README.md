# RecoIQ 2.0

## Overview

RecoIQ 2.0 is a **multi-tenant recommendation intelligence platform**
built on **Databricks, Apache Spark, and Streamlit**. It generates
explainable product recommendations by combining **FP-Growth Association
Rule Mining** and **Item-Based Collaborative Filtering (IBCF)** while
maintaining complete tenant isolation.

The platform demonstrates an end-to-end data engineering and machine
learning workflow---from synthetic data generation and ingestion through
recommendation engines, analytics, explainability, and interactive
dashboards.

------------------------------------------------------------------------

## Features

-   Multi-tenant architecture (Banking, Insurance, Telecom, Retail)
-   Tenant-isolated recommendation pipelines
-   FP-Growth recommendation engine
-   Item-Based Collaborative Filtering (IBCF)
-   Recommendation Intelligence layer
-   Customer 360 profiles
-   Explainable recommendations
-   Executive dashboards
-   Segment, Product, Diversity and Customer analytics
-   Databricks SQL Warehouse integration
-   Streamlit web application

------------------------------------------------------------------------

## Tech Stack

### Data Engineering

-   Databricks
-   Apache Spark
-   Delta Tables
-   Spark SQL

### Machine Learning

-   FP-Growth
-   Item-Based Collaborative Filtering

### Frontend

-   Streamlit
-   Plotly
-   Pandas

### Deployment

-   Databricks Apps
-   Databricks SQL Connector

------------------------------------------------------------------------

## Architecture

``` text
Synthetic Data
      │
      ▼
Data Validation
      │
      ▼
Data Ingestion
      │
      ▼
Customer Segmentation
      │
      ├──────────────┐
      ▼              ▼
 FP-Growth        IBCF
      │              │
      └──────┬───────┘
             ▼
Recommendation Intelligence
             ▼
Customer 360
             ▼
Analytics Tables
             ▼
Streamlit Dashboard
```

------------------------------------------------------------------------

## Dataset

The project simulates four independent tenants.

  Tenant   Industry
  -------- -----------
  T001     Banking
  T002     Insurance
  T003     Telecom
  T004     Retail

Approximate scale:

-   8,000 customers
-   1,200 products
-   4 tenants
-   80,000+ customer-product relationships

------------------------------------------------------------------------

## Recommendation Engines

### FP-Growth

Discovers frequent product combinations using association rule mining.

Outputs include:

-   Confidence
-   Lift
-   Explainable recommendation rules

### Item-Based Collaborative Filtering

Generates recommendations based on product similarity.

Outputs include:

-   Similarity strength
-   Supporting products
-   Contributing products

------------------------------------------------------------------------

## Customer 360

Each customer profile contains:

-   Customer information
-   Owned products
-   FP-Growth recommendations
-   IBCF recommendations
-   Explainability metrics
-   Recommendation scores

------------------------------------------------------------------------

## Dashboard Modules

-   Executive Overview
-   Model Comparison
-   Segment Analytics
-   Product Analytics
-   Diversity Analytics
-   Customer 360

------------------------------------------------------------------------

## Repository Structure

``` text
recommendation-platform/
├── app.py
├── app.yml
├── requirements.txt
├── .streamlit/
│   └── secrets.toml
└── src/
    ├── constants.py
    ├── db.py
    ├── loaders.py
    └── pages/
        ├── executive_overview.py
        ├── model_comparison.py
        ├── segment_analytics.py
        ├── product_analytics.py
        ├── diversity_analytics.py
        └── customer_360.py
```

------------------------------------------------------------------------

## Deployment

The application is designed for **Databricks Apps**.

Configuration is supplied through:

``` toml
.streamlit/secrets.toml
```

The dashboard connects directly to Delta tables through the Databricks
SQL Warehouse.

------------------------------------------------------------------------

## Highlights

-   Scalable multi-tenant architecture
-   Explainable AI recommendations
-   End-to-end Spark pipeline
-   Production-style deployment
-   Interactive analytics dashboards
-   Modular Streamlit application

------------------------------------------------------------------------

## Future Enhancements

-   Hybrid recommendation engine
-   Real-time recommendation updates
-   REST API
-   Authentication & RBAC
-   A/B testing
-   Monitoring dashboards

------------------------------------------------------------------------

## License

This project is intended for educational and portfolio purposes.
