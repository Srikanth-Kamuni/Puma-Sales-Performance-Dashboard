-- 01. Inspect the first orders
SELECT OrderID, OrderDate, Country, Channel FROM orders ORDER BY OrderID LIMIT 10;

-- 02. Count the tables
SELECT 'orders' AS TableName, COUNT(*) AS Rows FROM orders UNION ALL SELECT 'order_lines', COUNT(*) FROM order_lines UNION ALL SELECT 'products', COUNT(*) FROM products;

-- 03. Find the available categories
SELECT DISTINCT Category FROM products ORDER BY Category;

-- 04. Filter one country and period
SELECT * FROM orders WHERE Country='Poland' AND OrderDate>='2024-01-01' AND OrderDate<'2025-01-01' ORDER BY OrderDate,OrderID;

-- 05. Combine AND, OR, IN and a threshold
SELECT LineID, Quantity, DiscountRate FROM order_lines WHERE Quantity>=10 AND DiscountRate IN (0.20,0.25) ORDER BY Quantity DESC,LineID;

-- 06. Search names with LIKE
SELECT ProductID,ProductName FROM products WHERE ProductName LIKE '%Footwear%' ORDER BY ProductID;

-- 07. Build a row-level calculation
SELECT LineID,Quantity,UnitPriceEUR, ROUND(Quantity*UnitPriceEUR,2) AS GrossSalesEUR FROM order_lines ORDER BY LineID LIMIT 10;

-- 08. Classify discount bands with CASE
SELECT CASE WHEN DiscountRate=0 THEN 'No discount' WHEN DiscountRate<=0.10 THEN 'Up to 10%' ELSE 'Above 10%' END AS DiscountBand, COUNT(*) AS Lines FROM order_lines GROUP BY DiscountBand ORDER BY DiscountBand;

-- 09. Check duplicates
SELECT LineID,COUNT(*) AS Occurrences FROM order_lines GROUP BY LineID HAVING COUNT(*)>1;

-- 10. Validate quantity and return rules
SELECT LineID FROM order_lines WHERE Quantity<=0 OR ReturnedQty<0 OR ReturnedQty>Quantity OR DiscountRate<0 OR DiscountRate>1;

-- 11. Join lines to products
SELECT l.LineID,l.ProductID,p.ProductName,p.Category FROM order_lines AS l JOIN products AS p ON l.ProductID=p.ProductID ORDER BY l.LineID LIMIT 10;

-- 12. Detect missing product keys
SELECT l.LineID,l.ProductID FROM order_lines AS l LEFT JOIN products AS p ON l.ProductID=p.ProductID WHERE p.ProductID IS NULL;

-- 13. Inspect the analytical view
SELECT LineID,OrderID,Year,Region,Category,NetSalesEUR,COGSEUR,GrossProfitEUR FROM v_sales ORDER BY LineID LIMIT 10;

-- 14. Calculate annual KPI totals
SELECT Year,COUNT(*) AS Lines,COUNT(DISTINCT OrderID) AS Orders,ROUND(SUM(NetSalesEUR),2) AS NetSalesEUR,ROUND(SUM(GrossProfitEUR),2) AS GrossProfitEUR,ROUND(SUM(ContributionEUR),2) AS ContributionEUR FROM v_sales GROUP BY Year ORDER BY Year;

-- 15. Calculate weighted margin, returns and AOV
SELECT Year, ROUND(1.0*SUM(GrossProfitEUR)/NULLIF(SUM(NetSalesEUR),0),6) AS GrossMargin, ROUND(1.0*SUM(ReturnedQty)/NULLIF(SUM(Quantity),0),6) AS ReturnRate, ROUND(1.0*SUM(NetSalesEUR)/NULLIF(COUNT(DISTINCT OrderID),0),2) AS AverageOrderValueEUR FROM v_sales GROUP BY Year ORDER BY Year;

-- 16. Rank countries by sales
SELECT Country,ROUND(SUM(NetSalesEUR),2) AS NetSalesEUR FROM v_sales WHERE Year=2024 GROUP BY Country ORDER BY NetSalesEUR DESC,Country LIMIT 5;

-- 17. Filter groups using HAVING
SELECT Category,ROUND(SUM(NetSalesEUR),2) AS NetSalesEUR FROM v_sales WHERE Year=2024 GROUP BY Category HAVING SUM(NetSalesEUR)>300000 ORDER BY NetSalesEUR DESC;

-- 18. Aggregate dates by month
SELECT MonthStart,ROUND(SUM(NetSalesEUR),2) AS NetSalesEUR FROM v_sales GROUP BY MonthStart ORDER BY MonthStart;

-- 19. Find above-average order values with a CTE
WITH order_totals AS (SELECT OrderID,SUM(NetSalesEUR) AS OrderSales FROM v_sales WHERE Year=2024 GROUP BY OrderID) SELECT OrderID,ROUND(OrderSales,2) AS OrderSales FROM order_totals WHERE OrderSales>(SELECT AVG(OrderSales) FROM order_totals) ORDER BY OrderSales DESC,OrderID LIMIT 10;

-- 20. Find customers with repeat purchases
SELECT CustomerID,COUNT(*) AS Orders FROM orders WHERE OrderDate>='2024-01-01' AND OrderDate<'2025-01-01' GROUP BY CustomerID HAVING COUNT(*)>=2 ORDER BY Orders DESC,CustomerID;

-- 21. Find customers with no orders using NOT EXISTS
SELECT c.CustomerID,c.CustomerSegment FROM customers AS c WHERE NOT EXISTS (SELECT 1 FROM orders AS o WHERE o.CustomerID=c.CustomerID) ORDER BY c.CustomerID;

-- 22. Calculate category share with a window
WITH totals AS (SELECT Category,SUM(NetSalesEUR) AS Sales FROM v_sales WHERE Year=2024 GROUP BY Category) SELECT Category,ROUND(Sales,2) AS NetSalesEUR,ROUND(Sales/SUM(Sales) OVER (),6) AS SalesShare FROM totals ORDER BY Sales DESC;

-- 23. Rank products within each region
WITH totals AS (SELECT Region,ProductID,SUM(NetSalesEUR) AS Sales FROM v_sales WHERE Year=2024 GROUP BY Region,ProductID), ranked AS (SELECT *,DENSE_RANK() OVER (PARTITION BY Region ORDER BY Sales DESC) AS SalesRank FROM totals) SELECT Region,ProductID,ROUND(Sales,2) AS NetSalesEUR,SalesRank FROM ranked WHERE SalesRank<=3 ORDER BY Region,SalesRank,ProductID;

-- 24. Calculate month-over-month change
WITH monthly AS (SELECT MonthStart,SUM(NetSalesEUR) AS Sales FROM v_sales GROUP BY MonthStart), lagged AS (SELECT *,LAG(Sales) OVER (ORDER BY MonthStart) AS PreviousSales FROM monthly) SELECT MonthStart,ROUND(Sales,2) AS NetSalesEUR,ROUND(Sales/NULLIF(PreviousSales,0)-1,6) AS MoMGrowth FROM lagged ORDER BY MonthStart;

-- 25. Calculate running sales and moving average
WITH monthly AS (SELECT Year,MonthStart,SUM(NetSalesEUR) AS Sales FROM v_sales GROUP BY Year,MonthStart) SELECT Year,MonthStart,ROUND(Sales,2) AS NetSalesEUR,ROUND(SUM(Sales) OVER (PARTITION BY Year ORDER BY MonthStart ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW),2) AS YTDSales,ROUND(AVG(Sales) OVER (ORDER BY MonthStart ROWS BETWEEN 2 PRECEDING AND CURRENT ROW),2) AS ThreeMonthAverage FROM monthly ORDER BY MonthStart;

-- 26. Compare annual sales using conditional aggregation
SELECT Region,ROUND(SUM(CASE WHEN Year=2023 THEN NetSalesEUR ELSE 0 END),2) AS Sales2023,ROUND(SUM(CASE WHEN Year=2024 THEN NetSalesEUR ELSE 0 END),2) AS Sales2024,ROUND(SUM(CASE WHEN Year=2024 THEN NetSalesEUR ELSE 0 END)/NULLIF(SUM(CASE WHEN Year=2023 THEN NetSalesEUR ELSE 0 END),0)-1,6) AS YoYGrowth FROM v_sales GROUP BY Region ORDER BY Region;

-- 27. Join targets at their own grain
WITH actual AS (SELECT MonthStart,Region,SUM(NetSalesEUR) AS Sales FROM v_sales GROUP BY MonthStart,Region) SELECT t.MonthStart,t.Region,ROUND(COALESCE(a.Sales,0),2) AS ActualEUR,t.TargetNetSalesEUR,ROUND(COALESCE(a.Sales,0)-t.TargetNetSalesEUR,2) AS VarianceEUR,ROUND(a.Sales/NULLIF(t.TargetNetSalesEUR,0),6) AS Attainment FROM monthly_targets AS t LEFT JOIN actual AS a ON t.MonthStart=a.MonthStart AND t.Region=a.Region ORDER BY t.MonthStart,t.Region;

-- 28. Compare channels and delivery performance
SELECT Channel,COUNT(DISTINCT OrderID) AS Orders,ROUND(SUM(NetSalesEUR),2) AS NetSalesEUR,ROUND(AVG(DeliveryDays),2) AS AvgLineDeliveryDays,ROUND(1.0*SUM(CASE WHEN DeliveryDays>7 THEN 1 ELSE 0 END)/COUNT(*),6) AS LateLineRate FROM v_sales WHERE Year=2024 GROUP BY Channel ORDER BY NetSalesEUR DESC;

-- 29. Investigate returns by category
SELECT Category,SUM(Quantity) AS SoldUnits,SUM(ReturnedQty) AS ReturnedUnits,ROUND(1.0*SUM(ReturnedQty)/NULLIF(SUM(Quantity),0),6) AS UnitReturnRate,ROUND(SUM(RefundEUR),2) AS RefundEUR FROM v_sales WHERE Year=2024 GROUP BY Category ORDER BY UnitReturnRate DESC;

-- 30. Build a customer RFM table
WITH per_order AS (SELECT CustomerID,OrderID,MAX(OrderDate) AS OrderDate,SUM(NetSalesEUR) AS Sales FROM v_sales WHERE Year=2024 GROUP BY CustomerID,OrderID) SELECT CustomerID,CAST(julianday('2024-12-31')-julianday(MAX(OrderDate)) AS INTEGER) AS RecencyDays,COUNT(*) AS Frequency,ROUND(SUM(Sales),2) AS MonetaryEUR FROM per_order GROUP BY CustomerID ORDER BY MonetaryEUR DESC,CustomerID;

-- 31. Compare customer segments
SELECT c.CustomerSegment,COUNT(DISTINCT s.CustomerID) AS ActiveCustomers,COUNT(DISTINCT s.OrderID) AS Orders,ROUND(SUM(s.NetSalesEUR),2) AS NetSalesEUR FROM v_sales AS s JOIN customers AS c ON s.CustomerID=c.CustomerID WHERE s.Year=2024 GROUP BY c.CustomerSegment ORDER BY NetSalesEUR DESC;

-- 32. Create a discount sensitivity exercise
SELECT Category,ROUND(SUM(NetUnits*UnitPriceEUR*(1-DiscountRate)),2) AS CurrentNetSalesEUR,ROUND(SUM(NetUnits*UnitPriceEUR*(1-MIN(DiscountRate+0.05,1))),2) AS ScenarioNetSalesEUR FROM v_sales WHERE Year=2024 GROUP BY Category ORDER BY Category;

-- 33. Inspect a query plan
EXPLAIN QUERY PLAN SELECT OrderID FROM orders WHERE OrderDate>='2024-01-01' AND OrderDate<'2025-01-01';

-- 34. Reconcile revenue components
SELECT Year,ROUND(SUM(GrossSalesEUR)-SUM(DiscountEUR)-SUM(RefundEUR)-SUM(NetSalesEUR),6) AS RevenueDifference,ROUND(SUM(NetSalesEUR)-SUM(COGSEUR)-SUM(GrossProfitEUR),6) AS ProfitDifference FROM v_sales GROUP BY Year ORDER BY Year;