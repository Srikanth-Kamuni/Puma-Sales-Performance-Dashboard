"""PUMA-themed simulated sales analysis. Run: python python/puma_analysis.py"""
# %% 01 Imports and folders
from pathlib import Path
import json
import sqlite3
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Save charts without requiring an interactive display.
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'
OUT=ROOT/'results'/'python'
OUT.mkdir(parents=True,exist_ok=True)

# %% 02 Load and inspect the clean sales data
sales=pd.read_csv(DATA/'sales_raw.csv')
print(sales.head())
print('Rows and columns:',sales.shape)
print(sales.dtypes)
print('Missing values:',sales.isna().sum().to_dict())
sales['OrderDate']=pd.to_datetime(sales['OrderDate'],format='%Y-%m-%d',errors='raise')
assert len(sales)==7200
assert sales['LineID'].is_unique
assert sales['OrderID'].nunique()==3600

# %% 03 Validate numerical rules and the order flag
assert sales['Quantity'].gt(0).all()
assert sales['ReturnedQty'].ge(0).all()
assert sales['ReturnedQty'].le(sales['Quantity']).all()
assert sales['DiscountRate'].between(0,1).all()
assert sales['UnitPriceEUR'].gt(0).all()
assert sales.groupby('OrderID')['FirstOrderFlag'].sum().eq(1).all()

# %% 04 Clean a deliberately dirty practice file
dirty=pd.read_csv(DATA/'sales_dirty_practice.csv')
duplicate_count=int(dirty.duplicated(subset=['LineID']).sum())
# This file has one exact duplicate. Conflicting repeated IDs require investigation.
dirty=dirty.drop_duplicates().copy()
dirty['Country']=dirty['Country'].str.strip()
channel_map={'wholesale':'Wholesale','retail':'Retail','e-commerce':'E-commerce'}
dirty['Channel']=dirty['Channel'].str.strip().str.lower().map(channel_map)
dirty['OrderDate']=pd.to_datetime(dirty['OrderDate'],format='%Y-%m-%d',errors='coerce')
for c in ['Quantity','ReturnedQty','UnitPriceEUR','DiscountRate']:
    dirty[c]=pd.to_numeric(dirty[c],errors='coerce')
valid_products=set(pd.read_csv(DATA/'products.csv')['ProductID'])
valid_countries=set(pd.read_csv(DATA/'countries.csv')['Country'])
checks=pd.DataFrame({
    'missing_required':dirty[['OrderDate','Quantity','ReturnedQty','UnitPriceEUR','DiscountRate','Channel']].isna().any(axis=1),
    'invalid_quantity':dirty['Quantity'].le(0),
    'invalid_returns':dirty['ReturnedQty'].lt(0)|dirty['ReturnedQty'].gt(dirty['Quantity']),
    'invalid_price':dirty['UnitPriceEUR'].le(0),
    'invalid_discount':~dirty['DiscountRate'].between(0,1),
    'unknown_product':~dirty['ProductID'].isin(valid_products),
    'unknown_country':~dirty['Country'].isin(valid_countries)
})
bad=checks.any(axis=1)
rejects=dirty.loc[bad].join(checks.loc[bad].add_prefix('Issue_'))
clean_practice=dirty.loc[~bad].copy()
rejects.to_csv(OUT/'dirty_rejected_rows.csv',index=False)
clean_practice.to_csv(OUT/'dirty_accepted_rows.csv',index=False)
print('Dirty-file duplicate count:',duplicate_count,'Accepted:',len(clean_practice),'Rejected:',len(rejects))
assert duplicate_count==1 and len(clean_practice)==114 and len(rejects)==6
# The small cleaning file is a separate exercise. Do not append it to sales.

# %% 05 Calculate date keys and revenue components
sales['Year']=sales['OrderDate'].dt.year
sales['MonthStart']=sales['OrderDate'].dt.to_period('M').dt.to_timestamp()
sales['GrossSalesEUR']=(sales['Quantity']*sales['UnitPriceEUR']).round(2)
sales['DiscountEUR']=(sales['GrossSalesEUR']*sales['DiscountRate']).round(2)
sales['SalesAfterDiscountEUR']=sales['GrossSalesEUR']-sales['DiscountEUR']
sales['RefundEUR']=(sales['ReturnedQty']*sales['UnitPriceEUR']*(1-sales['DiscountRate'])).round(2)
sales['NetSalesEUR']=(sales['SalesAfterDiscountEUR']-sales['RefundEUR']).round(2)

# %% 06 Calculate units, cost and profit
sales['NetUnits']=sales['Quantity']-sales['ReturnedQty']
sales['COGSEUR']=(sales['NetUnits']*sales['UnitCostEUR']).round(2)
sales['GrossProfitEUR']=(sales['NetSalesEUR']-sales['COGSEUR']).round(2)
sales['ContributionEUR']=(sales['GrossProfitEUR']-sales['ShippingCostEUR']).round(2)
sales['LineMargin']=sales['GrossProfitEUR'].div(sales['NetSalesEUR'].replace(0,np.nan))
sales['ReturnFlag']=sales['ReturnedQty'].gt(0).astype(int)

# %% 07 Filter rows for a business question
sales_2024=sales.loc[sales['Year'].eq(2024)].copy()
poland_online=sales.loc[sales['Year'].eq(2024)&sales['Country'].eq('Poland')&sales['Channel'].eq('E-commerce')]
print('Poland online 2024 sales:',round(poland_online['NetSalesEUR'].sum(),2))

# %% 08 Annual aggregation and weighted rates
annual=sales.groupby('Year',as_index=False).agg(
    NetSalesEUR=('NetSalesEUR','sum'),GrossProfitEUR=('GrossProfitEUR','sum'),
    ContributionEUR=('ContributionEUR','sum'),Orders=('OrderID','nunique'),
    Quantity=('Quantity','sum'),ReturnedQty=('ReturnedQty','sum'),NetUnits=('NetUnits','sum'))
annual['GrossMargin']=annual['GrossProfitEUR']/annual['NetSalesEUR']
annual['ReturnRate']=annual['ReturnedQty']/annual['Quantity']
annual['AverageOrderValueEUR']=annual['NetSalesEUR']/annual['Orders']
annual=annual.sort_values('Year')
annual['YoYGrowth']=annual['NetSalesEUR'].pct_change(fill_method=None)
print(annual.to_string(index=False))

# %% 09 Monthly trends and moving averages
monthly=sales.groupby(['Year','MonthStart'],as_index=False).agg(
    NetSalesEUR=('NetSalesEUR','sum'),GrossProfitEUR=('GrossProfitEUR','sum'))
monthly=monthly.sort_values('MonthStart')
monthly['MoMGrowth']=monthly['NetSalesEUR'].pct_change(fill_method=None)
monthly['YTDSales']=monthly.groupby('Year')['NetSalesEUR'].cumsum()
monthly['ThreeMonthAverage']=monthly['NetSalesEUR'].rolling(3,min_periods=1).mean()

# %% 10 Country and category rankings
country=sales_2024.groupby('Country',as_index=False).agg(NetSalesEUR=('NetSalesEUR','sum'),Orders=('OrderID','nunique'))
country=country.sort_values(['NetSalesEUR','Country'],ascending=[False,True])
category=sales_2024.groupby('Category',as_index=False).agg(NetSalesEUR=('NetSalesEUR','sum'),GrossProfitEUR=('GrossProfitEUR','sum'))
category['Share']=category['NetSalesEUR']/category['NetSalesEUR'].sum()
category['GrossMargin']=category['GrossProfitEUR']/category['NetSalesEUR']

# %% 11 Join customer segment descriptions safely
customers=pd.read_csv(DATA/'customers.csv')
enriched=sales.merge(customers,on='CustomerID',how='left',validate='many_to_one',indicator=True)
assert len(enriched)==len(sales)
assert enriched['_merge'].eq('both').all()
segments=enriched.loc[enriched['Year'].eq(2024)].groupby('CustomerSegment',as_index=False).agg(
    NetSalesEUR=('NetSalesEUR','sum'),ActiveCustomers=('CustomerID','nunique'),Orders=('OrderID','nunique'))

# %% 12 Compare years using a pivot table
region_year=sales.pivot_table(index='Region',columns='Year',values='NetSalesEUR',aggfunc='sum')
region_year['YoYGrowth']=region_year[2024]/region_year[2023]-1
print(region_year)

# %% 13 Aggregate sales before joining monthly targets
targets=pd.read_csv(DATA/'monthly_targets.csv',parse_dates=['MonthStart'])
actual=sales.groupby(['MonthStart','Region'],as_index=False).agg(NetSalesEUR=('NetSalesEUR','sum'))
target_comparison=targets.merge(actual,on=['MonthStart','Region'],how='left',validate='one_to_one',indicator=True)
assert target_comparison['_merge'].eq('both').all()
target_comparison['VarianceEUR']=target_comparison['NetSalesEUR']-target_comparison['TargetNetSalesEUR']
target_comparison['Attainment']=target_comparison['NetSalesEUR']/target_comparison['TargetNetSalesEUR']
under_target=target_comparison.loc[target_comparison['Attainment'].lt(1)].sort_values('VarianceEUR')

# %% 14 Returns and delivery analysis
returns=sales_2024.groupby('Category',as_index=False).agg(
    SoldUnits=('Quantity','sum'),ReturnedUnits=('ReturnedQty','sum'),RefundEUR=('RefundEUR','sum'),ReturnedLines=('ReturnFlag','sum'),Lines=('LineID','count'))
returns['UnitReturnRate']=returns['ReturnedUnits']/returns['SoldUnits']
returns['ReturnedLineRate']=returns['ReturnedLines']/returns['Lines']
delivery=sales_2024.assign(LateLine=sales_2024['DeliveryDays'].gt(7)).groupby('Channel',as_index=False).agg(
    AvgLineDeliveryDays=('DeliveryDays','mean'),LateLineRate=('LateLine','mean'))

# %% 15 Customer recency, frequency and monetary value
order_totals=sales_2024.groupby(['CustomerID','OrderID'],as_index=False).agg(
    OrderDate=('OrderDate','max'),NetSalesEUR=('NetSalesEUR','sum'))
rfm=order_totals.groupby('CustomerID',as_index=False).agg(
    LastOrderDate=('OrderDate','max'),Frequency=('OrderID','nunique'),MonetaryEUR=('NetSalesEUR','sum'))
rfm['RecencyDays']=(pd.Timestamp('2024-12-31')-rfm['LastOrderDate']).dt.days
rfm=rfm.sort_values('MonetaryEUR',ascending=False)

# %% 16 Detect unusually large order values
q1=order_totals['NetSalesEUR'].quantile(.25)
q3=order_totals['NetSalesEUR'].quantile(.75)
upper=q3+1.5*(q3-q1)
large_orders=order_totals.loc[order_totals['NetSalesEUR'].gt(upper)].copy()
# These are review candidates. Wholesale orders can be legitimately large.

# %% 17 Reusable function and a fixed-volume discount scenario
def summarise(frame,group_column):
    result=frame.groupby(group_column,as_index=False).agg(
        NetSalesEUR=('NetSalesEUR','sum'),GrossProfitEUR=('GrossProfitEUR','sum'))
    result['GrossMargin']=result['GrossProfitEUR'].div(result['NetSalesEUR'].replace(0,np.nan))
    return result.sort_values('NetSalesEUR',ascending=False)

channel_summary=summarise(sales_2024,'Channel')
scenario=sales_2024.copy()
scenario['ScenarioDiscount']=(scenario['DiscountRate']+.05).clip(upper=1)
scenario['ScenarioNetSalesEUR']=(scenario['NetUnits']*scenario['UnitPriceEUR']*(1-scenario['ScenarioDiscount'])).round(2)
scenario_impact=scenario.groupby('Category',as_index=False).agg(
    CurrentNetSalesEUR=('NetSalesEUR','sum'),ScenarioNetSalesEUR=('ScenarioNetSalesEUR','sum'))
scenario_impact['ChangeEUR']=scenario_impact['ScenarioNetSalesEUR']-scenario_impact['CurrentNetSalesEUR']

# %% 18 Reconcile with independent controls and SQL
checks=json.loads((ROOT/'results'/'expected_checks.json').read_text())
for row in annual.itertuples(index=False):
    expected=checks['years'][str(row.Year)]
    assert abs(row.NetSalesEUR-expected['NetSalesEUR'])<.01
    assert abs(row.GrossProfitEUR-expected['GrossProfitEUR'])<.01
    assert row.Orders==expected['FirstOrderFlag']
with sqlite3.connect(ROOT/'sql'/'puma_solution.sqlite') as con:
    sql_annual=pd.read_sql_query('SELECT Year,SUM(NetSalesEUR) AS SQLSales FROM v_sales GROUP BY Year',con)
comparison=annual.merge(sql_annual,on='Year',validate='one_to_one')
assert np.allclose(comparison['NetSalesEUR'],comparison['SQLSales'],atol=.01,rtol=0)
assert abs(sales['GrossSalesEUR'].sum()-sales['DiscountEUR'].sum()-sales['RefundEUR'].sum()-sales['NetSalesEUR'].sum())<.01

# %% 19 Create a four-panel dashboard figure
fig,axes=plt.subplots(2,2,figsize=(14,9),layout='constrained')
for year,frame in monthly.groupby('Year'):
    axes[0,0].plot(frame['MonthStart'].dt.month,frame['NetSalesEUR']/1000,marker='o',label=str(year))
axes[0,0].set(title='Monthly net sales',xlabel='Month',ylabel='EUR thousands',xticks=range(1,13));axes[0,0].legend()
top=country.head(6).sort_values('NetSalesEUR')
axes[0,1].barh(top['Country'],top['NetSalesEUR']/1000,color='#B3282D')
axes[0,1].set(title='Top six countries, 2024',xlabel='EUR thousands')
cat=category.sort_values('NetSalesEUR',ascending=False)
axes[1,0].bar(cat['Category'],cat['NetSalesEUR']/1000,color='#253746')
axes[1,0].set(title='Category net sales, 2024',ylabel='EUR thousands')
tc=target_comparison.loc[target_comparison['MonthStart'].dt.year.eq(2024)].groupby('MonthStart',as_index=False)[['NetSalesEUR','TargetNetSalesEUR']].sum()
axes[1,1].plot(tc['MonthStart'].dt.month,tc['NetSalesEUR']/1000,label='Actual')
axes[1,1].plot(tc['MonthStart'].dt.month,tc['TargetNetSalesEUR']/1000,label='Target',linestyle='--')
axes[1,1].set(title='Actual versus artificial target, 2024',xlabel='Month',ylabel='EUR thousands',xticks=range(1,13));axes[1,1].legend()
for ax in axes.flat:
    ax.spines[['top','right']].set_visible(False)
    ax.grid(axis='y',alpha=.2)
fig.suptitle('PUMA-themed sales practice | Simulated data',fontsize=16)
fig.savefig(OUT/'dashboard.png',dpi=160)
plt.close(fig)

# %% 20 Export reproducible analysis tables
outputs={'annual':annual,'monthly':monthly,'country_2024':country,'category_2024':category,'customer_segments':segments,
    'target_comparison':target_comparison,'under_target':under_target,'returns_2024':returns,'delivery_2024':delivery,
    'customer_rfm_2024':rfm,'large_orders_review':large_orders,'channel_2024':channel_summary,'discount_scenario':scenario_impact}
for name,frame in outputs.items():
    frame.to_csv(OUT/f'{name}.csv',index=False)
sales.to_csv(OUT/'sales_calculated.csv',index=False)
print('Complete: all annual controls and SQL comparisons passed. Reports are in results/python.')
