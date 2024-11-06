import asyncio
import logging
import fastapi
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class WebSocketManager(fastapi.APIRouter):
    def __init__(self):
        super().__init__()
        self.clients: set[WebSocket] = set()
        self.lock = asyncio.Lock()
        self.add_websocket_route("/", self.endpoint)
    
    
    async def endpoint(self, websocket: WebSocket):
        await websocket.accept()
        async with self.lock:
            self.clients.add(websocket)
        try:
            while True:
                # Keeps the connection open for incoming messages
                await websocket.receive_text()
                await asyncio.sleep(1)
        except WebSocketDisconnect:
            async with self.lock:
                self.clients.remove(websocket)
            logger.info("Client disconnected")
        except Exception as e:
            logger.error(f"Unexpected error in WebSocket connection: {e}")
    
    
    async def broadcast(self, message: dict):
        async with self.lock:
            to_disconnect = []
            for client in list(self.clients):
                try:
                    await client.send_json(message)
                except WebSocketDisconnect:
                    to_disconnect.append(client)
                except Exception as e:
                    logger.error(f"Failed to send message to client: {e}")
                    
            # Remove all clients that disconnected during the broadcast attempt
            for client in to_disconnect:
                self.clients.remove(client)
