import os
import subprocess
import textwrap
import json
from dotenv import load_dotenv
import requests

# ===============================================================
# Load API key from .env
# ===============================================================
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# ===============================================================
# Model + endpoint
#   Use one of the models from list_models.py, e.g.:
#   models/gemini-3-pro-preview
#   models/gemini-2.5-pro
#   models/gemini-2.0-flash
# ===============================================================
MODEL_NAME = "models/gemini-3-pro-preview"

API_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/{MODEL_NAME}:generateContent"
HEADERS = {
    "Content-Type": "application/json",
    "X-goog-api-key": API_KEY,
}

# ===============================================================
# System prompt: JSON-only protocol
# ===============================================================
SYSTEM_PROMPT = """
You are an AI developer assistant directly controlling a macOS terminal via this bridge.

You must follow this STRICT MACHINE-READABLE PROTOCOL:

1. Your ENTIRE reply must be a SINGLE JSON object.
   - No backticks.
   - No markdown.
   - No prose outside JSON.
   - No additional keys beyond the three below.

2. The JSON must have EXACTLY these keys:

   {
     "commands": [<list of shell command strings>],
     "summary": "<human-readable explanation>",
     "finished": <true or false>
   }

   - "commands": an array (possibly empty) of shell commands to run in the user's terminal.
   - "summary": a short human-readable explanation of what you did or want to do.
   - "finished": a boolean.
        * false = you want another round after seeing the command transcript.
        * true  = you're done and do not need any more rounds.

3. Examples of VALID replies:

   {
     "commands": ["ls -F", "python3 main.py"],
     "summary": "Listed files and ran the main script.",
     "finished": false
   }

   {
     "commands": [],
     "summary": "No commands needed; I'm done.",
     "finished": true
   }

4. NEVER include explanations or comments outside the JSON.
   NEVER prefix commands with CMD: or DONE:.
   ONLY use the JSON structure above.

5. All commands run in the user's current project directory.
   Avoid destructive commands (rm -rf, sudo) unless explicitly requested.

You will be given:
- The user's request.
- A transcript of previously executed commands and their outputs.

Use that context to decide which commands to run next, and whether you are finished.
Repeat: Your entire reply must be ONE JSON object matching the schema above.
"""

# ===============================================================
# Low-level Gemini call (HTTP, curl-style)
# ===============================================================
def call_gemini(prompt_text: str) -> str:
    """
    Call the Gemini API using the same structure as the curl quickstart.
    Returns the first text part of the first candidate.
    """
    if not API_KEY:
         raise RuntimeError("Missing GEMINI_API_KEY. Please set it in .env or via the GUI.")

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt_text
                    }
                ]
            }
        ]
    }

    try:
        resp = requests.post(API_ENDPOINT, headers=HEADERS, data=json.dumps(payload))
    except Exception as e:
        raise RuntimeError(f"Request to Gemini failed: {e}")

    if resp.status_code != 200:
        raise RuntimeError(f"Gemini API error {resp.status_code}: {resp.text}")

    data = resp.json()

    try:
        candidates = data["candidates"]
        first = candidates[0]
        parts = first["content"]["parts"]
        text = parts[0]["text"]
        return text
    except Exception as e:
        raise RuntimeError(
            f"Unexpected Gemini response format: {e}\nFull response: {json.dumps(data, indent=2)}"
        )

# ===============================================================
# Shell command helpers
# ===============================================================
def run_shell_command(cmd: str) -> dict:
    shell = os.environ.get("SHELL", "/bin/bash")
    result = subprocess.run(
        cmd,
        shell=True,
        executable=shell,
        capture_output=True,
        text=True
    )
    return {
        "cmd": cmd,
        "exit_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr
    }

def format_execution_result(res: dict) -> str:
    return textwrap.dedent(f"""
    Command: {res["cmd"]}
    Exit code: {res["exit_code"]}

    STDOUT:
    {res["stdout"] if res["stdout"] else "(no stdout)"}

    STDERR:
    {res["stderr"] if res["stderr"] else "(no stderr)"}
    """).strip()

def coerce_finished_flag(raw_finished):
    """
    Robustly interpret the 'finished' field from the model's JSON.
    Accepts:
      - boolean true/false
      - string "true"/"false" (case-insensitive)
      - numbers (0 = False, non-zero = True)
    Anything else → False by default.
    """
    if isinstance(raw_finished, bool):
        return raw_finished
    if isinstance(raw_finished, str):
        val = raw_finished.strip().lower()
        if val in ("true", "yes", "y", "done", "finished"):
            return True
        if val in ("false", "no", "n"):
            return False
        # default for unknown strings
        return False
    if isinstance(raw_finished, (int, float)):
        return raw_finished != 0
    return False

def summary_indicates_done(summary: str) -> bool:
    """
    Heuristic: if the summary clearly says it's done, stop
    even if 'finished' is wrong.
    """
    s = summary.lower()
    keywords = [
        "i am done",
        "i'm done",
        "i am finished",
        "i'm finished",
        "no further steps",
        "nothing else to do",
        "task is complete",
        "all done",
        "everything is complete",
        "work is complete",
        "that completes",
        "that should complete",
    ]
    return any(k in s for k in keywords)

# ===============================================================
# Chat Session with Persistence
# ===============================================================
class GeminiBridgeSession:
    def __init__(self):
        self.conversation_history = [] # For future use if we want to send full chat history
        self.command_transcript = []   # Persistent transcript of commands run in this session

    def chat(self, user_request: str, max_rounds: int = 10):
        """
        Run a multi-turn loop to satisfy a SINGLE user request,
        but keeping the context of previous commands (self.command_transcript).
        """
        no_command_rounds = 0

        # We append the new request to our conceptual history
        # (For this simple implementation, we just pass the cumulative transcript
        # plus the current request to the model. A more advanced version might
        # send the entire conversation string.)
        
        # New interaction starts
        print(f"--- processing request: {user_request} ---")

        for round_num in range(max_rounds):
            # The context includes ALL previous commands from this session
            transcript_text = "\n\n".join(self.command_transcript) if self.command_transcript else "(no previous commands in this session)"

            prompt = f"""
{SYSTEM_PROMPT.strip()}

USER REQUEST:
{user_request}

TERMINAL TRANSCRIPT (Cumulative):
{transcript_text}

Remember: reply ONLY with a single JSON object:
{{
  "commands": [...],
  "summary": "...",
  "finished": true/false
}}
""".strip()

            # Call Gemini via HTTP
            raw_reply = call_gemini(prompt).strip()

            print(f"\n=== GEMINI RAW REPLY (ROUND {round_num + 1}) ===")
            print(raw_reply)
            print("===============================================\n")

            # Parse JSON
            try:
                obj = json.loads(raw_reply)
            except json.JSONDecodeError as e:
                print(f"[ERROR] Could not parse JSON from model reply: {e}")
                print("[ERROR] Raw reply was:")
                print(raw_reply)
                break

            commands = obj.get("commands", [])
            summary = obj.get("summary", "")
            raw_finished = obj.get("finished", False)

            if not isinstance(commands, list):
                print("[ERROR] 'commands' is not a list in model reply.")
                break

            # Robust finished flag + heuristic
            finished = coerce_finished_flag(raw_finished)

            if summary_indicates_done(summary):
                print("[Bridge] Summary indicates completion; treating as finished.")
                finished = True

            # Execute commands
            round_results = []
            if commands:
                no_command_rounds = 0
                for cmd in commands:
                    if not isinstance(cmd, str):
                        print(f"[WARN] Skipping non-string command: {cmd}")
                        continue

                    print(f"→ Running: {cmd}")
                    res = run_shell_command(cmd)
                    round_results.append(res)
                    print(format_execution_result(res))
                    print("-" * 45)
            else:
                no_command_rounds += 1
                print("[Bridge] No commands in this round.")

            # Update persistent transcript
            for res in round_results:
                self.command_transcript.append(format_execution_result(res))

            # Print summary for the user
            if summary:
                print("\n=== SUMMARY FROM GEMINI ===")
                print(summary)
                print("=================================\n")

            # Stop on finished flag
            if finished:
                print("[Bridge] Model indicated it is finished.")
                break

            # Stop if no commands for 2 consecutive rounds
            if no_command_rounds >= 2:
                print("[Bridge] No commands for 2 consecutive rounds; stopping to avoid infinite loop.")
                break
        else:
            print("[Bridge] Reached max_rounds without finished == true. Ending.")


# ===============================================================
# API key setter for GUI / dynamic updates
# ===============================================================
def set_api_key(new_key: str):
    """
    Update the Gemini API key at runtime.
    """
    global API_KEY, HEADERS
    new_key = (new_key or "").strip()
    if not new_key:
        raise ValueError("API key cannot be empty.")

    API_KEY = new_key
    os.environ["GEMINI_API_KEY"] = new_key

    # Update headers
    if "X-goog-api-key" in HEADERS:
        HEADERS["X-goog-api-key"] = new_key
    else:
        HEADERS["X-goog-api-key"] = new_key

# ===============================================================
# CLI entrypoint
# ===============================================================
if __name__ == "__main__":
    print(f"Gemini ↔ macOS Terminal Bridge ({MODEL_NAME})")
    print("Type a request (or 'exit' to quit).")
    
    session = GeminiBridgeSession()

    while True:
        try:
            req = input("\nYour request> ").strip()
        except EOFError:
            break

        if req.lower() in {"exit", "quit"}:
            break
        
        if not req:
            continue

        try:
            session.chat(req)
        except Exception as e:
            print(f"[ERROR] {e}")

