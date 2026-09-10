# The Cadence Engine (Ten Candles AI Game Master)

Welcome to **FahItWeBall**'s voice-native TTRPG engine! This project turns a mobile browser into a Push-to-Talk terminal where players can speak their actions naturally. 

Under the hood, it uses AssemblyAI's Voice Agent API, which handles speech-to-text, LLM reasoning, and text-to-speech over a single WebSocket connection. We use this because it costs a flat $4.50/hour and its speech-to-text accuracy (based on their Universal-3.5 Pro Realtime model released in June 2026) is critical for catching exact dice roll intents and alphanumeric identifiers.

The audio streaming defaults to 24 kHz, 16-bit, mono audio. The backend catches JSON-based tool calls (like `resolve_conflict`) so we can trigger real game mechanics (like d6 dice pools) based on spoken intent.

## 🛠️ Prerequisites

Before you run this, you need a few things installed:
* **Python 3.x**
* **An AssemblyAI API Key**: Create a free account at AssemblyAI. The Voice Agent API requires the `Bearer` prefix in the authorization header, but the server code already handles this for you. 

## 🚀 Local Setup

1. **Clone the repository**:
   ```bash
   git clone [https://github.com/YOUR_GITHUB_NAME/cadence-engine.git](https://github.com/YOUR_GITHUB_NAME/cadence-engine.git)
   cd cadence-engine

   Install the dependencies:
    Bash

    pip install fastapi uvicorn websockets python-dotenv

    Add the API Key:
    Create a new file in the main folder called .env and add your key like this:
    ASSEMBLYAI_API_KEY=your_actual_key_here
    (This keeps the key safe and out of the public GitHub code!)

🎲 Running the Game

    Start the backend server:
    Run the following command in your terminal:
    Bash

    uvicorn server:app --host 0.0.0.0 --port 8000

    Open the interface:

        On your PC: Open your web browser and go to http://localhost:8000.

        On your phone: Connect your phone to the same Wi-Fi network as your PC. Find your PC's local IPv4 address (e.g., 192.168.1.15) and navigate to http://YOUR_IP_ADDRESS:8000 in your mobile browser.

    Play:
    The initial connection starts with a session.update message to set the system prompt and tools. Wait for the Game Master's opening line. Tap and hold the giant red button to speak your action, then release it to listen. Check the Python terminal to see when the AI triggers the backend game mechanics!


### 2. Pushing from VS Code to GitHub
Since you already have VS Code open, you don't even need to type the Git commands manually in PowerShell. VS Code has a built-in visual Git interface.

**Step 1: Hide Your API Key (Crucial!)**
Before you push anything, you must hide your API key so someone doesn't steal it from GitHub and use up your hackathon credits. 
1. Create a file named `.env` and put your key inside it: `ASSEMBLYAI_API_KEY=YOUR_KEY`
2. Create another file named `.gitignore` and type `.env` inside it. This tells Git to completely ignore the key file.
3. Update your `server.py` to read the key from the `.env` file instead of hardcoding it:
```python
import os
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("ASSEMBLYAI_API_KEY")