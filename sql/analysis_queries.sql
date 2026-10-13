-- SQL-ready equivalents of the core portfolio metrics.
-- Assumes a table named online_retail with the original UCI columns.

-- 1. Valid-sales base
WITH valid_sales AS (
    SELECT
        InvoiceNo,
        StockCode,
        Description,
        Quantity,
        InvoiceDate,
        UnitPrice,
        CustomerID,
        Country,
        Quantity * UnitPrice AS revenue
    FROM online_retail
    WHERE CAST(InvoiceNo AS VARCHAR) NOT LIKE 'C%'
      AND Quantity > 0
      AND UnitPrice > 0
)
SELECT
    COUNT(*) AS valid_line_items,
    COUNT(DISTINCT InvoiceNo) AS valid_orders,
    SUM(revenue) AS gross_revenue
FROM valid_sales;

-- 2. Monthly revenue
WITH valid_sales AS (
    SELECT InvoiceNo, InvoiceDate, Quantity * UnitPrice AS revenue
    FROM online_retail
    WHERE CAST(InvoiceNo AS VARCHAR) NOT LIKE 'C%'
      AND Quantity > 0
      AND UnitPrice > 0
)
SELECT
    DATE_TRUNC('month', InvoiceDate) AS month,
    COUNT(DISTINCT InvoiceNo) AS orders,
    SUM(revenue) AS revenue
FROM valid_sales
GROUP BY 1
ORDER BY 1;

-- 3. Top products by revenue and order count
WITH valid_sales AS (
    SELECT StockCode, Description, InvoiceNo, Quantity, Quantity * UnitPrice AS revenue
    FROM online_retail
    WHERE CAST(InvoiceNo AS VARCHAR) NOT LIKE 'C%'
      AND Quantity > 0
      AND UnitPrice > 0
)
SELECT
    StockCode,
    Description,
    SUM(revenue) AS revenue,
    SUM(Quantity) AS units,
    COUNT(DISTINCT InvoiceNo) AS orders
FROM valid_sales
GROUP BY 1, 2
ORDER BY revenue DESC
LIMIT 10;

-- 4. Cancellation monitoring
SELECT
    COUNT(DISTINCT CASE WHEN CAST(InvoiceNo AS VARCHAR) LIKE 'C%' THEN InvoiceNo END) AS cancelled_orders,
    COUNT(DISTINCT CASE WHEN CAST(InvoiceNo AS VARCHAR) NOT LIKE 'C%' THEN InvoiceNo END) AS valid_orders,
    100.0 * COUNT(DISTINCT CASE WHEN CAST(InvoiceNo AS VARCHAR) LIKE 'C%' THEN InvoiceNo END)
      / COUNT(DISTINCT InvoiceNo) AS cancellation_rate_pct
FROM online_retail;
