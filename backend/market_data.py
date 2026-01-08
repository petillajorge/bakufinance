import asyncio
import ccxt.async_support as ccxt
import yfinance as yf
import pandas as pd
import random
import datetime

class MarketDataService:
    def __init__(self):
        self.exchange = ccxt.binance()
        
    async def get_crypto_price(self, symbol):
        # symbol e.g., 'BTC/USDT'
        try:
            ticker = await self.exchange.fetch_ticker(symbol)
            return {
                "ticker": symbol,
                "price": ticker['last'],
                "change": ticker['percentage'],
                "volume": ticker['quoteVolume'],
                "timestamp": ticker['timestamp'],
                "type": "crypto"
            }
        except Exception as e:
            print(f"Error fetching crypto {symbol}: {e}")
            return None

    async def get_stock_price(self, symbol):
        # symbol e.g., 'AAPL'
        # yfinance is synchronous, run in executor if needed for high throughput, 
        # but for this demo standard call is okay-ish or better simulated for real-time appearance
        # Real-time stock data is hard to get for free. We will simulate "live" ticks 
        # based on the last close + random noise for the demo if market is closed,
        # or just fetch latest if open (delayed).
        try:
            ticker = yf.Ticker(symbol)
            # fast_info is faster access
            price = ticker.fast_info['last_price']
            prev_close = ticker.fast_info['previous_close']
            change = ((price - prev_close) / prev_close) * 100
            
            return {
                "ticker": symbol,
                "price": price,
                "change": change,
                "timestamp": int(datetime.datetime.now().timestamp() * 1000),
                "type": "stock"
            }
        except Exception as e:
            print(f"Error fetching stock {symbol}: {e}")
            return None

    async def stream_ticker(self, ticker):
        """
        Generator that yields real-time data.
        """
        # Determine if crypto or stock
        is_crypto = '/' in ticker or ticker.endswith('USDT') or ticker in ['BTC', 'ETH']
        
        # Normalize crypto ticker for CCXT
        if is_crypto and '/' not in ticker:
            if ticker in ['BTC', 'ETH', 'SOL', 'DOGE']:
                ticker = f"{ticker}/USDT"
        
        while True:
            if is_crypto:
                data = await self.get_crypto_price(ticker)
            else:
                data = await self.get_stock_price(ticker)
            
            if data:
                yield data
            
            # Update frequency: 1 second
            await asyncio.sleep(1)
            
    async def get_history(self, ticker, period="1d", interval="1m"):
        """
        Fetch historical data.
        period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
        interval: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
        """
        is_crypto = '/' in ticker or ticker.endswith('USDT') 
        
        # Normalize
        if is_crypto and '/' not in ticker:
             ticker = f"{ticker}/USDT"

        data_points = []
        
        try:
            if is_crypto:
                # CCXT mapping for periods roughly
                # period logic is complex for ccxt, usually specific candles count
                # simpler to use a default or map period to limit
                timeframe = interval if interval in self.exchange.timeframes else '1m'
                # fetch last 1000 candles
                ohlcv = await self.exchange.fetch_ohlcv(ticker, timeframe, limit=1000)
                # Format: [timestamp, open, high, low, close, volume]
                for x in ohlcv:
                     data_points.append({
                         "time": x[0] / 1000, # seconds
                         "value": x[4] # close price
                     })
            else:
                # Stocks (yfinance)
                # Map timeframe to yfinance arguments
                # yf period: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
                # yf interval: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
                
                # Handling '1W' etc from frontend if passed differently
                stock = yf.Ticker(ticker)
                hist = stock.history(period=period, interval=interval)
                
                # hist.index is Timestamp
                for index, row in hist.iterrows():
                    data_points.append({
                        "time": index.timestamp(),
                        "value": row['Close']
                    })
                    
            return data_points
        except Exception as e:
            print(f"Error fetching history for {ticker}: {e}")
            return []

    async def search_assets(self, query):
        """
        Simple autocomplete mock. In prod, use a real database or API.
        """
        query = query.upper()
        # Mix of popular stocks and crypto
        assets = [
            {"symbol": "BTC/USDT", "name": "Bitcoin", "type": "Crypto"},
            {"symbol": "ETH/USDT", "name": "Ethereum", "type": "Crypto"},
            {"symbol": "USDT/USDT", "name": "Tether", "type": "Crypto"},
            {"symbol": "XRP/USDT", "name": "XRP", "type": "Crypto"},
            {"symbol": "BNB/USDT", "name": "BNB", "type": "Crypto"},
            {"symbol": "SOL/USDT", "name": "Solana", "type": "Crypto"},
            {"symbol": "USDC/USDT", "name": "USDC", "type": "Crypto"},
            {"symbol": "STETH/USDT", "name": "Lido Staked Ether", "type": "Crypto"},
            {"symbol": "TRX/USDT", "name": "TRON", "type": "Crypto"},
            {"symbol": "DOGE/USDT", "name": "Dogecoin", "type": "Crypto"},
            {"symbol": "ADA/USDT", "name": "Cardano", "type": "Crypto"},
            {"symbol": "WSTETH/USDT", "name": "Wrapped stETH", "type": "Crypto"},
            {"symbol": "BCH/USDT", "name": "Bitcoin Cash", "type": "Crypto"},
            {"symbol": "WBETH/USDT", "name": "Wrapped Beacon ETH", "type": "Crypto"},
            {"symbol": "WBTC/USDT", "name": "Wrapped Bitcoin", "type": "Crypto"},
            {"symbol": "WEETH/USDT", "name": "Wrapped eETH", "type": "Crypto"},
            {"symbol": "USDS/USDT", "name": "USDS", "type": "Crypto"},
            {"symbol": "LINK/USDT", "name": "Chainlink", "type": "Crypto"},
            {"symbol": "BSC-USD/USDT", "name": "Binance Bridged USDT", "type": "Crypto"},
            {"symbol": "LEO/USDT", "name": "LEO Token", "type": "Crypto"},
            {"symbol": "WETH/USDT", "name": "WETH", "type": "Crypto"},
            {"symbol": "XMR/USDT", "name": "Monero", "type": "Crypto"},
            {"symbol": "ZEC/USDT", "name": "Zcash", "type": "Crypto"},
            {"symbol": "XLM/USDT", "name": "Stellar", "type": "Crypto"},
            {"symbol": "SUI/USDT", "name": "Sui", "type": "Crypto"},
            {"symbol": "CBBTC/USDT", "name": "Coinbase Wrapped BTC", "type": "Crypto"},
            {"symbol": "HYPE/USDT", "name": "Hyperliquid", "type": "Crypto"},
            {"symbol": "LTC/USDT", "name": "Litecoin", "type": "Crypto"},
            {"symbol": "USDE/USDT", "name": "Ethena USDe", "type": "Crypto"},
            {"symbol": "AVAX/USDT", "name": "Avalanche", "type": "Crypto"},
            {"symbol": "NVDA", "name": "Nvidia Corp", "type": "Stock"},
            {"symbol": "GOOGL", "name": "Alphabet Inc.", "type": "Stock"},
            {"symbol": "AAPL", "name": "Apple Inc.", "type": "Stock"},
            {"symbol": "MSFT", "name": "Microsoft Corp", "type": "Stock"},
            {"symbol": "AMZN", "name": "Amazon.com Inc", "type": "Stock"},
            {"symbol": "TSM", "name": "Taiwan Semiconductor", "type": "Stock"},
            {"symbol": "META", "name": "Meta Platforms Inc", "type": "Stock"},
            {"symbol": "AVGO", "name": "Broadcom Inc", "type": "Stock"},
            {"symbol": "2222.SR", "name": "Saudi Aramco", "type": "Stock"},
            {"symbol": "TSLA", "name": "Tesla Inc.", "type": "Stock"},
            {"symbol": "BRK.B", "name": "Berkshire Hathaway Inc", "type": "Stock"},
            {"symbol": "LLY", "name": "Eli Lilly and Co", "type": "Stock"},
            {"symbol": "JPM", "name": "JPMorgan Chase & Co", "type": "Stock"},
            {"symbol": "WMT", "name": "Walmart Inc", "type": "Stock"},
            {"symbol": "TCEHY", "name": "Tencent Holdings", "type": "Stock"},
            {"symbol": "V", "name": "Visa Inc", "type": "Stock"},
            {"symbol": "005930.KS", "name": "Samsung Electronics", "type": "Stock"},
            {"symbol": "ORCL", "name": "Oracle Corp", "type": "Stock"},
            {"symbol": "MA", "name": "Mastercard Inc", "type": "Stock"},
            {"symbol": "XOM", "name": "Exxon Mobil Corp", "type": "Stock"},
            {"symbol": "JNJ", "name": "Johnson & Johnson", "type": "Stock"},
            {"symbol": "ASML", "name": "ASML Holding NV", "type": "Stock"},
            {"symbol": "PLTR", "name": "Palantir Technologies", "type": "Stock"},
            {"symbol": "BAC", "name": "Bank of America Corp", "type": "Stock"},
            {"symbol": "ABBV", "name": "AbbVie Inc", "type": "Stock"},
            {"symbol": "COST", "name": "Costco Wholesale Corp", "type": "Stock"},
            {"symbol": "NFLX", "name": "Netflix Inc", "type": "Stock"},
            {"symbol": "MU", "name": "Micron Technology", "type": "Stock"},
            {"symbol": "601288.SS", "name": "Agri Bank of China", "type": "Stock"},
            {"symbol": "000660.KS", "name": "SK Hynix", "type": "Stock"},
            {"symbol": "MC.PA", "name": "LVMH", "type": "Stock"},
            {"symbol": "BABA", "name": "Alibaba Group", "type": "Stock"},
            {"symbol": "1398.HK", "name": "ICBC", "type": "Stock"},
            {"symbol": "HD", "name": "The Home Depot Inc", "type": "Stock"},
            {"symbol": "GE", "name": "GE Aerospace", "type": "Stock"},
            {"symbol": "AMD", "name": "Advanced Micro Devices", "type": "Stock"},
            {"symbol": "ROG.SW", "name": "Roche Holding AG", "type": "Stock"},
            {"symbol": "601939.SS", "name": "China Construction Bank", "type": "Stock"},
            {"symbol": "PG", "name": "Procter & Gamble Co", "type": "Stock"},
            {"symbol": "CVX", "name": "Chevron Corp", "type": "Stock"},
            {"symbol": "UNH", "name": "UnitedHealth Group", "type": "Stock"},
            {"symbol": "WFC", "name": "Wells Fargo & Co", "type": "Stock"},
            {"symbol": "CSCO", "name": "Cisco Systems Inc", "type": "Stock"},
            {"symbol": "AZN", "name": "AstraZeneca PLC", "type": "Stock"},
            {"symbol": "MS", "name": "Morgan Stanley", "type": "Stock"},
            {"symbol": "KO", "name": "The Coca-Cola Co", "type": "Stock"},
            {"symbol": "GS", "name": "Goldman Sachs Group", "type": "Stock"},
            {"symbol": "SAP", "name": "SAP SE", "type": "Stock"},
            {"symbol": "CAT", "name": "Caterpillar Inc", "type": "Stock"},
            {"symbol": "TM", "name": "Toyota Motor Corp", "type": "Stock"},
            {"symbol": "PRX.AS", "name": "Prosus NV", "type": "Stock"},
            {"symbol": "IBM", "name": "International Business Machines", "type": "Stock"},
            {"symbol": "HSBC", "name": "HSBC Holdings PLC", "type": "Stock"},
            {"symbol": "NVS", "name": "Novartis AG", "type": "Stock"},
            {"symbol": "MRK", "name": "Merck & Co Inc", "type": "Stock"},
            {"symbol": "AXP", "name": "American Express Co", "type": "Stock"},
            {"symbol": "RMS.PA", "name": "Hermès International", "type": "Stock"},
            {"symbol": "LRCX", "name": "Lam Research Corp", "type": "Stock"},
            {"symbol": "601988.SS", "name": "Bank of China", "type": "Stock"},
            {"symbol": "CRM", "name": "Salesforce Inc", "type": "Stock"},
            {"symbol": "TMO", "name": "Thermo Fisher Scientific", "type": "Stock"},
            {"symbol": "ABT", "name": "Abbott Laboratories", "type": "Stock"},
            {"symbol": "LIN", "name": "Linde PLC", "type": "Stock"},
            {"symbol": "PEP", "name": "PepsiCo Inc", "type": "Stock"},
            {"symbol": "DIS", "name": "The Walt Disney Co", "type": "Stock"},
            {"symbol": "QCOM", "name": "QUALCOMM Inc", "type": "Stock"},
            {"symbol": "PM", "name": "Philip Morris International", "type": "Stock"},
            {"symbol": "INTU", "name": "Intuit Inc", "type": "Stock"},
            {"symbol": "TXN", "name": "Texas Instruments", "type": "Stock"},
            {"symbol": "AMAT", "name": "Applied Materials Inc", "type": "Stock"},
            {"symbol": "INTC", "name": "Intel Corp", "type": "Stock"},
            {"symbol": "RTX", "name": "RTX Corp", "type": "Stock"},
            {"symbol": "PFE", "name": "Pfizer Inc", "type": "Stock"},
            {"symbol": "NEE", "name": "NextEra Energy", "type": "Stock"},
            {"symbol": "DHR", "name": "Danaher Corp", "type": "Stock"},
            {"symbol": "HON", "name": "Honeywell International", "type": "Stock"},
            {"symbol": "UNP", "name": "Union Pacific Corp", "type": "Stock"},
            {"symbol": "LOW", "name": "Lowe's Companies Inc", "type": "Stock"},
            {"symbol": "SPGI", "name": "S&P Global Inc", "type": "Stock"},
            {"symbol": "VRTX", "name": "Vertex Pharmaceuticals", "type": "Stock"},
            {"symbol": "EL", "name": "Estée Lauder Companies", "type": "Stock"},
            {"symbol": "CDNS", "name": "Cadence Design Systems", "type": "Stock"},
            {"symbol": "SNPS", "name": "Synopsys Inc", "type": "Stock"},
            {"symbol": "MDT", "name": "Medtronic PLC", "type": "Stock"},
            {"symbol": "BX", "name": "Blackstone Inc", "type": "Stock"},
            {"symbol": "DE", "name": "Deere & Co", "type": "Stock"},
            {"symbol": "SHOP", "name": "Shopify Inc", "type": "Stock"},
            {"symbol": "BKNG", "name": "Booking Holdings Inc", "type": "Stock"},
            {"symbol": "ADP", "name": "Automatic Data Processing", "type": "Stock"},
            {"symbol": "C", "name": "Citigroup Inc", "type": "Stock"},
            {"symbol": "TJX", "name": "TJX Companies Inc", "type": "Stock"},
            {"symbol": "MDLZ", "name": "Mondelez International", "type": "Stock"},
            {"symbol": "LMT", "name": "Lockheed Martin Corp", "type": "Stock"},
            {"symbol": "GILD", "name": "Gilead Sciences Inc", "type": "Stock"},
            {"symbol": "CB", "name": "Chubb Limited", "type": "Stock"},
            {"symbol": "PGR", "name": "Progressive Corp", "type": "Stock"},
            {"symbol": "SYK", "name": "Stryker Corp", "type": "Stock"},
            {"symbol": "ZTS", "name": "Zoetis Inc", "type": "Stock"},
            {"symbol": "REGN", "name": "Regeneron Pharmaceuticals", "type": "Stock"},
            {"symbol": "FI", "name": "Fiserv Inc", "type": "Stock"},
            {"symbol": "SCHW", "name": "Charles Schwab Corp", "type": "Stock"},
            {"symbol": "TMUS", "name": "T-Mobile US Inc", "type": "Stock"},
            {"symbol": "T", "name": "AT&T Inc", "type": "Stock"},
            {"symbol": "VZ", "name": "Verizon Communications", "type": "Stock"},
            {"symbol": "BSX", "name": "Boston Scientific Corp", "type": "Stock"},
            {"symbol": "CVS", "name": "CVS Health Corp", "type": "Stock"},
            {"symbol": "BMY", "name": "Bristol-Myers Squibb", "type": "Stock"},
            {"symbol": "AMGN", "name": "Amgen Inc", "type": "Stock"},
            {"symbol": "CI", "name": "The Cigna Group", "type": "Stock"},
            {"symbol": "UBER", "name": "Uber Technologies Inc", "type": "Stock"},
            {"symbol": "MU", "name": "Micron Technology Inc", "type": "Stock"},
            {"symbol": "PANW", "name": "Palo Alto Networks", "type": "Stock"},
            {"symbol": "LRCX", "name": "Lam Research Corp", "type": "Stock"},
            {"symbol": "ETN", "name": "Eaton Corp PLC", "type": "Stock"},
            {"symbol": "SNOW", "name": "Snowflake Inc", "type": "Stock"},
            {"symbol": "MCD", "name": "McDonald's Corp", "type": "Stock"},
            {"symbol": "SBUX", "name": "Starbucks Corp", "type": "Stock"},
            {"symbol": "ANET", "name": "Arista Networks Inc", "type": "Stock"},
            {"symbol": "KLAC", "name": "KLA Corp", "type": "Stock"},
            {"symbol": "ADBE", "name": "Adobe Inc", "type": "Stock"},
            {"symbol": "PYPL", "name": "PayPal Holdings Inc", "type": "Stock"},
            {"symbol": "SHW", "name": "Sherwin-Williams Co", "type": "Stock"},
            {"symbol": "NKE", "name": "NIKE Inc", "type": "Stock"},
            {"symbol": "ECL", "name": "Ecolab Inc", "type": "Stock"},
            {"symbol": "EQIX", "name": "Equinix Inc", "type": "Stock"},
            {"symbol": "PH", "name": "Parker-Hannifin Corp", "type": "Stock"},
            {"symbol": "WM", "name": "Waste Management Inc", "type": "Stock"},
            {"symbol": "ICE", "name": "Intercontinental Exchange", "type": "Stock"},
            {"symbol": "MMC", "name": "Marsh & McLennan", "type": "Stock"},
            {"symbol": "USB", "name": "U.S. Bancorp", "type": "Stock"},
            {"symbol": "TGT", "name": "Target Corp", "type": "Stock"},
            {"symbol": "ORLY", "name": "O'Reilly Automotive", "type": "Stock"},
            {"symbol": "CMG", "name": "Chipotle Mexican Grill", "type": "Stock"},
            {"symbol": "MCK", "name": "McKesson Corp", "type": "Stock"},
            {"symbol": "MO", "name": "Altria Group Inc", "type": "Stock"},
            {"symbol": "PNC", "name": "PNC Financial Services", "type": "Stock"},
            {"symbol": "MPC", "name": "Marathon Petroleum", "type": "Stock"},
            {"symbol": "EMR", "name": "Emerson Electric Co", "type": "Stock"},
            {"symbol": "HCA", "name": "HCA Healthcare Inc", "type": "Stock"},
            {"symbol": "COF", "name": "Capital One Financial", "type": "Stock"},
            {"symbol": "NSC", "name": "Norfolk Southern Corp", "type": "Stock"},
            {"symbol": "ROP", "name": "Roper Technologies", "type": "Stock"},
            {"symbol": "AIG", "name": "American International Group", "type": "Stock"},
            {"symbol": "EOG", "name": "EOG Resources Inc", "type": "Stock"},
            {"symbol": "SLB", "name": "Schlumberger Limited", "type": "Stock"},
            {"symbol": "ABNB", "name": "Airbnb Inc", "type": "Stock"},
            {"symbol": "MAR", "name": "Marriott International", "type": "Stock"},
            {"symbol": "PSX", "name": "Phillips 66", "type": "Stock"},
            {"symbol": "KMB", "name": "Kimberly-Clark Corp", "type": "Stock"},
            {"symbol": "MET", "name": "MetLife Inc", "type": "Stock"},
            {"symbol": "AJG", "name": "Arthur J. Gallagher & Co", "type": "Stock"},
            {"symbol": "FDX", "name": "FedEx Corp", "type": "Stock"},
            {"symbol": "STZ", "name": "Constellation Brands", "type": "Stock"},
            {"symbol": "MCO", "name": "Moody's Corp", "type": "Stock"},
            {"symbol": "CME", "name": "CME Group Inc", "type": "Stock"},
            {"symbol": "GD", "name": "General Dynamics Corp", "type": "Stock"},
            {"symbol": "ITW", "name": "Illinois Tool Works", "type": "Stock"},
            {"symbol": "TRV", "name": "The Travelers Companies", "type": "Stock"},
            {"symbol": "EIX", "name": "Edison International", "type": "Stock"},
            {"symbol": "DUK", "name": "Duke Energy Corp", "type": "Stock"},
            {"symbol": "AEP", "name": "American Electric Power", "type": "Stock"},
            {"symbol": "SO", "name": "Southern Co", "type": "Stock"},
            {"symbol": "APD", "name": "Air Products & Chemicals", "type": "Stock"},
            {"symbol": "BKR", "name": "Baker Hughes Co", "type": "Stock"},
            {"symbol": "VLO", "name": "Valero Energy Corp", "type": "Stock"},
            {"symbol": "WELL", "name": "Welltower Inc", "type": "Stock"},
            {"symbol": "PSA", "name": "Public Storage", "type": "Stock"},
            {"symbol": "O", "name": "Realty Income Corp", "type": "Stock"},
            {"symbol": "NOC", "name": "Northrop Grumman Corp", "type": "Stock"},
            {"symbol": "OXY", "name": "Occidental Petroleum", "type": "Stock"},
            {"symbol": "ADM", "name": "Archer-Daniels-Midland", "type": "Stock"},
            {"symbol": "KR", "name": "The Kroger Co", "type": "Stock"},
            {"symbol": "D", "name": "Dominion Energy Inc", "type": "Stock"},
            {"symbol": "PCG", "name": "PG&E Corp", "type": "Stock"},
            {"symbol": "CNP", "name": "CenterPoint Energy", "type": "Stock"},
            {"symbol": "EXC", "name": "Exelon Corp", "type": "Stock"},
            {"symbol": "XEL", "name": "Xcel Energy Inc", "type": "Stock"},
            {"symbol": "F", "name": "Ford Motor Co", "type": "Stock"},
            {"symbol": "GM", "name": "General Motors Co", "type": "Stock"},
            {"symbol": "MCHP", "name": "Microchip Technology", "type": "Stock"},
            {"symbol": "TEL", "name": "TE Connectivity Ltd", "type": "Stock"},
            {"symbol": "APH", "name": "Amphenol Corp", "type": "Stock"},
            {"symbol": "KEYS", "name": "Keysight Technologies", "type": "Stock"},
            {"symbol": "FTNT", "name": "Fortinet Inc", "type": "Stock"},
            {"symbol": "WDAY", "name": "Workday Inc", "type": "Stock"},
            {"symbol": "LULU", "name": "Lululemon Athletica", "type": "Stock"},
            {"symbol": "MNST", "name": "Monster Beverage Corp", "type": "Stock"},
            {"symbol": "KDP", "name": "Keurig Dr Pepper Inc", "type": "Stock"},
            {"symbol": "K", "name": "Kellogg Co", "type": "Stock"},
            {"symbol": "GIS", "name": "General Mills Inc", "type": "Stock"},
            {"symbol": "CL", "name": "Colgate-Palmolive Co", "type": "Stock"},
            {"symbol": "HSY", "name": "The Hershey Co", "type": "Stock"},
            {"symbol": "DASH", "name": "DoorDash Inc", "type": "Stock"},
            {"symbol": "MKTX", "name": "MarketAxess Holdings", "type": "Stock"},
            {"symbol": "URBN", "name": "Urban Outfitters", "type": "Stock"}
                    ]
        
        results = [a for a in assets if query in a['symbol'] or query in a['name'].upper()]
        return results[:10]

    async def close(self):
        await self.exchange.close()
