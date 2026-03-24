"""Download datasets from Google Drive"""
import gdown

# Historical Trader Data from Hyperliquid
historical_data_id = "1IAfLZwu6rJzyWKgBToqwSmmVYU6VbjVs"
historical_data_output = "historical_trader_data.csv"

# Fear Greed Index
fear_greed_id = "1PgQC0tO8XN-wqkNyghWc_-mnrYv_nhSf"
fear_greed_output = "fear_greed_index.csv"

print("Downloading Historical Trader Data...")
gdown.download(id=historical_data_id, output=historical_data_output, quiet=False)

print("\nDownloading Fear & Greed Index...")
gdown.download(id=fear_greed_id, output=fear_greed_output, quiet=False)

print("\nDownload complete!")
