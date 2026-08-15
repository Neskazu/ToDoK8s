const apiBaseUrl = (window.APP_CONFIG?.API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");

const form = document.querySelector("#todo-form");
const input = document.querySelector("#todo-input");
const statusElement = document.querySelector("#status");
const todoList = document.querySelector("#todo-list");

function setStatus(message, isError = false) {
  statusElement.textContent = message;
  statusElement.classList.toggle("error", isError);
}

async function request(path, options = {}) {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    let errorMessage = `Request failed with status ${response.status}`;

    try {
      const errorBody = await response.json();
      if (errorBody.detail) {
        errorMessage = errorBody.detail;
      }
    } catch (error) {
      void error;
    }

    throw new Error(errorMessage);
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

function createTodoItem(todo) {
  const listItem = document.createElement("li");
  listItem.className = "todo-item";

  const text = document.createElement("span");
  text.className = "todo-text";
  text.textContent = todo.text;

  const button = document.createElement("button");
  button.type = "button";
  button.className = "delete-button";
  button.textContent = "Удалить";
  button.addEventListener("click", async () => {
    try {
      setStatus("Удаление...");
      await request(`/todos/${todo.id}`, { method: "DELETE" });
      await loadTodos("Задача удалена.");
    } catch (error) {
      setStatus(error.message, true);
    }
  });

  listItem.append(text, button);
  return listItem;
}

async function loadTodos(successMessage = "") {
  try {
    const todos = await request("/todos");
    todoList.replaceChildren();

    if (todos.length === 0) {
      const emptyState = document.createElement("li");
      emptyState.className = "todo-item";
      emptyState.textContent = "Список пуст.";
      todoList.append(emptyState);
    } else {
      todos.forEach((todo) => {
        todoList.append(createTodoItem(todo));
      });
    }

    setStatus(successMessage || "Готово.");
  } catch (error) {
    todoList.replaceChildren();
    setStatus(error.message, true);
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const text = input.value.trim();
  if (!text) {
    setStatus("Введите текст задачи.", true);
    return;
  }

  try {
    setStatus("Добавление...");
    await request("/todos", {
      method: "POST",
      body: JSON.stringify({ text }),
    });
    input.value = "";
    await loadTodos("Задача добавлена.");
  } catch (error) {
    setStatus(error.message, true);
  }
});

loadTodos();
