# PromptPi — dry run (no hardware)

Software stand-in for the ESP32 paper. You talk, the browser transcribes, and a
**local LLM** rewrites your rough speech into a **structured prompt** you paste
into Claude — and can download as a `.md` file. Same server the ESP32 will later
POST to.

## Run

```bash
pip install -r requirements.txt
python app.py
```

Open http://localhost:5000 in **Chrome or Edge** (Web Speech API needs them).
Press **TALK**, speak, **STOP**, **SEND**, then **Copy for Claude** or **Download .md**.

## The local LLM

`/structure` calls any server that speaks the **OpenAI chat API**. Default points
at Ollama. If nothing is running, it returns a labelled mock so the UI still works.

**Ollama (easiest):**
```bash
# install from ollama.com, then:
ollama pull llama3.2     # or a smaller/faster model
ollama serve             # runs on :11434 — the default LLM_URL
python app.py
```
Pick a model with `set LLM_MODEL=qwen2.5` (Windows `set`, or `$env:LLM_MODEL=...`).

**LM Studio / llama.cpp / LEAP:** start its local server and point at it:
```bash
set LLM_URL=http://localhost:1234/v1/chat/completions
set LLM_MODEL=your-model
```

**LiquidAI LFM2** (the model you linked) fits here — it's a small on-device LLM.
Run it through Ollama (GGUF), LM Studio, or Liquid's LEAP SDK, then set `LLM_URL`
/ `LLM_MODEL` to it. Note: LFM2 runs on a laptop or a Raspberry Pi — **not** on
the ESP32, which has no room for any LLM.

Self-check (offline, forces the mock path): `python app.py --selftest`

## Mapping to the paper's hardware

| Paper (ESP32) | Dry run |
|---|---|
| INMP441 I2S mic + cloud STT | browser mic + Web Speech API |
| ESP32 TALK/SEND/REDO buttons | the on-screen buttons |
| cloud server + AI prompt gen | `app.py` `/structure` → local LLM (unchanged later) |
| TFT display + web dashboard | `index.html` |
| Firebase history | in-memory `/history` list |

When the ESP32 arrives it records audio and POSTs to the **same** server; add a
server-side STT step there, and `/structure` is reused as-is.
