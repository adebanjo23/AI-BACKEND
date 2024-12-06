from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
from twilio.twiml.voice_response import VoiceResponse, Connect

def register_routes(app: FastAPI):
    @app.websocket("/media-stream")
    async def handle_media_stream(websocket: WebSocket):
        await app.state.pipeline.process(websocket)

    @app.api_route("/incoming-call", methods=["GET", "POST"])
    async def handle_incoming_call(request: Request):
        response = VoiceResponse()
        host = request.url.hostname
        connect = Connect()
        connect.stream(url=f'wss://{host}/media-stream')
        response.append(connect)
        return HTMLResponse(content=str(response), media_type="application/xml")