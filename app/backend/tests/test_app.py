from datetime import datetime, timezone

from fastapi.testclient import TestClient

from main import create_app


class FakeDatabase:
    def __init__(self) -> None:
        self.todos: list[dict] = []
        self.next_id = 1
        self.is_healthy = True
        self.initialized = False

    def initialize(self) -> None:
        self.initialized = True

    def list_todos(self) -> list[dict]:
        return list(self.todos)

    def create_todo(self, text: str) -> dict:
        todo = {
            "id": self.next_id,
            "text": text,
            "created_at": datetime.now(timezone.utc),
        }
        self.next_id += 1
        self.todos.append(todo)
        return todo

    def delete_todo(self, todo_id: int) -> bool:
        for index, todo in enumerate(self.todos):
            if todo["id"] == todo_id:
                del self.todos[index]
                return True
        return False

    def check_connection(self) -> bool:
        return self.is_healthy


def create_test_client(database: FakeDatabase) -> TestClient:
    app = create_app(database)
    return TestClient(app)


def test_health_returns_ok_for_healthy_backend() -> None:
    database = FakeDatabase()
    with create_test_client(database) as client:
        response = client.get("/health")

    assert database.initialized is True
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_returns_503_when_database_is_unavailable() -> None:
    database = FakeDatabase()
    database.is_healthy = False

    with create_test_client(database) as client:
        response = client.get("/health")

    assert response.status_code == 503
    assert response.json()["detail"] == "Database connection is unavailable."


def test_create_and_list_todos() -> None:
    database = FakeDatabase()

    with create_test_client(database) as client:
        create_response = client.post("/todos", json={"text": "Learn Docker"})
        list_response = client.get("/todos")

    assert create_response.status_code == 201
    assert create_response.json()["text"] == "Learn Docker"
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
    assert list_response.json()[0]["id"] == 1


def test_delete_todo() -> None:
    database = FakeDatabase()

    with create_test_client(database) as client:
        create_response = client.post("/todos", json={"text": "Delete me"})
        todo_id = create_response.json()["id"]

        delete_response = client.delete(f"/todos/{todo_id}")
        list_response = client.get("/todos")

    assert delete_response.status_code == 204
    assert list_response.json() == []


def test_rejects_blank_todo_text() -> None:
    database = FakeDatabase()

    with create_test_client(database) as client:
        response = client.post("/todos", json={"text": "   "})

    assert response.status_code == 400
    assert response.json()["detail"] == "Todo text must not be empty."
