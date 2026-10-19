"""Run from any folder: python sql/build_database.py. Standard library only."""
from pathlib import Path
import csv, sqlite3

ROOT=Path(__file__).resolve().parents[1]
db=ROOT/'sql'/'puma_starter.sqlite'
if db.exists():
    raise SystemExit('puma_starter.sqlite exists. Use the supplied file, or rename it before rebuilding.')
schema='''
PRAGMA foreign_keys=ON;
CREATE TABLE countries (Country TEXT PRIMARY KEY, Region TEXT NOT NULL);
CREATE TABLE customers (CustomerID TEXT PRIMARY KEY, CustomerSegment TEXT NOT NULL, SignupYear INTEGER NOT NULL);
CREATE TABLE products (ProductID TEXT PRIMARY KEY, ProductName TEXT NOT NULL, Category TEXT NOT NULL, ListPriceEUR REAL NOT NULL CHECK(ListPriceEUR>0), UnitCostEUR REAL NOT NULL CHECK(UnitCostEUR>=0));
CREATE TABLE orders (OrderID TEXT PRIMARY KEY, OrderDate TEXT NOT NULL, CustomerID TEXT NOT NULL REFERENCES customers(CustomerID), Country TEXT NOT NULL REFERENCES countries(Country), Channel TEXT NOT NULL, PaymentMethod TEXT NOT NULL);
CREATE TABLE order_lines (LineID TEXT PRIMARY KEY, OrderID TEXT NOT NULL REFERENCES orders(OrderID), ProductID TEXT NOT NULL REFERENCES products(ProductID), Quantity INTEGER NOT NULL CHECK(Quantity>0), UnitPriceEUR REAL NOT NULL CHECK(UnitPriceEUR>0), DiscountRate REAL NOT NULL CHECK(DiscountRate>=0 AND DiscountRate<=1), ReturnedQty INTEGER NOT NULL CHECK(ReturnedQty>=0 AND ReturnedQty<=Quantity), UnitCostEUR REAL NOT NULL CHECK(UnitCostEUR>=0), ShippingCostEUR REAL NOT NULL CHECK(ShippingCostEUR>=0), DeliveryDays INTEGER NOT NULL CHECK(DeliveryDays>=0));
CREATE TABLE monthly_targets (MonthStart TEXT NOT NULL, Region TEXT NOT NULL, TargetNetSalesEUR REAL NOT NULL CHECK(TargetNetSalesEUR>0), PRIMARY KEY(MonthStart,Region));
'''
with sqlite3.connect(db) as con:
    con.executescript(schema)
    for table in ['countries','customers','products','orders','order_lines','monthly_targets']:
        with (ROOT/'data'/f'{table}.csv').open(newline='',encoding='utf-8') as f:
            reader=csv.reader(f);headers=next(reader)
            sql=f'INSERT INTO {table} ({",".join(headers)}) VALUES ({",".join("?" for _ in headers)})'
            con.executemany(sql,reader)
    assert con.execute('PRAGMA foreign_key_check').fetchall()==[]
(ROOT/'sql'/'schema.sql').write_text(schema)
print('Created',db.name,'with 6 loaded tables. No analytical views yet.')
