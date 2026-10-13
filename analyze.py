from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data' / 'Online Retail.xlsx'
CHARTS = ROOT / 'charts'
TABLES = ROOT / 'tables'
CHARTS.mkdir(exist_ok=True)
TABLES.mkdir(exist_ok=True)

# ---------- Load and clean ----------
df = pd.read_excel(DATA)
df.columns = [c.strip() for c in df.columns]
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
df['InvoiceNo'] = df['InvoiceNo'].astype(str)
df['is_cancelled'] = df['InvoiceNo'].str.startswith('C')
df['Revenue'] = df['Quantity'] * df['UnitPrice']

raw_rows = len(df)
raw_invoices = df['InvoiceNo'].nunique()
clean = df[(~df['is_cancelled']) & (df['Quantity'] > 0) & (df['UnitPrice'] > 0)].copy()
clean['Month'] = clean['InvoiceDate'].dt.to_period('M').dt.to_timestamp()
clean['DayOfWeek'] = clean['InvoiceDate'].dt.day_name()
clean['Hour'] = clean['InvoiceDate'].dt.hour
clean['Revenue'] = clean['Quantity'] * clean['UnitPrice']

# ---------- KPI calculations ----------
positive_invoices = clean['InvoiceNo'].nunique()
cancelled_invoices = df.loc[df['is_cancelled'], 'InvoiceNo'].nunique()
metrics = {
    'raw_rows': int(raw_rows),
    'raw_invoices': int(raw_invoices),
    'analysis_rows': int(len(clean)),
    'analysis_invoices': int(positive_invoices),
    'cancelled_invoices': int(cancelled_invoices),
    'cancellation_rate_pct': round(cancelled_invoices / (positive_invoices + cancelled_invoices) * 100, 1),
    'gross_revenue_gbp': round(float(clean['Revenue'].sum()), 2),
    'customers_with_id': int(clean['CustomerID'].nunique()),
    'products': int(clean['StockCode'].nunique()),
    'countries': int(clean['Country'].nunique()),
    'date_start': clean['InvoiceDate'].min().strftime('%d %b %Y'),
    'date_end': clean['InvoiceDate'].max().strftime('%d %b %Y'),
    'average_order_value_gbp': round(float(clean.groupby('InvoiceNo')['Revenue'].sum().mean()), 2),
}

# ---------- Tables ----------
monthly = clean.groupby('Month', as_index=False).agg(Revenue=('Revenue','sum'), Orders=('InvoiceNo','nunique'), Units=('Quantity','sum'))
monthly['AOV'] = monthly['Revenue'] / monthly['Orders']
monthly.to_csv(TABLES/'monthly_revenue.csv', index=False)

top_products = clean.groupby(['StockCode','Description'], as_index=False).agg(Revenue=('Revenue','sum'), Units=('Quantity','sum'), Orders=('InvoiceNo','nunique'))
top_products = top_products.sort_values('Revenue', ascending=False).head(10)
top_products.to_csv(TABLES/'top_products.csv', index=False)

top_countries = clean.groupby('Country', as_index=False).agg(Revenue=('Revenue','sum'), Orders=('InvoiceNo','nunique'), Customers=('CustomerID','nunique')).sort_values('Revenue', ascending=False)
top_countries.to_csv(TABLES/'top_countries.csv', index=False)

# RFM segmentation (customers with identifiable IDs only)
customer = clean.dropna(subset=['CustomerID']).copy()
snapshot = customer['InvoiceDate'].max() + pd.Timedelta(days=1)
rfm = customer.groupby('CustomerID').agg(
    Recency=('InvoiceDate', lambda x: (snapshot - x.max()).days),
    Frequency=('InvoiceNo','nunique'),
    Monetary=('Revenue','sum')
).reset_index()
# rank-based quintiles; duplicates are handled using rank first
for col, ascending in [('Recency', False), ('Frequency', True), ('Monetary', True)]:
    rfm[col+'_score'] = pd.qcut(rfm[col].rank(method='first'), 5, labels=[1,2,3,4,5]).astype(int)
# recency should be lower-is-better, invert score
rfm['R_score'] = 6 - rfm['Recency_score']
rfm['F_score'] = rfm['Frequency_score']
rfm['M_score'] = rfm['Monetary_score']
rfm['RFM_score'] = rfm[['R_score','F_score','M_score']].sum(axis=1)

def segment(row):
    if row.R_score >= 4 and row.F_score >= 4 and row.M_score >= 4:
        return 'Champions'
    if row.R_score >= 4 and row.F_score >= 3:
        return 'Loyal / active'
    if row.R_score >= 4 and row.F_score <= 2:
        return 'New / promising'
    if row.R_score <= 2 and row.F_score >= 3:
        return 'At risk'
    return 'Needs reactivation'
rfm['Segment'] = rfm.apply(segment, axis=1)
rfm.to_csv(TABLES/'customer_rfm.csv', index=False)
segment_summary = rfm.groupby('Segment', as_index=False).agg(Customers=('CustomerID','count'), Revenue=('Monetary','sum'), Avg_Recency_Days=('Recency','mean'), Avg_Orders=('Frequency','mean')).sort_values('Revenue', ascending=False)
segment_summary['Revenue_Share_Pct'] = segment_summary['Revenue'] / segment_summary['Revenue'].sum() * 100
segment_summary.to_csv(TABLES/'segment_summary.csv', index=False)

# ---------- Chart style ----------
plt.rcParams.update({'font.family':'DejaVu Sans','axes.titlesize':13,'axes.labelsize':10,'xtick.labelsize':9,'ytick.labelsize':9})
NAVY = '#102A43'; TEAL = '#0F766E'; BLUE = '#2F80ED'; ORANGE = '#F2994A'; RED = '#D64545'; GREY = '#627D98'; LIGHT = '#EAF2F8'

def savefig(name):
    plt.tight_layout()
    plt.savefig(CHARTS/name, dpi=220, bbox_inches='tight', facecolor='white')
    plt.close()

def money(x, pos): return f'£{x/1e6:.1f}M' if abs(x) >= 1e6 else f'£{x/1e3:.0f}K'

# 1 monthly revenue
fig, ax = plt.subplots(figsize=(9.4,4.4))
ax.plot(monthly['Month'], monthly['Revenue'], color=TEAL, linewidth=2.5, marker='o', markersize=3)
ax.fill_between(monthly['Month'], monthly['Revenue'], color=TEAL, alpha=.10)
ax.yaxis.set_major_formatter(FuncFormatter(money)); ax.set_title('Revenue accelerated into the holiday season'); ax.set_ylabel('Gross revenue'); ax.grid(axis='y', alpha=.2); ax.spines[['top','right']].set_visible(False)
ax.annotate('Peak month', xy=(monthly.loc[monthly.Revenue.idxmax(),'Month'], monthly.Revenue.max()), xytext=(-50,25), textcoords='offset points', arrowprops=dict(arrowstyle='->', color=GREY), fontsize=9, color=NAVY)
savefig('01_monthly_revenue.png')

# 2 top products
fig, ax = plt.subplots(figsize=(9.4,5.0))
tp = top_products.sort_values('Revenue')
labels = [str(x)[:34] for x in tp['Description'].fillna('Unknown')]
ax.barh(labels, tp['Revenue'], color=BLUE)
ax.xaxis.set_major_formatter(FuncFormatter(money)); ax.set_title('Top products by gross revenue'); ax.set_xlabel('Gross revenue'); ax.spines[['top','right']].set_visible(False); ax.grid(axis='x', alpha=.2)
savefig('02_top_products.png')

# 3 country share
fig, ax = plt.subplots(figsize=(9.4,4.8))
tc = top_countries.head(8).sort_values('Revenue')
ax.barh(tc['Country'], tc['Revenue'], color=ORANGE)
ax.xaxis.set_major_formatter(FuncFormatter(money)); ax.set_title('The UK dominates revenue; international markets are smaller but diversified'); ax.set_xlabel('Gross revenue'); ax.spines[['top','right']].set_visible(False); ax.grid(axis='x', alpha=.2)
savefig('03_top_countries.png')

# 4 RFM segment
fig, ax = plt.subplots(figsize=(9.4,4.8))
ss = segment_summary.sort_values('Revenue')
colors = [RED if s == 'At risk' else TEAL if s in ['Champions','Loyal / active'] else BLUE if s == 'New / promising' else GREY for s in ss['Segment']]
ax.barh(ss['Segment'], ss['Revenue'], color=colors)
ax.xaxis.set_major_formatter(FuncFormatter(money)); ax.set_title('Active and loyal customers account for most identified-customer value'); ax.set_xlabel('Revenue'); ax.spines[['top','right']].set_visible(False); ax.grid(axis='x', alpha=.2)
savefig('04_rfm_segments.png')

# 5 day/hour heatmap
heat = clean.pivot_table(index='DayOfWeek', columns='Hour', values='InvoiceNo', aggfunc='nunique', fill_value=0)
order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
heat = heat.reindex(order).fillna(0)
fig, ax = plt.subplots(figsize=(9.4,3.9))
im = ax.imshow(heat.values, aspect='auto', cmap='YlGnBu')
ax.set_yticks(range(len(heat.index)), [x[:3] for x in heat.index]); ax.set_xticks(range(len(heat.columns)), heat.columns)
ax.set_title('Order activity is concentrated in weekday business hours'); ax.set_xlabel('Hour of day'); ax.set_ylabel('Day'); fig.colorbar(im, ax=ax, label='Distinct orders')
savefig('05_order_heatmap.png')

# ---------- narrative-ready highlights ----------
peak = monthly.loc[monthly['Revenue'].idxmax()]
lowest = monthly.loc[monthly['Revenue'].idxmin()]
uk_share = top_countries.loc[top_countries['Country'].eq('United Kingdom'),'Revenue'].iloc[0] / clean['Revenue'].sum() * 100
champ = segment_summary[segment_summary['Segment'].eq('Champions')].iloc[0]
loyal = segment_summary[segment_summary['Segment'].eq('Loyal / active')].iloc[0]
at_risk = segment_summary[segment_summary['Segment'].eq('At risk')].iloc[0]
insights = {
    'peak_month': peak['Month'].strftime('%B %Y'), 'peak_revenue_gbp': round(float(peak['Revenue']),2),
    'lowest_month': lowest['Month'].strftime('%B %Y'), 'lowest_revenue_gbp': round(float(lowest['Revenue']),2),
    'uk_revenue_share_pct': round(float(uk_share),1),
    'champions_customers': int(champ['Customers']), 'champions_revenue_gbp': round(float(champ['Revenue']),2),
    'loyal_customers': int(loyal['Customers']), 'loyal_revenue_gbp': round(float(loyal['Revenue']),2),
    'at_risk_customers': int(at_risk['Customers']), 'at_risk_revenue_gbp': round(float(at_risk['Revenue']),2),
    'top_product': str(top_products.iloc[0]['Description']), 'top_product_revenue_gbp': round(float(top_products.iloc[0]['Revenue']),2),
    'top_product_orders': int(top_products.iloc[0]['Orders']),
}
(ROOT/'metrics.json').write_text(json.dumps(metrics, indent=2))
(ROOT/'insights.json').write_text(json.dumps(insights, indent=2))
print(json.dumps({'metrics':metrics,'insights':insights}, indent=2))
