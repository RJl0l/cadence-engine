import asyncio
import json
import base64
import websockets
import sounddevice as sd

# 1. Paste your exact API key here
API_KEY = "e9d86a5fb9f34359b9d8fa2a15fb9feb"

async def run_agent():
    url = "wss://agents.assemblyai.com/v1/ws"
    headers = {"Authorization": f"Bearer {API_KEY}"}

    print("Connecting to the Shadows...")
    
    # THE FIX: additional_headers instead of extra_headers
    async with websockets.connect(url, additional_headers=headers) as ws:
        print("✅ Connection Established! The Game Master is listening...\n")
        
        # 2. Initialize the Ten Candles Session
        await ws.send(json.dumps({
            "type": "session.update",
            "session": {
                "system_prompt": "You are the Game Master for a tragic horror game called Ten Candles. Speak slowly, with a somber, grim tone. Keep replies to two sentences max.",
                "greeting": "These things are true. The world is dark. And we are alive. What do you do?",
                "output": {"voice": "ivy"}
            }
        }))

        # 3. Stream Microphone Audio UP to the AI
        async def send_audio():
            loop = asyncio.get_event_loop()
            queue = asyncio.Queue()

            def callback(indata, frames, time, status):
                loop.call_soon_threadsafe(queue.put_nowait, bytes(indata))

            stream = sd.RawInputStream(samplerate=24000, channels=1, dtype='int16', blocksize=1200, callback=callback)
            with stream:
                while True:
                    data = await queue.get()
                    payload = base64.b64encode(data).decode("ascii")
                    await ws.send(json.dumps({"type": "input.audio", "audio": payload}))

        # 4. Stream AI Voice Audio DOWN to your Speakers
        async def receive_events():
            stream = sd.RawOutputStream(samplerate=24000, channels=1, dtype='int16')
            with stream:
                async for message in ws:
                    event = json.loads(message)
                    if event["type"] == "reply.audio":
                        audio_bytes = base64.b64decode(event["data"])
                        stream.write(audio_bytes)
                    elif event["type"] == "reply.done":
                        print("--> Agent finished speaking, your turn.")
                    elif event["type"] == "error":
                        print("❌ Error:", event)

        # Run both streams simultaneously
        await asyncio.gather(send_audio(), receive_events())

# Start the engine
asyncio.run(run_agent())