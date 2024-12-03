from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import yfinance as yf

app = FastAPI()

class StockQuery(BaseModel):
    query: str

@app.post("/find-stocks")
async def find_stocks(query: StockQuery):
    # Mock NLP Processing
    nlp_keywords = query.query.lower()
    
    # Define sectors or conditions based on user query
    target_sector = "technology" if "technology" in nlp_keywords else None
    min_market_cap = 1_000  # Example threshold in billions, adjust as needed
    
    # Fetch stock data dynamically
    tickers = ["AAPL", "GOOGL", "AMZN", "MSFT", "TSLA", "NVDA"]  # Add NYSE tickers as needed
    stocks_data = []
    
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Append stock data
            stocks_data.append({
                "ticker": ticker,
                "name": info.get("longName", "N/A"),
                "sector": info.get("sector", "Unknown"),
                "market_cap": info.get("marketCap", 0) / 1e9,  # Convert to billions
                "volume": info.get("volume", 0)
            })
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
    
    # Filter stocks based on sector and market cap
    filtered_stocks = [
        stock for stock in stocks_data
        if (not target_sector or stock["sector"].lower() == target_sector)
        and stock["market_cap"] >= min_market_cap
    ]
    
    # Sort by market cap in descending order
    filtered_stocks = sorted(filtered_stocks, key=lambda x: x["market_cap"], reverse=True)
    
    # Limit to top 5 results
    top_stocks = filtered_stocks[:5]
    
    # Handle case where no results match
    if not top_stocks:
        raise HTTPException(status_code=404, detail="No stocks match the criteria.")
    
    return {"top_companies": top_stocks}
