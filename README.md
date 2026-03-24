# Trader Performance vs Market Sentiment Analysis

A comprehensive analysis exploring the relationship between trader performance on Hyperliquid and Bitcoin market sentiment (Fear & Greed Index).

## 📊 Dataset Overview

| Dataset | Records | Description |
|---------|---------|-------------|
| Historical Trader Data | 211,224 trades | Hyperliquid trading data with PnL, position size, direction |
| Fear & Greed Index | 2,644 records | Daily Bitcoin market sentiment readings |

## 🎯 Key Findings

| Metric | Value |
|--------|-------|
| **Total PnL** | $10,296,958.94 |
| **Overall Win Rate** | 83.20% |
| **Best Sentiment (PnL)** | Fear ($2,675,413.42) |
| **Best Sentiment (Win Rate)** | Extreme Greed (45.87%) |
| **Best Trading Hour** | 12:00 ($911,657.26) |
| **Best Trading Day** | Tuesday ($1,959,180.83) |
| **Top Performing Coin** | @107 ($2,783,912.92) |

## 🚀 Key Insights

1. **Contrarian Strategy Works**
   - Short during Fear periods: $1,978,361 PnL
   - Long during Greed periods: $939,176 PnL

2. **Sentiment Momentum Matters**
   - Improving sentiment: $64.54 avg PnL
   - Worsening sentiment: $32.60 avg PnL

3. **Position Sizing Impact**
   - Very Large trades generate 80% of total PnL ($8.2M)

4. **Optimal Timing**
   - Best hours: 12:00, 07:00, 19:00
   - Best days: Tuesday, Thursday, Friday
   - Best month: December ($2.9M)

## 📁 Project Structure

```
├── TRADING_STRATEGY_REPORT.md    # Detailed analysis report
├── analysis.py                    # Main analysis script
├── advanced_analysis.py           # Advanced pattern analysis
├── download_data.py               # Data download script
├── explore_data.py                # Data exploration script
├── sentiment_analysis_overview.png
├── sentiment_direction_heatmap.png
├── top_traders_analysis.png
├── time_based_patterns.png
├── coin_analysis.png
├── size_risk_analysis.png
└── sentiment_momentum.png
```

## 🛠️ Installation

```bash
pip install pandas numpy matplotlib seaborn scikit-learn gdown
```

## 📈 Usage

1. **Download Data**
   ```bash
   python download_data.py
   ```

2. **Run Analysis**
   ```bash
   python analysis.py
   python advanced_analysis.py
   ```

3. **View Report**
   - Open `TRADING_STRATEGY_REPORT.md` for detailed insights

## 📋 Analysis Scripts

| Script | Purpose |
|--------|---------|
| `download_data.py` | Downloads datasets from Google Drive |
| `explore_data.py` | Initial data exploration and structure analysis |
| `analysis.py` | Core sentiment-performance correlation analysis |
| `advanced_analysis.py` | Time patterns, coin analysis, statistical tests |

## 🎯 Trading Strategies

The report includes 7 actionable strategies:

1. **Sentiment-Based Position Sizing** - Adjust sizes based on Fear/Greed level
2. **Contrarian Directional Trading** - Short in Fear, Long in Greed
3. **Optimal Timing** - Trade during high-performance windows
4. **Sentiment Momentum Trading** - Follow improving sentiment trends
5. **Coin Selection Framework** - Tier-based coin allocation
6. **Risk Management Rules** - Sentiment-adjusted stop losses
7. **Scaling Protocol** - Position scaling based on trade performance

## 📊 Generated Visualizations

- **sentiment_analysis_overview.png** - Main dashboard with key metrics
- **sentiment_direction_heatmap.png** - PnL heatmap by sentiment and direction
- **top_traders_analysis.png** - Top trader performance breakdown
- **time_based_patterns.png** - Hourly, daily, monthly patterns
- **coin_analysis.png** - Coin performance comparison
- **size_risk_analysis.png** - Position size impact analysis
- **sentiment_momentum.png** - Sentiment momentum effect

## ⚠️ Limitations

- Historical data analysis; future results may differ
- ~20% of trades couldn't be matched with sentiment data
- Correlation does not imply causation
- Market conditions evolve; strategies need periodic review

## 📄 License

This analysis is for educational and informational purposes only. Not financial advice.

---

*Analysis period: January 2023 - December 2025*  
*Report generated: March 24, 2026*
