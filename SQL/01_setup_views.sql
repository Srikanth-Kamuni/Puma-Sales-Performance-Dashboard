-- Run once on puma_starter.sqlite before the analytical queries.
CREATE VIEW IF NOT EXISTS v_base AS
SELECT l.*, o.OrderDate, o.CustomerID, o.Country, o.Channel,
       o.PaymentMethod, p.ProductName, p.Category, c.Region,
       CAST(strftime('%Y',o.OrderDate) AS INTEGER) AS Year,
       substr(o.OrderDate,1,7)||'-01' AS MonthStart,
       ROUND(l.Quantity*l.UnitPriceEUR,2) AS GrossSalesEUR,
       ROUND(l.Quantity*l.UnitPriceEUR*l.DiscountRate,2) AS DiscountEUR,
       ROUND(l.ReturnedQty*l.UnitPriceEUR*(1-l.DiscountRate),2) AS RefundEUR,
       l.Quantity-l.ReturnedQty AS NetUnits,
       ROUND((l.Quantity-l.ReturnedQty)*l.UnitCostEUR,2) AS COGSEUR
FROM order_lines AS l
JOIN orders AS o ON l.OrderID=o.OrderID
JOIN products AS p ON l.ProductID=p.ProductID
JOIN countries AS c ON o.Country=c.Country;

CREATE VIEW IF NOT EXISTS v_net AS
SELECT *, ROUND(GrossSalesEUR-DiscountEUR-RefundEUR,2) AS NetSalesEUR
FROM v_base;

CREATE VIEW IF NOT EXISTS v_sales AS
SELECT *, ROUND(NetSalesEUR-COGSEUR,2) AS GrossProfitEUR,
       ROUND(NetSalesEUR-COGSEUR-ShippingCostEUR,2) AS ContributionEUR
FROM v_net;

CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(OrderDate);
CREATE INDEX IF NOT EXISTS idx_lines_order ON order_lines(OrderID);
CREATE INDEX IF NOT EXISTS idx_lines_product ON order_lines(ProductID);
