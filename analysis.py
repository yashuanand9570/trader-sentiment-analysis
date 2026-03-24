"""
Comprehensive Analysis: Trader Performance vs Market Sentiment
================================================================
This script analyzes the relationship between trader performance and 
Bitcoin market sentiment (Fear & Greed Index) to uncover patterns and 
deliver actionable trading insights.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set style for better visualizations
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

print("=" * 80)
print("TRADER PERFORMANCE vs MARKET SENTIMENT ANALYSIS")
print("=" * 80)

# =============================================================================
# 1. LOAD AND PREPROCESS DATA
# =============================================================================
print("\n[1/7] Loading and preprocessing data...")

# Load datasets
historical_data = pd.read_csv("historical_trader_data.csv")
fear_greed = pd.read_csv("fear_greed_index.csv")

# Convert timestamps
historical_data['Timestamp IST'] = pd.to_datetime(historical_data['Timestamp IST'], format='mixed')
historical_data['Timestamp'] = pd.to_datetime(historical_data['Timestamp'], unit='ms')
historical_data['Date'] = historical_data['Timestamp IST'].dt.date
historical_data['Date_dt'] = pd.to_datetime(historical_data['Date'])

fear_greed['date'] = pd.to_datetime(fear_greed['date'])
fear_greed['Date'] = fear_greed['date'].dt.date

# Create sentiment score mapping
sentiment_mapping = {
    'Extreme Fear': 1,
    'Fear': 2,
    'Neutral': 3,
    'Greed': 4,
    'Extreme Greed': 5
}
fear_greed['sentiment_score'] = fear_greed['classification'].map(sentiment_mapping)

# Extract date for merging
historical_data['trade_date'] = historical_data['Timestamp IST'].dt.date

print(f"   Historical data: {len(historical_data):,} trades")
print(f"   Fear & Greed data: {len(fear_greed):,} records")

# =============================================================================
# 2. MERGE DATASETS
# =============================================================================
print("\n[2/7] Merging datasets on date...")

# Merge on date
merged_data = historical_data.merge(
    fear_greed[['Date', 'value', 'classification', 'sentiment_score']],
    left_on='trade_date',
    right_on='Date',
    how='left'
)

# Drop duplicate date column
merged_data = merged_data.drop(columns=['Date_y'] if 'Date_y' in merged_data.columns else [])
if 'Date_x' in merged_data.columns:
    merged_data = merged_data.rename(columns={'Date_x': 'Date'})

print(f"   Merged data: {len(merged_data):,} trades with sentiment data")
print(f"   Missing sentiment data: {merged_data['value'].isnull().sum():,} ({merged_data['value'].isnull().mean()*100:.2f}%)")

# =============================================================================
# 3. BASIC STATISTICS AND OVERVIEW
# =============================================================================
print("\n[3/7] Computing basic statistics...")

# Overall performance metrics
total_pnl = merged_data['Closed PnL'].sum()
profitable_trades = (merged_data['Closed PnL'] > 0).sum()
total_trades_with_pnl = (merged_data['Closed PnL'] != 0).sum()
win_rate = profitable_trades / total_trades_with_pnl * 100 if total_trades_with_pnl > 0 else 0

print(f"\n   Overall Performance:")
print(f"   - Total PnL: ${total_pnl:,.2f}")
print(f"   - Total Trades: {len(merged_data):,}")
print(f"   - Profitable Trades: {profitable_trades:,} ({win_rate:.2f}%)")

# Sentiment distribution
print(f"\n   Sentiment Distribution:")
sentiment_counts = merged_data['classification'].value_counts()
for sentiment, count in sentiment_counts.items():
    if pd.notna(sentiment):
        print(f"   - {sentiment}: {count:,} trades ({count/len(merged_data)*100:.2f}%)")

# =============================================================================
# 4. PERFORMANCE BY SENTIMENT
# =============================================================================
print("\n[4/7] Analyzing performance by market sentiment...")

# Group by sentiment
sentiment_performance = merged_data.groupby('classification').agg({
    'Closed PnL': ['sum', 'mean', 'std', 'count'],
    'Size USD': 'mean',
    'Account': 'nunique'
}).round(2)

print("\n   Performance by Sentiment:")
print(sentiment_performance)

# Calculate win rate by sentiment
sentiment_win_rates = merged_data.groupby('classification').apply(
    lambda x: pd.Series({
        'Total Trades': len(x),
        'Profitable Trades': (x['Closed PnL'] > 0).sum(),
        'Win Rate (%)': (x['Closed PnL'] > 0).sum() / len(x) * 100 if len(x) > 0 else 0,
        'Total PnL': x['Closed PnL'].sum(),
        'Avg PnL per Trade': x['Closed PnL'].mean(),
        'Avg Trade Size (USD)': x['Size USD'].mean()
    })
).round(2)

print("\n   Win Rates by Sentiment:")
print(sentiment_win_rates)

# =============================================================================
# 5. PERFORMANCE BY SENTIMENT AND DIRECTION
# =============================================================================
print("\n[5/7] Analyzing performance by sentiment and trading direction...")

# Filter for directional trades (Long/Short)
directional_trades = merged_data[merged_data['Direction'].isin(['Open Long', 'Open Short', 'Close Long', 'Close Short'])]

direction_sentiment_perf = directional_trades.groupby(['classification', 'Direction']).agg({
    'Closed PnL': ['sum', 'mean', 'count'],
    'Size USD': 'mean'
}).round(2)

print("\n   Directional Trading Performance by Sentiment:")
print(direction_sentiment_perf)

# =============================================================================
# 6. TOP TRADERS ANALYSIS
# =============================================================================
print("\n[6/7] Analyzing top traders performance by sentiment...")

# Top traders by total PnL
top_traders = merged_data.groupby('Account').agg({
    'Closed PnL': 'sum',
    'Trade ID': 'count'
}).rename(columns={'Trade ID': 'Total Trades'}).sort_values('Closed PnL', ascending=False).head(10)

print("\n   Top 10 Traders by Total PnL:")
print(top_traders)

# Top traders performance by sentiment
top_trader_accounts = top_traders.index.tolist()
top_traders_sentiment = merged_data[merged_data['Account'].isin(top_trader_accounts)].groupby(
    ['Account', 'classification']
).agg({
    'Closed PnL': 'sum',
    'Trade ID': 'count'
}).reset_index()

print("\n   Top Traders Performance by Sentiment (sample):")
print(top_traders_sentiment.head(20))

# =============================================================================
# 7. GENERATE VISUALIZATIONS
# =============================================================================
print("\n[7/7] Generating visualizations...")

# Create figure with subplots
fig = plt.figure(figsize=(20, 16))

# 1. Total PnL by Sentiment
ax1 = fig.add_subplot(2, 3, 1)
sentiment_pnl = merged_data.groupby('classification')['Closed PnL'].sum().sort_values(ascending=False)
colors = plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(sentiment_pnl)))
bars = ax1.bar(range(len(sentiment_pnl)), sentiment_pnl.values, color=colors)
ax1.set_xticks(range(len(sentiment_pnl)))
ax1.set_xticklabels(sentiment_pnl.index, rotation=45, ha='right')
ax1.set_ylabel('Total PnL (USD)')
ax1.set_title('Total PnL by Market Sentiment', fontweight='bold')
ax1.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
for i, (idx, val) in enumerate(sentiment_pnl.items()):
    ax1.text(i, val, f'${val:,.0f}', ha='center', va='bottom' if val > 0 else 'top', fontsize=9)

# 2. Win Rate by Sentiment
ax2 = fig.add_subplot(2, 3, 2)
sentiment_win = sentiment_win_rates['Win Rate (%)']
colors = plt.cm.RdYlGn(sentiment_win.values / 100)
bars = ax2.bar(range(len(sentiment_win)), sentiment_win.values, color=colors)
ax2.set_xticks(range(len(sentiment_win)))
ax2.set_xticklabels(sentiment_win.index, rotation=45, ha='right')
ax2.set_ylabel('Win Rate (%)')
ax2.set_title('Win Rate by Market Sentiment', fontweight='bold')
ax2.set_ylim(0, 100)
for i, val in enumerate(sentiment_win.values):
    ax2.text(i, val, f'{val:.1f}%', ha='center', va='bottom', fontsize=9)

# 3. Average PnL per Trade by Sentiment
ax3 = fig.add_subplot(2, 3, 3)
sentiment_avg_pnl = merged_data.groupby('classification')['Closed PnL'].mean().sort_values(ascending=False)
colors = plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(sentiment_avg_pnl)))
bars = ax3.bar(range(len(sentiment_avg_pnl)), sentiment_avg_pnl.values, color=colors)
ax3.set_xticks(range(len(sentiment_avg_pnl)))
ax3.set_xticklabels(sentiment_avg_pnl.index, rotation=45, ha='right')
ax3.set_ylabel('Avg PnL per Trade (USD)')
ax3.set_title('Average PnL per Trade by Sentiment', fontweight='bold')
ax3.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
for i, val in enumerate(sentiment_avg_pnl.values):
    ax3.text(i, val, f'${val:.2f}', ha='center', va='bottom' if val > 0 else 'top', fontsize=8)

# 4. Trade Count by Sentiment
ax4 = fig.add_subplot(2, 3, 4)
sentiment_counts = merged_data['classification'].value_counts()
colors = plt.cm.Set3(np.linspace(0, 1, len(sentiment_counts)))
ax4.pie(sentiment_counts.values, labels=sentiment_counts.index, autopct='%1.1f%%', colors=colors)
ax4.set_title('Trade Distribution by Sentiment', fontweight='bold')

# 5. PnL Distribution by Sentiment (Box Plot)
ax5 = fig.add_subplot(2, 3, 5)
sentiment_order = ['Extreme Fear', 'Fear', 'Neutral', 'Greed', 'Extreme Greed']
pnl_by_sentiment = [merged_data[merged_data['classification'] == s]['Closed PnL'] for s in sentiment_order if s in merged_data['classification'].unique()]
labels = [s for s in sentiment_order if s in merged_data['classification'].unique()]
bp = ax5.boxplot(pnl_by_sentiment, labels=labels, patch_artist=True)
for patch, color in zip(bp['boxes'], colors[:len(labels)]):
    patch.set_facecolor(color)
ax5.set_ylabel('PnL (USD)')
ax5.set_title('PnL Distribution by Sentiment', fontweight='bold')
ax5.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
plt.setp(ax5.xaxis.get_majorticklabels(), rotation=45, ha='right')

# 6. Cumulative PnL Over Time by Sentiment
ax6 = fig.add_subplot(2, 3, 6)
merged_sorted = merged_data.sort_values('Timestamp IST')
for sentiment in merged_data['classification'].unique():
    if pd.notna(sentiment):
        subset = merged_sorted[merged_sorted['classification'] == sentiment]
        cumulative_pnl = subset['Closed PnL'].cumsum()
        ax6.plot(subset['Timestamp IST'], cumulative_pnl, label=sentiment, linewidth=2)
ax6.set_xlabel('Date')
ax6.set_ylabel('Cumulative PnL (USD)')
ax6.set_title('Cumulative PnL Over Time by Sentiment', fontweight='bold')
ax6.legend(loc='upper left', fontsize=8)
ax6.tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.savefig('sentiment_analysis_overview.png', dpi=150, bbox_inches='tight')
print("   Saved: sentiment_analysis_overview.png")

# Additional visualization: Heatmap of performance
fig2, ax = plt.subplots(figsize=(12, 8))

# Create pivot table for heatmap
pivot_data = merged_data.groupby(['classification', 'Direction'])['Closed PnL'].agg(['sum', 'mean', 'count']).reset_index()
pivot_data = pivot_data[pivot_data['Direction'].isin(['Open Long', 'Open Short', 'Close Long', 'Close Short'])]
heatmap_data = merged_data[merged_data['Direction'].isin(['Open Long', 'Open Short', 'Close Long', 'Close Short'])]
heatmap_pivot = heatmap_data.pivot_table(
    values='Closed PnL',
    index='classification',
    columns='Direction',
    aggfunc='sum',
    fill_value=0
)

sns.heatmap(heatmap_pivot, annot=True, fmt='.0f', cmap='RdYlGn', center=0, ax=ax)
ax.set_title('Total PnL by Sentiment and Direction', fontweight='bold', fontsize=14)
ax.set_xlabel('Direction', fontsize=12)
ax.set_ylabel('Market Sentiment', fontsize=12)
plt.tight_layout()
plt.savefig('sentiment_direction_heatmap.png', dpi=150, bbox_inches='tight')
print("   Saved: sentiment_direction_heatmap.png")

# Top traders visualization
fig3, axes = plt.subplots(1, 2, figsize=(16, 6))

# Top 10 traders total PnL
top10_traders = merged_data.groupby('Account')['Closed PnL'].sum().sort_values(ascending=False).head(10)
colors = ['green' if x > 0 else 'red' for x in top10_traders.values]
axes[0].barh(range(len(top10_traders)), top10_traders.values, color=colors)
axes[0].set_yticks(range(len(top10_traders)))
axes[0].set_yticklabels([f"{x[:8]}..." for x in top10_traders.index])
axes[0].set_xlabel('Total PnL (USD)')
axes[0].set_title('Top 10 Traders by Total PnL', fontweight='bold')
axes[0].axvline(x=0, color='black', linestyle='-', linewidth=0.5)

# Top 10 traders by sentiment
top10_accounts = top10_traders.index.tolist()
top10_sentiment = merged_data[merged_data['Account'].isin(top10_accounts)].groupby(
    ['Account', 'classification']
)['Closed PnL'].sum().unstack(fill_value=0)

sns.heatmap(top10_sentiment, annot=True, fmt='.0f', cmap='RdYlGn', center=0, ax=axes[1])
axes[1].set_title('Top 10 Traders PnL by Sentiment', fontweight='bold')
axes[1].set_xlabel('Sentiment', fontsize=12)
axes[1].set_ylabel('Trader Account', fontsize=12)
plt.setp(axes[1].xaxis.get_majorticklabels(), rotation=45, ha='right')

plt.tight_layout()
plt.savefig('top_traders_analysis.png', dpi=150, bbox_inches='tight')
print("   Saved: top_traders_analysis.png")

# =============================================================================
# 8. SAVE DETAILED RESULTS
# =============================================================================
print("\n[8/8] Saving detailed results...")

# Save sentiment performance summary
sentiment_win_rates.to_csv('sentiment_performance_summary.csv')
print("   Saved: sentiment_performance_summary.csv")

# Save top traders analysis
top_traders.to_csv('top_traders_summary.csv')
print("   Saved: top_traders_summary.csv")

# Save merged dataset for further analysis
merged_data.to_csv('merged_trader_sentiment_data.csv', index=False)
print("   Saved: merged_trader_sentiment_data.csv")

# =============================================================================
# SUMMARY AND INSIGHTS
# =============================================================================
print("\n" + "=" * 80)
print("KEY INSIGHTS SUMMARY")
print("=" * 80)

best_sentiment = sentiment_win_rates['Total PnL'].idxmax()
worst_sentiment = sentiment_win_rates['Total PnL'].idxmin()
best_win_rate_sentiment = sentiment_win_rates['Win Rate (%)'].idxmax()

print(f"""
1. OVERALL PERFORMANCE:
   - Total PnL across all trades: ${total_pnl:,.2f}
   - Overall win rate: {win_rate:.2f}%
   - Total trades analyzed: {len(merged_data):,}

2. BEST PERFORMING SENTIMENT:
   - Highest Total PnL: {best_sentiment} (${sentiment_win_rates.loc[best_sentiment, 'Total PnL']:,.2f})
   - Best Win Rate: {best_win_rate_sentiment} ({sentiment_win_rates.loc[best_win_rate_sentiment, 'Win Rate (%)']:.2f}%)

3. WORST PERFORMING SENTIMENT:
   - Lowest Total PnL: {worst_sentiment} (${sentiment_win_rates.loc[worst_sentiment, 'Total PnL']:,.2f})

4. TRADING ACTIVITY BY SENTIMENT:
   - Most active sentiment: {sentiment_counts.index[0]} ({sentiment_counts.values[0]:,} trades)
   - Least active sentiment: {sentiment_counts.index[-1]} ({sentiment_counts.values[-1]:,} trades)

5. TOP PERFORMERS:
   - Best trader: {top_traders.index[0][:10]}... (${top_traders.iloc[0]['Closed PnL']:,.2f})
   - Most active trader: {merged_data.groupby('Account').size().sort_values(ascending=False).index[0][:10]}...

6. RISK OBSERVATIONS:
   - Highest average PnL volatility: {merged_data.groupby('classification')['Closed PnL'].std().idxmax()}
   - Most consistent sentiment: {merged_data.groupby('classification')['Closed PnL'].std().idxmin()}
""")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE!")
print("=" * 80)
print("\nGenerated files:")
print("  - sentiment_analysis_overview.png")
print("  - sentiment_direction_heatmap.png")
print("  - top_traders_analysis.png")
print("  - sentiment_performance_summary.csv")
print("  - top_traders_summary.csv")
print("  - merged_trader_sentiment_data.csv")
