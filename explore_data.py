"""Explore the structure of both datasets"""
import pandas as pd

# Load datasets
print("=" * 60)
print("LOADING DATASETS")
print("=" * 60)

historical_data = pd.read_csv("historical_trader_data.csv")
fear_greed = pd.read_csv("fear_greed_index.csv")

print("\n" + "=" * 60)
print("HISTORICAL TRADER DATA")
print("=" * 60)
print(f"\nShape: {historical_data.shape}")
print(f"\nColumns: {historical_data.columns.tolist()}")
print(f"\nData Types:\n{historical_data.dtypes}")
print(f"\nFirst 5 rows:\n{historical_data.head()}")
print(f"\nBasic Statistics:\n{historical_data.describe()}")
print(f"\nMissing Values:\n{historical_data.isnull().sum()}")

print("\n" + "=" * 60)
print("FEAR & GREED INDEX")
print("=" * 60)
print(f"\nShape: {fear_greed.shape}")
print(f"\nColumns: {fear_greed.columns.tolist()}")
print(f"\nData Types:\n{fear_greed.dtypes}")
print(f"\nFirst 5 rows:\n{fear_greed.head()}")
print(f"\nBasic Statistics:\n{fear_greed.describe()}")
print(f"\nMissing Values:\n{fear_greed.isnull().sum()}")

# Check unique values in key columns
print("\n" + "=" * 60)
print("UNIQUE VALUES ANALYSIS")
print("=" * 60)

print(f"\nHistorical Data - Unique Coins: {historical_data['Coin'].nunique()}")
print(f"Coins (first 20): {historical_data['Coin'].unique()[:20]}")

print(f"\nHistorical Data - Unique Accounts: {historical_data['Account'].nunique()}")

print(f"\nHistorical Data - Unique Sides: {historical_data['Side'].unique()}")

print(f"\nHistorical Data - Unique Directions: {historical_data['Direction'].unique()}")

print(f"\nFear & Greed - Classification values: {fear_greed['classification'].unique()}")

# Check date ranges
print("\n" + "=" * 60)
print("DATE RANGE ANALYSIS")
print("=" * 60)

# Convert time columns to datetime with mixed format
historical_data['Timestamp IST'] = pd.to_datetime(historical_data['Timestamp IST'], format='mixed')
historical_data['Timestamp'] = pd.to_datetime(historical_data['Timestamp'], unit='ms')
fear_greed['date'] = pd.to_datetime(fear_greed['date'])

print(f"\nHistorical Data Time Range (IST): {historical_data['Timestamp IST'].min()} to {historical_data['Timestamp IST'].max()}")
print(f"Historical Data Time Range (UTC): {historical_data['Timestamp'].min()} to {historical_data['Timestamp'].max()}")
print(f"Fear & Greed Date Range: {fear_greed['date'].min()} to {fear_greed['date'].max()}")

# Check PnL distribution
print("\n" + "=" * 60)
print("PnL ANALYSIS")
print("=" * 60)
print(f"\nClosed PnL Statistics:\n{historical_data['Closed PnL'].describe()}")
print(f"\nTotal PnL: {historical_data['Closed PnL'].sum():,.2f}")
print(f"Profitable Trades: {(historical_data['Closed PnL'] > 0).sum()} ({(historical_data['Closed PnL'] > 0).mean()*100:.2f}%)")
print(f"Loss-Making Trades: {(historical_data['Closed PnL'] < 0).sum()} ({(historical_data['Closed PnL'] < 0).mean()*100:.2f}%)")
print(f"Break-even Trades: {(historical_data['Closed PnL'] == 0).sum()}")

# Save cleaned column names for reference
print("\n" + "=" * 60)
print("COLUMN MAPPING FOR ANALYSIS")
print("=" * 60)
print("""
Historical Trader Data Columns (cleaned):
- Account -> Trader account address
- Coin -> Trading pair symbol
- Execution Price -> Trade execution price
- Size Tokens -> Trade size in tokens
- Size USD -> Trade size in USD
- Side -> Buy/Sell side
- Timestamp IST -> Trade timestamp (IST timezone)
- Start Position -> Position size at trade start
- Direction -> Long/Short direction
- Closed PnL -> Realized PnL from trade
- Transaction Hash -> Blockchain transaction hash
- Order ID -> Order identifier
- Crossed -> Whether order was crossed
- Fee -> Trading fee
- Trade ID -> Unique trade identifier
- Timestamp -> Unix timestamp (ms)

Fear & Greed Index Columns:
- timestamp -> Unix timestamp
- value -> Fear/Greed score (0-100)
- classification -> Fear/Neutral/Greed category
- date -> Calendar date
""")
