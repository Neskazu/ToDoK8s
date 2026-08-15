from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, HTTPException, Path, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from db import DatabaseProtocol, PostgresDatabase


class TodoCreate(BaseModel):
    text: str = Field(min_length=1)


class TodoResponse(BaseModel):
    id: int
    text: str
    created_at: str


class HealthResponse(BaseModel):
    status: str


def create_app(database: DatabaseProtocol | None = None) -> FastAPI:
    database_instance = database or PostgresDatabase.from_env()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.database = database_instance
        app.state.database.initialize()
        yield

    app = FastAPI(title="ToDoK8s Backend", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    def get_database(request: Request) -> DatabaseProtocol:
        return request.app.state.database

    @app.get("/todos", response_model=list[TodoResponse])
    def get_todos(request: Request) -> list[dict]:
        database = get_database(request)
        todos = database.list_todos()
        return [
            {
                "id": todo["id"],
                "text": todo["text"],
                "created_at": todo["created_at"].isoformat(),
            }
            for todo in todos
        ]

    @app.post(
        "/todos",
        response_model=TodoResponse,
        status_code=status.HTTP_201_CREATED,
    )
    def create_todo(payload: TodoCreate, request: Request) -> dict:
        text = payload.text.strip()
        if not text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Todo text must not be empty.",
            )

        database = get_database(request)
        todo = database.create_todo(text)
        return {
            "id": todo["id"],
            "text": todo["text"],
            "created_at": todo["created_at"].isoformat(),
        }

    @app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_todo(
        todo_id: Annotated[int, Path(gt=0)],
        request: Request,
    ) -> Response:
        database = get_database(request)
        deleted = database.delete_todo(todo_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Todo not found.",
            )
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    @app.get("/health", response_model=HealthResponse)
    def get_health(request: Request) -> dict[str, str]:
        database = get_database(request)
        if not database.check_connection():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database connection is unavailable.",
            )
        return {"status": "ok"}

    return app


app = create_app()
