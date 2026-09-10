import os
import asyncio
import json
from fastapi import FastAPI, WebSocket
import websockets
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv

# Load the hidden API key from the .env file
load_dotenv()

# Look for the label "ASSEMBLYAI_API_KEY" inside the .env file
API_KEY = os.getenv("ASSEMBLYAI_API_KEY")

app = FastAPI()

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
                    "type": "function", # <--- ADD THIS EXACT LINE
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
                if event.get("type") == "tool_calls":
                    for tool in event["tool_calls"]:
                        if tool["name"] == "resolve_conflict":
                            print(f"\n⚙️ SAM'S BACKEND TRIGGERED: {tool['arguments']}")
                            
                            # --- 1. SAM'S DICE LOGIC HAPPENS HERE ---
                            # (Read gameState.json, roll the d6s, update candle count)
                            
                            # Let's pretend the roll was a success for this example
                            roll_outcome = "The player rolled a 6. They succeed in their action."
                            
                            # --- 2. SEND THE RESULT BACK TO ASSEMBLYAI ---
                            response_payload = {
                                "type": "tool_response",
                                "tool_calls": [
                                    {
                                        "id": tool["id"], # You MUST pass back the exact ID the AI sent you
                                        "result": roll_outcome
                                    }
                                ]
                            }
                            await aai_ws.send(json.dumps(response_payload))
                
                # Forward everything else (like AI audio) to the browser
                await client_ws.send_text(message)

        # Run both the browser listener and the AI listener at the same time
        await asyncio.gather(receive_from_browser(), receive_from_aai())