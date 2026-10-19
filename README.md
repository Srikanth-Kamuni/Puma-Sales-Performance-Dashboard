# PUMA-themed sales analytics | Excel, SQL and Python

An end-to-end sales analytics project covering data preparation, KPI calculations, an Excel dashboard, relational SQL analysis and a reproducible Python workflow. The same sales population and metric definitions are used across the three tools so results can be reconciled.

**Data disclosure:** Transaction records, customers, products, prices, costs, deliveries and targets are simulated for learning. They are not PUMA's internal data or a representative sample of its business. The project covers 12 selected countries, not every PUMA market. A separate file contains published historical PUMA sales figures; those figures are excluded from the transaction dashboard.

![Excel dashboard preview using simulated sales data](assets/advanced_dashboard_preview.png)

## Business problem

A practice sportswear business needs a consistent sales review across markets, products and channels. The analysis answers:

- How did net sales, gross profit and average order value change between 2023 and 2024?
- Which countries, regions, categories and products contribute the most sales?
- How do discounts, refunds and shipping affect the reported measures?
- Where do actual sales fall below monthly regional targets?
- Which customer purchasing patterns and delivery results need further review?

The deliverables are an Excel dashboard, SQL reporting queries, a Python notebook and script, exported reports, and calculation checks.

## Tools and techniques

| Tool | Work covered |
|---|---|
| Excel | Tables, Power Query import lessons, calculated columns, `SUMIFS`, `COUNTIFS`, `IF`, date functions, `INDEX`/`MATCH`, ranking, dropdown filters, charts and dashboard formatting |
| SQLite | Relational tables, keys and constraints, joins, views, aggregations, CTEs, window functions, indexes, query-plan inspection and transaction practice |
| Python | pandas, NumPy, Matplotlib, data-quality checks, validated merges, aggregation, customer RFM, scenario calculations and report exports |
| JupyterLab | A notebook version of the Python workflow for working through the analysis one section at a time |

The package includes starter and solution files, detailed Excel lessons, 34 SQL reporting exercises and 20 Python code sections.

## Dataset

The practice transactions cover **January 2023 through December 2024**. All financial inputs are expressed in simulated EUR.

| File | Meaning of one row | Records |
|---|---|---:|
| `data/sales_raw.csv` | One product line within an order, with descriptive fields attached | 7,200 |
| `data/orders.csv` | One placed order | 3,600 |
| `data/order_lines.csv` | One product line with relational identifiers | 7,200 |
| `data/customers.csv` | One simulated customer record | 900 |
| `data/products.csv` | One practice product | 24 |
| `data/countries.csv` | One country-to-region mapping | 12 |
| `data/monthly_targets.csv` | One target for a month and region | 72 |
| `data/sales_dirty_practice.csv` | One record in a separate cleaning exercise | 121 before cleaning |

The three regions are EMEA, Americas and Asia/Pacific. Categories are Footwear, Apparel and Accessories. Channels are Wholesale, Retail and E-commerce.

Each order has two product lines, and each month has 150 orders. This controlled structure supports learning and validation; it does not describe PUMA's transaction volumes. The customer table contains 900 records, which is not the same as 900 active customers in a selected period.

`sales_raw.csv` is the flattened version of the orders and order lines used in SQL. Do not append these datasets together. The dirty practice file is a separate exercise and must also stay outside the main sales population.

See the [data dictionary and assumptions](guides/01_Start_here_and_data_dictionary.md) for field definitions and record-level rules.

## KPI definitions

| KPI | Definition |
|---|---|
| Gross sales | Quantity × unit price |
| Discount amount | Gross sales × discount rate |
| Refund | Returned quantity × original discounted unit price |
| Net sales | Gross sales − discounts − refunds |
| Net units | Quantity − returned quantity |
| Cost of goods sold | Net units × historical unit cost |
| Gross profit | Net sales − cost of goods sold |
| Contribution | Gross profit − allocated shipping cost |
| Orders | Distinct order IDs |
| Average order value | Net sales ÷ distinct orders |
| Gross margin | Total gross profit ÷ total net sales |
| Unit return rate | Returned units ÷ units sold before returns |
| Discount rate on gross sales | Total discount amount ÷ total gross sales |
| Target attainment | Actual net sales ÷ target net sales |
| Year-on-year growth | Current-year net sales ÷ prior-year net sales − 1 |

Rates are calculated from their aggregate numerators and denominators, not by averaging transaction percentages. Financial components are rounded at line level as specified in the supplied code.

For the Excel dashboard's Year and Region filters, summing `FirstOrderFlag` counts each order once. That shortcut should not be reused for additional product or category filters without reviewing order-count logic.

## Excel dashboard

The solution workbook includes:

- Year and Region dropdown filters.
- Net Sales, Net Units, Orders and Average Order Value cards.
- Monthly sales and gross-profit trends.
- A world coverage image with formula-driven regional sales figures.
- Category and channel charts, a dynamic top-five product list and a target ring.
- Gross Margin, Gross Profit, Unit Return Rate and Discount Rate cards.
- A sidebar, product image and consistent panel formatting.

The supplied world map is a **fixed coverage image**. Its colours identify the selected practice markets and regions; they do not represent sales intensity or change with filters. The regional figures beside it are calculated dynamically. The advanced guide also explains a native Excel Filled Map alternative where supported.

### Start the Excel project

1. Open [PUMA_Sales_Starter.xlsx](excel/PUMA_Sales_Starter.xlsx) in desktop Excel and save a working copy.
2. Follow the [Excel foundation guide](guides/02_Excel_step_by_step.md) to inspect the data and build the calculations.
3. Follow the [advanced dashboard guide](guides/06_Advanced_Excel_dashboard.md) for layout, images, controls and charts.
4. Compare your calculations and layout with [PUMA_Sales_Solution.xlsx](excel/PUMA_Sales_Solution.xlsx).
5. Check the results against the [answer checks](guides/05_Answer_checks.md).

The [complete HTML handbook](PUMA_Complete_Handbook.html) combines the lessons and can be opened locally in a browser. Download the repository to use the workbook and handbook files.

## SQL analysis

The SQL implementation uses **SQLite**, with six source tables: `countries`, `customers`, `products`, `orders`, `order_lines` and `monthly_targets`.

Orders connect to customers and countries; order lines connect to orders and products. Targets have a separate month-and-region grain. Actual sales are aggregated to that grain before joining targets to prevent repeated target amounts.

Three analytical views, `v_base`, `v_net` and `v_sales`, organise the calculations. The exercises progress from filtering and joins to product rankings, category share, month-over-month growth, running totals, moving averages, RFM and reconciliation.

### Run the SQL exercises

1. Use a SQLite editor such as [DB Browser for SQLite](https://sqlitebrowser.org/). Window-function exercises require SQLite 3.25 or later.
2. Copy `sql/puma_starter.sqlite` to a working database, for example `sql/puma_my_work.sqlite`.
3. Open the working database in the editor.
4. Run [01_setup_views.sql](sql/01_setup_views.sql) to create the analytical views and indexes. Save pending database changes.
5. Open [02_analysis_queries.sql](sql/02_analysis_queries.sql). Execute one numbered query at a time.
6. Use the [SQL guide](guides/03_SQL_step_by_step.md) for explanations of the statements, conditions and functions.
7. Use [03_transaction_practice.sql](sql/03_transaction_practice.sql) for temporary-table update and rollback practice.
8. Compare with `sql/puma_solution.sqlite` and `results/sql_answer_samples.json`.

To rebuild the starter database from the CSV files, first rename or move the existing `sql/puma_starter.sqlite`, then run this from the project root:

```bash
python sql/build_database.py
```

The builder uses Python's standard library and refuses to overwrite an existing starter database. It creates and loads the source tables; run the setup views afterwards.

The supplied queries use SQLite-specific date functions and syntax. SQL Server, MySQL and PostgreSQL versions would require changes.

## Python analysis

The Python workflow includes:

- Loading data and checking identifiers, dates, quantities, returns and discounts.
- Cleaning the separate dirty dataset and exporting accepted and rejected records.
- Calculating revenue, cost, profit and weighted KPIs.
- Analysing annual and monthly trends, countries, categories and channels.
- Validating customer and target joins.
- Building customer recency, frequency and monetary-value summaries.
- Flagging unusually large orders for review.
- Calculating a fixed-volume discount sensitivity scenario.
- Reconciling annual totals with expected controls and the SQL solution.
- Saving a four-panel Matplotlib figure and CSV reports.

### Run the Python script

Open a terminal in the project root, where the `data`, `sql` and `python` folders are visible.

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Or on macOS/Linux:

```bash
source .venv/bin/activate
```

Install the dependencies and run the analysis:

```bash
python -m pip install -r python/requirements.txt
python python/puma_analysis.py
```

Keep `sql/puma_solution.sqlite` and `results/expected_checks.json` in place: the script uses them for reconciliation. A successful run prints a completion message after its assertions pass and writes reports to `results/python/`, replacing matching output files.

### Work through the notebook

With the environment activated:

```bash
jupyter lab
```

Open [python/puma_analysis.ipynb](python/puma_analysis.ipynb) and run the cells in order. Use the [Python guide](guides/04_Python_step_by_step.md) for explanations.

The Python dashboard is a saved PNG figure, not an interactive web application.

## Reference results: 2024, all regions

These are expected results from the **simulated transactions**, not published PUMA financial results.

| Measure | Value |
|---|---:|
| Net sales | €1,885,059.75 |
| Gross profit | €920,398.35 |
| Contribution after allocated shipping | €907,487.85 |
| Net units | 33,663 |
| Orders | 1,800 |
| Average order value | €1,047.26 |
| Gross margin | 48.83% |
| Unit return rate | 1.69% |
| Annual target | €1,967,911.08 |
| Target attainment | 95.79% |
| Actual minus target | −€82,851.33 |
| Net sales growth versus 2023 | 10.62% |

Within this practice dataset:

- Net sales increased from €1,704,092.00 in 2023 to €1,885,059.75 in 2024. Orders remained at 1,800 in each year, while average order value increased.
- Footwear contributed €940,561.00, or approximately 49.90% of 2024 net sales.
- Wholesale contributed €1,446,512.25, or approximately 76.74% of 2024 net sales.
- Annual net sales were €82,851.33 below the artificial target.

These observations describe the generated data only and do not establish causes or support recommendations about PUMA's actual business.

## Validation and assumptions

Checks include unique line identifiers, distinct order counts, valid return quantities and discount rates, join cardinality, revenue reconciliation, and agreement between Python and SQL annual totals. Reference controls are stored in [expected_checks.json](results/expected_checks.json).

The separate dirty-data exercise contains one exact duplicate. After duplicate removal and rule checks, the supplied workflow produces **114 accepted records and 6 rejected records**.

Important modelling assumptions:

- Returns are assigned to the original order month; no separate return date is available.
- Returned units are assumed recoverable, so their cost is removed from recognised COGS.
- Shipping is allocated per transaction line and retained after returns.
- Contribution excludes other operating costs and is not net profit.
- Targets were generated from practice sales using varying multipliers; they are not independent budgets or forecasts.
- The discount scenario holds volume constant and does not model customer demand responses.
- Large-order flags identify review candidates, not confirmed errors or fraud.
- SQLite uses floating-point money fields in this teaching project; monetary comparisons use a €0.01 tolerance.

## Repository contents

| Location | Contents |
|---|---|
| `data/` | Clean CSVs, relational extracts, dirty-data exercise and separate published-sales reference |
| `excel/` | Starter and solution workbooks |
| `sql/` | Database files, schema, builder, views and exercises |
| `python/` | Analysis script, notebook and dependencies |
| `guides/` | Data dictionary, Excel, SQL, Python, validation and advanced dashboard lessons |
| `assets/` | Dashboard preview, decorative product image, coverage map and asset notes |
| `results/` | Expected controls, SQL answer samples and completed Python outputs |
| `PUMA_Complete_Handbook.html` | Combined offline learning handbook |

Place this `README.md` at the repository root beside these folders. Relative links and dashboard images depend on that layout.

## Sources and asset notes

The separate [published-sales reference](data/puma_published_sales_2023_2024.csv) cites [PUMA Annual Report 2024 — Sales development](https://annual-report.puma.com/2024/en/combined-management-report/economic-report/sales-development/index.html). Its group, region and product-division rows are alternative views of sales and must not be summed together. It does not reconcile to the simulated transactions.

The map uses public-domain [Natural Earth country geometry](https://www.naturalearthdata.com/downloads/110m-cultural-vectors/). The decorative sports image is an AI-generated fictional product concept, not an official PUMA catalogue photograph. See [asset notes](assets/ASSET_NOTES.md).

This is an independent educational portfolio project and is not affiliated with or endorsed by PUMA.

## Author

**Srikanth Kamuni**
