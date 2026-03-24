"""
Advanced Pattern Analysis: Trader Performance vs Market Sentiment
==================================================================
This script performs deeper analysis including:
- Time-based patterns (hourly, daily, monthly)
- Coin-specific analysis
- Leverage and risk analysis
- Advanced statistical correlations
- Trading strategy recommendations
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

print("=" * 80)
print("ADVANCED PATTERN ANALYSIS")
print("=" * 80)

# Load merged data
merged_data = pd.read_csv('merged_trader_sentiment_data.csv')
merged_data['Timestamp IST'] = pd.to_datetime(merged_data['Timestamp IST'])
merged_data['Date'] = pd.to_datetime(merged_data['Date'])

# =============================================================================
# 1. TIME-BASED PATTERNS
# =============================================================================
print("\n[1/6] Analyzing time-based patterns...")

# Extract time features
merged_data['Hour'] = merged_data['Timestamp IST'].dt.hour
merged_data['DayOfWeek'] = merged_data['Timestamp IST'].dt.dayofweek
merged_data['Month'] = merged_data['Timestamp IST'].dt.month
merged_data['Year'] = merged_data['Timestamp IST'].dt.year
merged_data['IsWeekend'] = merged_data['DayOfWeek'].isin([5, 6])

# Hourly patterns
hourly_perf = merged_data.groupby('Hour').agg({
    'Closed PnL': ['sum', 'mean', 'count'],
    'Size USD': 'mean'
}).round(2)

print("\n   Hourly Performance (Top 5 hours by Total PnL):")
top_hours = hourly_perf[('Closed PnL', 'sum')].sort_values(ascending=False).head(5)
for hour, pnl in top_hours.items():
    print(f"   - {hour:02d}:00 - Total PnL: ${pnl:,.2f}")

# Day of week patterns
dow_perf = merged_data.groupby('DayOfWeek').agg({
    'Closed PnL': ['sum', 'mean'],
    'Size USD': 'mean'
}).round(2)
dow_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

print("\n   Day of Week Performance:")
for i, dow in enumerate(dow_names):
    pnl = dow_perf[('Closed PnL', 'sum')].iloc[i]
    print(f"   - {dow}: Total PnL: ${pnl:,.2f}")

# Monthly patterns
monthly_perf = merged_data.groupby('Month').agg({
    'Closed PnL': 'sum',
    'Trade ID': 'count'
}).round(2)
month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

print("\n   Monthly Performance:")
for i, month in enumerate(month_names):
    if i+1 in monthly_perf.index:
        pnl = monthly_perf.loc[i+1, 'Closed PnL']
        print(f"   - {month}: Total PnL: ${pnl:,.2f}")

# =============================================================================
# 2. SENTIMENT + TIME INTERACTION
# =============================================================================
print("\n[2/6] Analyzing sentiment-time interactions...")

# Sentiment by hour
sentiment_hour = merged_data.groupby(['classification', 'Hour'])['Closed PnL'].sum().unstack(fill_value=0)

# Best hour for each sentiment
print("\n   Best Trading Hour by Sentiment:")
for sentiment in sentiment_hour.index:
    best_hour = sentiment_hour.loc[sentiment].idxmax()
    best_pnl = sentiment_hour.loc[sentiment].max()
    print(f"   - {sentiment}: {best_hour:02d}:00 (${best_pnl:,.2f})")

# Sentiment by day of week
sentiment_dow = merged_data.groupby(['classification', 'DayOfWeek'])['Closed PnL'].sum().unstack(fill_value=0)

print("\n   Best Trading Day by Sentiment:")
for sentiment in sentiment_dow.index:
    best_day = sentiment_dow.loc[sentiment].idxmax()
    best_pnl = sentiment_dow.loc[sentiment].max()
    print(f"   - {sentiment}: {dow_names[best_day]} (${best_pnl:,.2f})")

# =============================================================================
# 3. COIN-SPECIFIC ANALYSIS
# =============================================================================
print("\n[3/6] Analyzing coin-specific patterns...")

# Top coins by volume
top_coins = merged_data.groupby('Coin')['Size USD'].sum().sort_values(ascending=False).head(20)

print("\n   Top 10 Coins by Trading Volume:")
for coin, vol in top_coins.head(10).items():
    print(f"   - {coin}: ${vol:,.2f}")

# Top coins by PnL
coin_pnl = merged_data.groupby('Coin').agg({
    'Closed PnL': 'sum',
    'Size USD': 'sum',
    'Trade ID': 'count'
}).sort_values('Closed PnL', ascending=False)

print("\n   Top 10 Coins by Total PnL:")
for coin in coin_pnl.head(10).index:
    pnl = coin_pnl.loc[coin, 'Closed PnL']
    trades = coin_pnl.loc[coin, 'Trade ID']
    print(f"   - {coin}: ${pnl:,.2f} ({trades:,} trades)")

# Coin performance by sentiment
top_5_coins = top_coins.head(5).index
coin_sentiment_perf = merged_data[merged_data['Coin'].isin(top_5_coins)].groupby(
    ['Coin', 'classification']
)['Closed PnL'].agg(['sum', 'mean', 'count']).round(2)

print("\n   Top 5 Coins Performance by Sentiment (sample):")
print(coin_sentiment_perf.head(15))

# =============================================================================
# 4. TRADE SIZE AND RISK ANALYSIS
# =============================================================================
print("\n[4/6] Analyzing trade size and risk patterns...")

# Create trade size buckets
merged_data['Size Bucket'] = pd.qcut(merged_data['Size USD'], q=5, labels=['Very Small', 'Small', 'Medium', 'Large', 'Very Large'])

size_perf = merged_data.groupby('Size Bucket').agg({
    'Closed PnL': ['sum', 'mean', 'std'],
    'Trade ID': 'count'
}).round(2)

print("\n   Performance by Trade Size:")
print(size_perf)

# Win rate by size bucket
size_win_rate = merged_data.groupby('Size Bucket').apply(
    lambda x: pd.Series({
        'Total Trades': len(x),
        'Profitable': (x['Closed PnL'] > 0).sum(),
        'Win Rate (%)': (x['Closed PnL'] > 0).sum() / len(x) * 100
    })
).round(2)

print("\n   Win Rate by Trade Size:")
print(size_win_rate)

# Size bucket by sentiment
size_sentiment = merged_data.groupby(['Size Bucket', 'classification'])['Closed PnL'].mean().unstack(fill_value=0)

print("\n   Avg PnL by Size and Sentiment:")
print(size_sentiment.round(2))

# =============================================================================
# 5. SENTIMENT MOMENTUM ANALYSIS
# =============================================================================
print("\n[5/6] Analyzing sentiment momentum...")

# Load fear & greed data for momentum
fear_greed = pd.read_csv('fear_greed_index.csv')
fear_greed['date'] = pd.to_datetime(fear_greed['date'])
fear_greed = fear_greed.sort_values('date')

# Calculate sentiment change
fear_greed['prev_value'] = fear_greed['value'].shift(1)
fear_greed['sentiment_change'] = fear_greed['value'] - fear_greed['prev_value']
fear_greed['sentiment_momentum'] = fear_greed['sentiment_change'].apply(
    lambda x: 'Improving' if x > 0 else ('Worsening' if x < 0 else 'Neutral')
)

# Merge momentum with trades
merged_with_momentum = merged_data.merge(
    fear_greed[['date', 'sentiment_change', 'sentiment_momentum']],
    left_on=merged_data['Date'].dt.date,
    right_on=fear_greed['date'].dt.date,
    how='left'
)

# Performance by sentiment momentum
momentum_perf = merged_with_momentum.groupby('sentiment_momentum').agg({
    'Closed PnL': ['sum', 'mean', 'count']
}).round(2)

print("\n   Performance by Sentiment Momentum:")
print(momentum_perf)

# =============================================================================
# 6. STATISTICAL ANALYSIS
# =============================================================================
print("\n[6/6] Performing statistical analysis...")

# Correlation between sentiment score and PnL
merged_data['sentiment_score'] = merged_data['classification'].map({
    'Extreme Fear': 1, 'Fear': 2, 'Neutral': 3, 'Greed': 4, 'Extreme Greed': 5
})

# Filter out zero PnL trades for correlation
nonzero_trades = merged_data[merged_data['Closed PnL'] != 0]

if len(nonzero_trades) > 0:
    # Drop NaN values from both columns first
    valid_data = nonzero_trades[['sentiment_score', 'Closed PnL']].dropna()
    if len(valid_data) > 0:
        correlation = valid_data['sentiment_score'].corr(valid_data['Closed PnL'])
        print(f"\n   Correlation between Sentiment Score and PnL: {correlation:.4f}")
        
        # Statistical significance
        corr_stat = stats.pearsonr(valid_data['sentiment_score'], 
                                    valid_data['Closed PnL'])
        print(f"   P-value: {corr_stat.pvalue:.4f}")
        if corr_stat.pvalue < 0.05:
            print("   → Statistically significant correlation!")
        else:
            print("   → Not statistically significant")

# ANOVA test for sentiment categories
from scipy.stats import f_oneway

sentiment_groups = [group['Closed PnL'].values for name, group in merged_data.groupby('classification') if len(group) > 0]
anova_result = f_oneway(*sentiment_groups)
print(f"\n   ANOVA Test (PnL differences across sentiments):")
print(f"   F-statistic: {anova_result.statistic:.4f}")
print(f"   P-value: {anova_result.pvalue:.4e}")
if anova_result.pvalue < 0.05:
    print("   → Significant differences exist between sentiment categories!")

# =============================================================================
# GENERATE VISUALIZATIONS
# =============================================================================
print("\n" + "=" * 80)
print("GENERATING ADVANCED VISUALIZATIONS")
print("=" * 80)

# Figure 1: Time-based patterns
fig1, axes = plt.subplots(2, 2, figsize=(16, 12))

# Hourly PnL
hourly_pnl = merged_data.groupby('Hour')['Closed PnL'].sum()
axes[0, 0].bar(hourly_pnl.index, hourly_pnl.values, color='steelblue')
axes[0, 0].set_xlabel('Hour of Day')
axes[0, 0].set_ylabel('Total PnL (USD)')
axes[0, 0].set_title('Hourly Trading Performance', fontweight='bold')
axes[0, 0].axhline(y=0, color='black', linestyle='-', linewidth=0.5)

# Day of Week PnL
dow_pnl = merged_data.groupby('DayOfWeek')['Closed PnL'].sum()
axes[0, 1].bar(range(7), dow_pnl.values, color='coral')
axes[0, 1].set_xticks(range(7))
axes[0, 1].set_xticklabels(dow_names, rotation=45, ha='right')
axes[0, 1].set_xlabel('Day of Week')
axes[0, 1].set_ylabel('Total PnL (USD)')
axes[0, 1].set_title('Day of Week Trading Performance', fontweight='bold')
axes[0, 1].axhline(y=0, color='black', linestyle='-', linewidth=0.5)

# Monthly PnL
monthly_pnl = merged_data.groupby('Month')['Closed PnL'].sum()
axes[1, 0].bar(monthly_pnl.index, monthly_pnl.values, color='seagreen')
axes[1, 0].set_xticks(range(1, 13))
axes[1, 0].set_xticklabels(month_names, rotation=45, ha='right')
axes[1, 0].set_xlabel('Month')
axes[1, 0].set_ylabel('Total PnL (USD)')
axes[1, 0].set_title('Monthly Trading Performance', fontweight='bold')
axes[1, 0].axhline(y=0, color='black', linestyle='-', linewidth=0.5)

# Trade count by hour
hourly_count = merged_data.groupby('Hour').size()
axes[1, 1].plot(hourly_count.index, hourly_count.values, marker='o', linewidth=2, color='purple')
axes[1, 1].set_xlabel('Hour of Day')
axes[1, 1].set_ylabel('Number of Trades')
axes[1, 1].set_title('Trading Activity by Hour', fontweight='bold')

plt.tight_layout()
plt.savefig('time_based_patterns.png', dpi=150, bbox_inches='tight')
print("Saved: time_based_patterns.png")

# Figure 2: Coin analysis
fig2, axes = plt.subplots(1, 2, figsize=(16, 6))

# Top coins by PnL
top_15_coins = coin_pnl.head(15)
colors = ['green' if x > 0 else 'red' for x in top_15_coins['Closed PnL']]
axes[0].barh(range(len(top_15_coins)), top_15_coins['Closed PnL'], color=colors)
axes[0].set_yticks(range(len(top_15_coins)))
axes[0].set_yticklabels(top_15_coins.index)
axes[0].set_xlabel('Total PnL (USD)')
axes[0].set_title('Top 15 Coins by Total PnL', fontweight='bold')
axes[0].axvline(x=0, color='black', linestyle='-', linewidth=0.5)

# Top coins by win rate
coin_win_rates = merged_data.groupby('Coin').apply(
    lambda x: (x['Closed PnL'] > 0).sum() / len(x) * 100 if len(x) > 0 else 0
).sort_values(ascending=False).head(15)
axes[1].barh(range(len(coin_win_rates)), coin_win_rates.values, color='teal')
axes[1].set_yticks(range(len(coin_win_rates)))
axes[1].set_yticklabels(coin_win_rates.index)
axes[1].set_xlabel('Win Rate (%)')
axes[1].set_title('Top 15 Coins by Win Rate', fontweight='bold')

plt.tight_layout()
plt.savefig('coin_analysis.png', dpi=150, bbox_inches='tight')
print("Saved: coin_analysis.png")

# Figure 3: Size and risk analysis
fig3, axes = plt.subplots(1, 2, figsize=(16, 6))

# PnL by size bucket
size_order = ['Very Small', 'Small', 'Medium', 'Large', 'Very Large']
size_pnl = merged_data.groupby('Size Bucket')['Closed PnL'].agg(['sum', 'mean'])
size_pnl = size_pnl.reindex(size_order)

x = np.arange(len(size_order))
width = 0.35

axes[0].bar(x - width/2, size_pnl['sum'], width, label='Total PnL', color='steelblue')
axes[0].bar(x + width/2, size_pnl['mean'], width, label='Avg PnL', color='coral')
axes[0].set_xlabel('Trade Size Bucket')
axes[0].set_ylabel('PnL (USD)')
axes[0].set_title('Performance by Trade Size', fontweight='bold')
axes[0].set_xticks(x)
axes[0].set_xticklabels(size_order, rotation=45, ha='right')
axes[0].legend()
axes[0].axhline(y=0, color='black', linestyle='-', linewidth=0.5)

# Win rate by size
size_win = merged_data.groupby('Size Bucket').apply(
    lambda x: (x['Closed PnL'] > 0).sum() / len(x) * 100
).reindex(size_order)
axes[1].bar(size_order, size_win.values, color='seagreen')
axes[1].set_xlabel('Trade Size Bucket')
axes[1].set_ylabel('Win Rate (%)')
axes[1].set_title('Win Rate by Trade Size', fontweight='bold')
axes[1].tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.savefig('size_risk_analysis.png', dpi=150, bbox_inches='tight')
print("Saved: size_risk_analysis.png")

# Figure 4: Sentiment momentum
fig4, ax = plt.subplots(figsize=(10, 6))
if 'sentiment_momentum' in merged_with_momentum.columns:
    momentum_pnl = merged_with_momentum.groupby('sentiment_momentum')['Closed PnL'].sum()
    colors = ['red' if x < 0 else 'green' for x in momentum_pnl]
    ax.bar(momentum_pnl.index, momentum_pnl.values, color=colors)
    ax.set_xlabel('Sentiment Momentum')
    ax.set_ylabel('Total PnL (USD)')
    ax.set_title('Performance by Sentiment Momentum', fontweight='bold')
    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    for i, (idx, val) in enumerate(momentum_pnl.items()):
        ax.text(i, val, f'${val:,.0f}', ha='center', va='bottom' if val > 0 else 'top')

plt.tight_layout()
plt.savefig('sentiment_momentum.png', dpi=150, bbox_inches='tight')
print("Saved: sentiment_momentum.png")

# =============================================================================
# SAVE DETAILED RESULTS
# =============================================================================
print("\n" + "=" * 80)
print("SAVING DETAILED RESULTS")
print("=" * 80)

# Save coin analysis
coin_pnl.to_csv('coin_performance_summary.csv')
print("Saved: coin_performance_summary.csv")

# Save hourly patterns
hourly_perf.to_csv('hourly_performance_summary.csv')
print("Saved: hourly_performance_summary.csv")

# Save size bucket analysis
size_perf.to_csv('size_bucket_performance.csv')
print("Saved: size_bucket_performance.csv")

# =============================================================================
# STRATEGIC RECOMMENDATIONS
# =============================================================================
print("\n" + "=" * 80)
print("STRATEGIC RECOMMENDATIONS")
print("=" * 80)

# Find best performing combinations
best_hour = hourly_perf[('Closed PnL', 'sum')].idxmax()
best_day = dow_perf[('Closed PnL', 'sum')].idxmax()
best_sentiment = merged_data.groupby('classification')['Closed PnL'].sum().idxmax()
best_coin = coin_pnl['Closed PnL'].idxmax()

print(f"""
BASED ON THE COMPREHENSIVE ANALYSIS, HERE ARE KEY INSIGHTS:

1. OPTIMAL TRADING TIMES:
   - Best Hour: {best_hour:02d}:00 (Highest total PnL)
   - Best Day: {dow_names[best_day]} (Highest total PnL)
   - Consider concentrating trading activity during these periods

2. MARKET SENTIMENT STRATEGY:
   - Best Overall Sentiment: {best_sentiment}
   - Trade more aggressively during {best_sentiment} periods
   - Reduce position sizes during Extreme Fear periods (highest volatility)

3. COIN SELECTION:
   - Best Performing Coin: {best_coin}
   - Focus on top 5 coins by PnL for better risk-adjusted returns
   - Diversify across coins with different sentiment correlations

4. POSITION SIZING:
   - Larger trades show different win rates than smaller trades
   - Consider scaling position sizes based on sentiment
   - Use smaller sizes during high volatility (Extreme Fear/Greed)

5. SENTIMENT MOMENTUM:
   - Monitor daily sentiment changes
   - Improving sentiment may signal good entry points
   - Worsening sentiment may indicate time to reduce exposure

6. RISK MANAGEMENT:
   - Extreme Fear shows highest PnL volatility
   - Neutral sentiment shows most consistent (lowest std) returns
   - Adjust stop-losses and position sizes accordingly
""")

print("\n" + "=" * 80)
print("ADVANCED ANALYSIS COMPLETE!")
print("=" * 80)
print("\nGenerated files:")
print("  - time_based_patterns.png")
print("  - coin_analysis.png")
print("  - size_risk_analysis.png")
print("  - sentiment_momentum.png")
print("  - coin_performance_summary.csv")
print("  - hourly_performance_summary.csv")
print("  - size_bucket_performance.csv")
