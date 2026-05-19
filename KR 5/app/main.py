from fastapi import FastAPI, Request, status, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from .routers import tasks, users, admin
from .schemas import ErrorResponse
from .config import APP_ENV
from .websocket_manager import room_manager

app = FastAPI(title="Task Manager API", version="1.0.0")

app.include_router(tasks.router)
app.include_router(users.router)
app.include_router(admin.router)

@app.get("/health", tags=["system"])
async def health_check():
    return {"status": "ok"}

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            detail="Validation error",
            status_code=422,
            error_type="ValidationError"
        ).model_dump()
    )

@app.websocket("/ws/rooms/{room_id}")
async def websocket_room(
    websocket: WebSocket,
    room_id: str,
    username: str = Query(..., min_length=1, description="Имя пользователя")
):
    if not username or not username.strip():
        await websocket.close(code=1008, reason="Username is required")
        return

    username = username.strip()
    await room_manager.connect(room_id, username, websocket)

    try:
        while True:
            data = await websocket.receive_json()
            message_text = data.get("text", "")

            if len(message_text) > 300:
                await room_manager.send_error(websocket, "Message is too long")
                continue

            await room_manager.broadcast(
                room_id,
                {
                    "type": "message",
                    "room_id": room_id,
                    "username": username,
                    "text": message_text,
                },
            )
    except WebSocketDisconnect:
        room_manager.disconnect(room_id, username, websocket)
        await room_manager.broadcast(
            room_id,
            {
                "type": "system",
                "event": "user_left",
                "room_id": room_id,
                "username": username,
                "users": await room_manager.get_users(room_id),
            },
        )


@app.get("/rooms/{room_id}/users")
async def get_room_users(room_id: str):
    users = await room_manager.get_users(room_id)
    return {"room_id": room_id, "users": users}