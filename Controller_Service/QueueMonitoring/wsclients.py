from websocket import WebSocket
import json

workspace = 'Workspace-01'
ws = WebSocket()
notificaton_url = f'ws://localhost:8000/ws/chat/{workspace}/'
ws.connect(url=notificaton_url)
msg_dict = {
    "owner": workspace,
    "finished": "True"
}
ws.send(json.dumps({"message": msg_dict}))