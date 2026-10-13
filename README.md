# Online Retail Growth & Customer Retention

A data analyst portfolio case study using the official [UCI Online Retail dataset](https://archive.ics.uci.edu/dataset/352/online+retail).

![Monthly revenue](charts/01_monthly_revenue.png)

## Business question

How can a small online retailer use transaction data to protect revenue, prioritize customer retention, and plan around demand peaks?

## Headline findings

- **£10.67M** gross revenue from valid, non-cancelled line items.
- **19,960** valid orders across **4,338** customers with an ID.
- **16.1%** cancellation rate by invoice count.
- **November 2011** was the strongest month at **£1.51M**.
- The United Kingdom generated **84.6%** of revenue.
- **947 Champions** generated **64.6%** of identified-customer revenue.

## What this project demonstrates

- Data cleaning and metric definition
- Exploratory analysis and KPI design
- Product and geographic performance analysis
- RFM customer segmentation
- Business-focused visualization
- SQL-ready analytical logic
- Translating findings into operational recommendations

## Portfolio deliverables

- [Read the full portfolio case study](portfolio.md)
- [Download the PDF portfolio](portfolio.pdf)
- [View the Python analysis](analyze.py)
- [View SQL analysis examples](sql/analysis_queries.sql)
- [View the data dictionary](docs/data-dictionary.md)
- [View reproducibility notes](docs/reproducibility.md)

## Visualizations

| Analysis | Chart |
|---|---|
| Revenue seasonality | [Monthly revenue](charts/01_monthly_revenue.png) |
| Product mix | [Top products](charts/02_top_products.png) |
| Market mix | [Top countries](charts/03_top_countries.png) |
| Customer value | [RFM segments](charts/04_rfm_segments.png) |
| Operating rhythm | [Order heatmap](charts/05_order_heatmap.png) |

## How to reproduce

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Download and extract the dataset into `data/Online Retail.xlsx`, then run:

```bash
python analyze.py
```

The raw dataset is intentionally excluded from GitHub. See [`data/README.md`](data/README.md) for the official source and setup instructions.

## Data source and attribution

Chen, D. (2015). *Online Retail*. UCI Machine Learning Repository. https://doi.org/10.24432/C5BW33

The dataset is licensed under CC BY 4.0. The analysis follows the UCI variable definitions and identifies invoice numbers beginning with `C` as cancellations.
