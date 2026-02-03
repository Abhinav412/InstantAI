from backend.main import start_chat, chat_reply
from backend.main import StartRequest, ReplyRequest
import json

if __name__ == '__main__':
    # Start chat
    req = StartRequest(message='Top 10 incubators in India')
    out = start_chat(req)
    print('START_OUT:', json.dumps(out, indent=2, ensure_ascii=False))
    if out.get('ok'):
        chat_id = out['chat_id']
        # Now reply, ask bot to pick metrics
        r = ReplyRequest(message='Pick metrics')
        out2 = chat_reply(chat_id, r)
        print('\nREPLY_OUT:', json.dumps(out2, indent=2, ensure_ascii=False))
    else:
        print('start failed')
