# Setup — get PromptPi running in 5 minutes

You talk → the browser transcribes → a **local LLM** rewrites it into a clean,
structured prompt. Everything runs on your own machine. No API key, no cloud.

Follow these steps in order.

## 1. Install Python (if you don't have it)

Check: open a terminal and run `python --version`.
If it's missing, get it from https://www.python.org/downloads/ (tick **"Add
Python to PATH"** during install), then reopen the terminal.

## 2. Install Ollama (the local LLM runner)

Download and run the installer from **https://ollama.com/download**
(Windows users can instead run `winget install Ollama.Ollama`).

After installing, Ollama runs in the background automatically.

## 3. Download the model

In a terminal:

```bash
ollama pull qwen2.5:1.5b
```

(~1 GB, one-time. Want faster/lighter? `ollama pull qwen2.5:0.5b` and set
`LLM_MODEL=qwen2.5:0.5b` before step 5.)

## 4. Get the code and its one dependency

```bash
git clone https://github.com/jacklachan/prompi.git
cd prompi
pip install -r requirements.txt
```

## 5. Run it

```bash
python app.py
```

Then open **http://localhost:5000** in **Chrome or Edge**
(the 🎙 microphone only works in those browsers).

## Use it

1. Press **TALK**, say your idea, press **STOP**.
2. Press **SEND** — the local LLM structures it.
3. **Copy for Claude** or **Download .md**.

You can also just type into the box instead of talking.

## If something's off

| Problem | Fix |
|---|---|
| Output says "mock mode … not reachable" | Ollama isn't running. Open the Ollama app, or run `ollama serve`. |
| "model not found" | You skipped step 3. Run `ollama pull qwen2.5:1.5b`. |
| Mic button does nothing | Use Chrome or Edge, and allow microphone access when asked. |
| Port 5000 already in use | Close the other app, or change the port at the bottom of `app.py`. |

That's it. See [README.md](README.md) for how this maps to the ESP32 device.
