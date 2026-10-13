# Data dictionary

Source: UCI Online Retail dataset.

| Field | Description | Type | Analytical use |
|---|---|---|---|
| `InvoiceNo` | Invoice number; values beginning with `C` indicate cancellation | Categorical | Order identifier and cancellation flag |
| `StockCode` | Product code | Categorical | Product-level aggregation |
| `Description` | Product name | Categorical | Product interpretation |
| `Quantity` | Units in the line item | Integer | Volume and revenue calculation |
| `InvoiceDate` | Date and time invoice was generated | Datetime | Seasonality and order timing |
| `UnitPrice` | Product price per unit in GBP | Numeric | Revenue calculation |
| `CustomerID` | Customer identifier | Categorical | Customer-level analysis and RFM |
| `Country` | Customer country | Categorical | Geographic analysis |

## Derived fields

- `is_cancelled`: invoice number starts with `C`.
- `Revenue`: `Quantity * UnitPrice`.
- `Month`: month extracted from `InvoiceDate`.
- `DayOfWeek`: weekday extracted from `InvoiceDate`.
- `Hour`: hour extracted from `InvoiceDate`.

## Cleaning rules

- Exclude cancellation invoices from valid-sales reporting.
- Exclude rows with non-positive quantity or unit price.
- Use non-null `CustomerID` only for customer-level RFM segmentation.
