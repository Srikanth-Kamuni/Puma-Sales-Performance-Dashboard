
PRAGMA foreign_keys=ON;
CREATE TABLE countries (Country TEXT PRIMARY KEY, Region TEXT NOT NULL);
CREATE TABLE customers (CustomerID TEXT PRIMARY KEY, CustomerSegment TEXT NOT NULL, SignupYear INTEGER NOT NULL);
CREATE TABLE products (ProductID TEXT PRIMARY KEY, ProductName TEXT NOT NULL, Category TEXT NOT NULL, ListPriceEUR REAL NOT NULL CHECK(ListPriceEUR>0), UnitCostEUR REAL NOT NULL CHECK(UnitCostEUR>=0));
CREATE TABLE orders (OrderID TEXT PRIMARY KEY, OrderDate TEXT NOT NULL, CustomerID TEXT NOT NULL REFERENCES customers(CustomerID), Country TEXT NOT NULL REFERENCES countries(Country), Channel TEXT NOT NULL, PaymentMethod TEXT NOT NULL);
CREATE TABLE order_lines (LineID TEXT PRIMARY KEY, OrderID TEXT NOT NULL REFERENCES orders(OrderID), ProductID TEXT NOT NULL REFERENCES products(ProductID), Quantity INTEGER NOT NULL CHECK(Quantity>0), UnitPriceEUR REAL NOT NULL CHECK(UnitPriceEUR>0), DiscountRate REAL NOT NULL CHECK(DiscountRate>=0 AND DiscountRate<=1), ReturnedQty INTEGER NOT NULL CHECK(ReturnedQty>=0 AND ReturnedQty<=Quantity), UnitCostEUR REAL NOT NULL CHECK(UnitCostEUR>=0), ShippingCostEUR REAL NOT NULL CHECK(ShippingCostEUR>=0), DeliveryDays INTEGER NOT NULL CHECK(DeliveryDays>=0));
CREATE TABLE monthly_targets (MonthStart TEXT NOT NULL, Region TEXT NOT NULL, TargetNetSalesEUR REAL NOT NULL CHECK(TargetNetSalesEUR>0), PRIMARY KEY(MonthStart,Region));
