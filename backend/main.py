from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
from market_data import MarketDataService

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev, allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

market_service = MarketDataService()

@app.get("/")
async def root():
    return {"status": "ok", "service": "Finance API"}

@app.get("/history/{ticker:path}")
async def get_history(ticker: str, period: str = "1d", interval: str = "1m"):
    ticker = ticker.upper()
    data = await market_service.get_history(ticker, period, interval)
    return data

@app.get("/search")
async def search_assets(q: str):
    return await market_service.search_assets(q)

@app.websocket("/ws/{ticker:path}")
async def websocket_endpoint(websocket: WebSocket, ticker: str):
    await websocket.accept()
    try:
        # Subscribe logic would go here. 
        # For this demo, we'll stream data for the requested ticker.
        # Ensure ticker is upper case
        ticker = ticker.upper()
        
        async for data in market_service.stream_ticker(ticker):
            await websocket.send_json(data)
            
    except WebSocketDisconnect:
        print(f"Client disconnected from {ticker}")
    except Exception as e:
        print(f"Error in websocket: {e}")
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
