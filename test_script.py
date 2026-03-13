import asyncio
import websockets
import json

async def test_ws():
    uri = "ws://localhost:8000/ws/call/"
    print(f"Connecting to {uri}...")
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected!")
            
            # Send test message
            msg = {
                "type": "call_message",
                "message": {"status": "ringing", "call_id": "123"},
                "sender": "test_script"
            }
            print(f"Sending: {msg}")
            await websocket.send(json.dumps(msg))
            
            # Receive response
            response = await websocket.recv()
            print(f"Received: {response}")
            print("WebSocket test successful!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_ws())
