"""PromptPi dry run — the cloud server from the paper, minus the hardware.

Flow: browser mic (stands in for the ESP32's I2S mic) -> transcript -> this
server asks a LOCAL LLM to turn the raw spoken brain-dump into a structured
prompt -> dashboard shows it and offers a .md download. When the ESP32 arrives
it just POSTs to /structure too.

The local LLM is any server that speaks the OpenAI chat API (Ollama, LM Studio,
llama.cpp --server, LEAP/LFM2). Point LLM_URL/LLM_MODEL at it:

  Ollama:    ollama serve ; ollama pull llama3.2     (default below)
  LM Studio: start its local server, set LLM_URL=http://localhost:1234/v1/chat/completions

Run:  python app.py   then open http://localhost:5000
If the local LLM is unreachable, /structure falls back to a labelled mock so the
UI flow still works offline.
"""
import os
import json
import urllib.request
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder=".")

# Any OpenAI-compatible /v1/chat/completions endpoint. Ollama's is the default.
LLM_URL = os.environ.get("LLM_URL", "http://localhost:11434/v1/chat/completions")
LLM_MODEL = os.environ.get("LLM_MODEL", "qwen2.5:1.5b")  # installed; bigger = better

SYSTEM = (
    "You are a prompt engineer. The user speaks a rough, unstructured idea out "
    "loud; you receive the raw speech-to-text transcript. Rewrite it as one "
    "clear, well-structured prompt that the user can paste straight into Claude "
    "to get the result they want.\n\n"
    "Always include ALL of these sections, each on its own line:\n"
    "**Task** — one sentence saying what you want Claude to do.\n"
    "**Context** — background Claude needs (infer sensible context from the idea).\n"
    "**Requirements** — at least 3 specific bullets the output must satisfy.\n"
    "**Output format** — how the answer should be shaped.\n\n"
    "If the transcript is vague or missing key details, do NOT invent specifics. "
    "Instead add an **Assumptions & open questions** section that names what is "
    "unclear, and end the prompt with an instruction telling Claude to make "
    "reasonable assumptions (and state them), filling the gaps itself and asking "
    "only for details it genuinely cannot proceed without.\n\n"
    "Fix filler and speech-to-text noise. Do not answer the request or add "
    "commentary — output only the finished prompt."
)

history = []  # in-memory, newest last; replaces Firebase for the dry run

# The LLM is always local — bypass any system HTTP proxy, or localhost calls fail.
_opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def call_llm(transcript):
    """POST to the local OpenAI-compatible chat endpoint; return the prompt text."""
    # Small local models follow the directive better in the user turn than as a
    # bare system prompt, so we repeat it around the transcript.
    user = (
        "Here is a raw speech-to-text transcript of someone thinking out loud:\n\n"
        f'"""{transcript}"""\n\n'
        "Rewrite it as the structured prompt described, filling in ALL four "
        "sections (Task, Context, Requirements, Output format). Output ONLY the "
        "finished prompt, starting immediately with the line `**Task**`."
    )
    body = json.dumps({
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user},
        ],
        "temperature": 0.2,
        "stream": False,
    }).encode()
    req = urllib.request.Request(LLM_URL, body, {"Content-Type": "application/json"})
    with _opener.open(req, timeout=120) as r:
        data = json.load(r)
    return data["choices"][0]["message"]["content"].strip()


def mock(transcript, reason):
    return (
        "**Task**\n" + (transcript or "(say something first)") + "\n\n"
        "**Requirements**\n- Be specific and complete.\n\n"
        "**Assumptions & open questions**\n- Local LLM was unreachable, so this "
        "is a passthrough. Claude: make reasonable assumptions and ask for "
        "anything essential that's missing.\n\n"
        f"_[mock mode — local LLM at {LLM_URL} not reachable: {reason}]_"
    )


def structure(transcript):
    transcript = transcript.strip()
    try:
        return call_llm(transcript)
    except Exception as e:  # not running / model missing / timeout
        return mock(transcript, type(e).__name__)


@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/structure", methods=["POST"])
def structure_endpoint():
    transcript = (request.get_json(force=True) or {}).get("transcript", "")
    if not transcript.strip():
        return jsonify(error="empty transcript"), 400
    prompt = structure(transcript)
    history.append({"transcript": transcript, "prompt": prompt})
    return jsonify(prompt=prompt)


@app.route("/history")
def history_endpoint():
    return jsonify(history[-20:])


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        os.environ["no_proxy"] = "*"
        globals()["LLM_URL"] = "http://127.0.0.1:1/x"  # force unreachable -> mock
        out = structure("um so i want a python script that renames photos by date")
        assert "**Task**" in out and "rename" in out and "mock mode" in out, out
        print("selftest OK (mock path):\n" + out)
    else:
        app.run(host="127.0.0.1", port=5000, debug=True)
