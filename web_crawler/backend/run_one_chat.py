import json
import sys
from pathlib import Path

# Ensure repo root is on sys.path so `backend` package can be imported
repo_root = str(Path(__file__).resolve().parents[1])
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from backend.main import chat, ChatRequest

if __name__ == '__main__':
    req = ChatRequest(message='Top 10 netflix shows in India')
    out = chat(req)
    print(json.dumps(out, indent=2, ensure_ascii=False))
