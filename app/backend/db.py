import os
from typing import Any, Protocol

import psycopg
from psycopg.rows import dict_row


class DatabaseProtocol(Protocol):
    def initialize(self) -> None: ...

    def list_todos(self) -> list[dict[str, Any]]: ...

    def create_todo(self, text: str) -> dict[str, Any]: ...

    def delete_todo(self, todo_id: int) -> bool: ...

    def check_connection(self) -> bool: ...


class PostgresDatabase:
    def __init__(
        self,
        host: str,
        port: int,
        dbname: str,
        user: str,
        password: str,
    ) -> None:
        self._connection_kwargs = {
            "host": host,
            "port": port,
            "dbname": dbname,
            "user": user,
            "password": password,
        }

    @classmethod
    def from_env(cls) -> "PostgresDatabase":
        return cls(
            host=os.getenv("POSTGRES_HOST", "postgres"),
            port=int(os.getenv("POSTGRES_PORT", "5432")),
            dbname=os.getenv("POSTGRES_DB", "todok8s"),
            user=os.getenv("POSTGRES_USER", "todok8s"),
            password=os.getenv("POSTGRES_PASSWORD", "todok8s"),
        )

    def _connect(self) -> psycopg.Connection:
        return psycopg.connect(**self._connection_kwargs, autocommit=True)

    def initialize(self) -> None:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS todos (
                        id BIGSERIAL PRIMARY KEY,
                        text TEXT NOT NULL CHECK (char_length(trim(text)) > 0),
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    );
                    """
                )

    def list_todos(self) -> list[dict[str, Any]]:
        with self._connect() as connection:
            with connection.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    SELECT id, text, created_at
                    FROM todos
                    ORDER BY id;
                    """
                )
                return list(cursor.fetchall())

    def create_todo(self, text: str) -> dict[str, Any]:
        with self._connect() as connection:
            with connection.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    INSERT INTO todos (text)
                    VALUES (%s)
                    RETURNING id, text, created_at;
                    """,
                    (text,),
                )
                row = cursor.fetchone()
                if row is None:
                    raise RuntimeError("Failed to create todo")
                return dict(row)

    def delete_todo(self, todo_id: int) -> bool:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM todos WHERE id = %s;", (todo_id,))
                return cursor.rowcount > 0

    def check_connection(self) -> bool:
        try:
            with self._connect() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1;")
                    cursor.fetchone()
            return True
        except psycopg.Error:
            return False
