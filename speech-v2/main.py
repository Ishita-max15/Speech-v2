from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import os
import random
import json

app = FastAPI(title="Ishita's Conversation Bot")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create templates directory if it doesn't exist
os.makedirs("templates", exist_ok=True)
templates = Jinja2Templates(directory="templates")


class ConversationBot:
    def __init__(self):
        self.responses = {
            "hello": ["Hi there!", "Hello!", "Hey! How can I help?"],
            "hi": ["Hi there!", "Hello!", "Hey! How can I help?"],
            "how are you": ["I'm great, thanks!", "Doing well!", "All systems operational!"],
            "what's your name": ["I'm Ishita's conversation bot!", "I'm your friendly chat bot!"],
            "default": ["That's interesting!", "Tell me more!", "I see.", "Cool!"]
        }

    def get_response(self, user_input):
        user_input = user_input.lower()
        for key in self.responses:
            if key in user_input:
                return random.choice(self.responses[key])
        return random.choice(self.responses["default"])


bot = ConversationBot()


@app.get("/")
async def get_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "host": "Ishita"})


@app.post("/get_response")
async def get_bot_response(request: Request):
    data = await request.json()
    user_input = data.get("user_input", "")
    response = bot.get_response(user_input)
    return JSONResponse({"response": response})


class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)


manager = ConnectionManager()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)

            if message_data.get('type') == 'text_to_speech':
                text = message_data.get('text', '')
                if text:
                    # For now, just echo back a response
                    response_text = f"I received your message: {text}"
                    await manager.send_personal_message({
                        "type": "message",
                        "text": response_text
                    }, websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        ssl_keyfile="./key.pem",  # Optional: for HTTPS
        ssl_certfile="./cert.pem"