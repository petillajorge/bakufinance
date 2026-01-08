import asyncio
import websockets
import json

async def test_ws():
    uri = "ws://localhost:8000/ws/BTC/USDT"
    try:
        async with websockets.connect(uri) as websocket:
            print(f"Connected to {uri}")
            while True:
                message = await websocket.recv()
                print(f"Received: {message}")
                break # Just get one message to prove it works
    except Exception as e:
        print(f"Failed to connect: {e}")

if __name__ == "__main__":
    asyncio.run(test_ws())
