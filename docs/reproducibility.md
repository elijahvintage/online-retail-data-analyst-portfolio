# Reproducibility notes

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Download and extract the official UCI dataset into `data/Online Retail.xlsx`, then run:

```bash
python analyze.py
```

The script writes:

- `charts/` — five PNG visualizations
- `tables/` — CSV outputs for monthly, product, country, and RFM analysis
- `metrics.json` — headline KPIs
- `insights.json` — narrative-ready findings

## Metric definitions

- Gross revenue is the sum of `Quantity * UnitPrice` for valid, non-cancelled rows.
- An order is a distinct valid `InvoiceNo`.
- Cancellation rate is cancelled invoice count divided by all cancelled plus valid invoices.
- RFM uses quintile scores across customer recency, frequency, and monetary value.

The dataset ends on 09 Dec 2011. The findings demonstrate analytical method and business communication; they are not a current market forecast.
