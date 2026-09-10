import asyncio
import json
import base64
from fastapi import FastAPI, WebSocket
import websockets
from fastapi.responses import HTMLResponse

app = FastAPI()
API_KEY = "YOUR_API_KEY" # Paste your key here

# This serves the HTML interface to your browser
@app.get("/")
def get_home():
    with open("index.html", "r") as f:
        return HTMLResponse(f.read())

# This relays audio between the HTML page and AssemblyAI
@app.websocket("/ws")
async def websocket_proxy(client_ws: WebSocket):
    await client_ws.accept()
    
    url = "wss://agents.assemblyai.com/v1/ws"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    async with websockets.connect(url, additional_headers=headers) as aai_ws:
        print("✅ Backend connected to AssemblyAI!")
        
        # 1. Initialize the Ten Candles Session
        await aai_ws.send(json.dumps({
            "type": "session.update",
            "session": {
                "system_prompt": "You are the Game Master for a tragic horror game called Ten Candles. Speak slowly, with a somber, grim tone. Keep replies to two sentences max.",
                "greeting": "These things are true. The world is dark. And we are alive. What do you do?",
                "output": {"voice": "ivy"},
                "tools": [{
                    "name": "resolve_conflict",
                    "description": "Resolves a dangerous or risky action using the Ten Candles d6 dice pool mechanic.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "character_id": { "type": "string" },
                            "action_description": { "type": "string" }
                        },
                        "required": ["character_id", "action_description"]
                    }
                }]
            }
        }))

        # 2. Forward Browser Audio -> AssemblyAI
        async def receive_from_browser():
            try:
                while True:
                    data = await client_ws.receive_text()
                    await aai_ws.send(data)
            except:
                pass

        # 3. Forward AssemblyAI Responses -> Browser (and catch tools!)
        async def receive_from_aai():
            async for message in aai_ws:
                event = json.loads(message)
                
                # Catch the GM rolling dice on the backend!
                if event["type"] == "tool_calls":
                    for tool in event["tool_calls"]:
                        if tool["name"] == "resolve_conflict":
                            print(f"\n⚙️ SAM'S BACKEND TRIGGERED: {tool['arguments']}")
                
                # Forward everything else (like AI audio) to the browser
                await client_ws.send_text(message)

        await asyncio.gather(receive_from_browser(), receive_from_aai())