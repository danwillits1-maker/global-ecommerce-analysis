# Global E-Commerce Analysis

An end-to-end analytics project using a synthetic e-commerce dataset to explore revenue, profit, product performance, regional results and order-status risk. The workflow uses Python, PostgreSQL and Power BI, with a five-page interactive dashboard.

## Business Questions

- How are revenue and profit distributed across products, countries and time?
- Which categories and subcategories show different revenue and profit-margin patterns?
- What do order statuses and shipping methods reveal in the dashboard’s risk measures?

## Dashboard Highlights

These figures are outputs from the project’s simulated dataset:

- **Overall performance:** $3.20M revenue, $743.66K profit and a 23.2% profit margin, compared with a 20% target.
- **Product performance:** Electronics contributed 60.87% of revenue. Women’s Wear had the highest subcategory margin shown at 37.3%.
- **Regional performance:** Germany’s margin was 17.4%, compared with the 23.2% overall margin.
- **Order risk:** The dashboard reports $2.87M in lost revenue and 47.2% revenue leakage. Economy and Overnight shipping show the largest lost-revenue amounts, at $0.79M and $0.76M.

## Workflow

1. **Python and Pandas:** Cleaned column names, standardized text, parsed dates, removed exact duplicate rows, and prepared the fact and dimension tables.
2. **PostgreSQL:** Structured the data into a star schema with a fact table and six dimension tables, then added relational constraints and validation queries.
3. **Power BI:** Connected to PostgreSQL and built DAX measures and interactive views for the executive summary, product performance, regional performance, performance trends and risk audit.

## Data Source and Limitations

The dataset is a synthetic dataset from [Kaggle](https://www.kaggle.com/datasets/abdelfattahibrahim/global-e-commerce-sales-dataset-20212024), rather than real company data.

The SQL scenario-adjustment script deliberately changes some category revenue and profit values, seasonal patterns, Germany’s results, and selected return and cancellation statuses. The dashboard therefore demonstrates an analytics workflow on simulated scenarios; its patterns are not independent evidence about real customers or markets.

The dataset does not explain why orders were returned or cancelled, or establish actual delivery problems. Treat explanations about shipping, carriers or customer behaviour as hypotheses to validate with real operational data.

## Possible Follow-Up Analysis

- Use return and cancellation reason codes to investigate why orders fail.
- Compare promised and actual delivery times by shipping method and carrier.
- Validate regional and product-margin decisions using actual costs and marketing-spend data.
