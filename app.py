import streamlit as st
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
import sqlite3


class TaskState(str, Enum):
    planned = "planned"
    in_progress = "in-progress"
    done = "done"


class Task(BaseModel):
    name: str
    description: str
    notes: str
    state: TaskState = Field(default=TaskState.planned)
    created_at: datetime = Field(default_factory=datetime.now)
    category: str


def init_db():
    with sqlite3.connect('tasks.db') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                notes TEXT NOT NULL,
                state TEXT NOT NULL,
                created_at TEXT NOT NULL,
                category TEXT NOT NULL
            )
        ''')
        conn.commit()


def add_task_to_db(task: Task):
    with sqlite3.connect('tasks.db') as conn:
        conn.execute('''
            INSERT INTO tasks (name, description, notes, state, created_at, category)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (task.name, task.description, task.notes, task.state.value, task.created_at.isoformat(), task.category))
        conn.commit()


def get_tasks_from_db():
    with sqlite3.connect('tasks.db') as conn:
        tasks = conn.execute('''
            SELECT id, name, description, notes, state, created_at, category FROM tasks
        ''').fetchall()
        return tasks


def update_task_state_in_db(id: int, new_state: TaskState):
    with sqlite3.connect('tasks.db') as conn:
        conn.execute('''
            UPDATE tasks SET state = ? WHERE id = ?
        ''', (new_state.value, id))
        conn.commit()


def delete_task_from_db(id: int):
    with sqlite3.connect('tasks.db') as conn:
        conn.execute('''
            DELETE FROM tasks WHERE id = ?
        ''', (id,))
        conn.commit()

init_db()

st.title('Todo List App')


with st.form("add_task"):
    st.write("## Add a new task")
    name = st.text_input("Task Name", max_chars=50)
    description = st.text_area("Task Description")
    notes = st.text_area("Notes")
    category = st.selectbox("Category", ["Personal", "Work", "School"])
    submitted = st.form_submit_button("Submit")

    if submitted and name and description and notes and category:
        add_task_to_db(Task(name=name, description=description, notes=notes, category=category))
        st.success("Task added successfully!")


st.write("## Tasks")
tasks = get_tasks_from_db()

for task in tasks:
    st.write(f"ID: {task[0]}, Name: {task[1]}, Description: {task[2]}, Notes: {task[3]}, State: {task[4]}, Created At: {task[5]}, Category: {task[6]}")
    
   
    if st.button("Mark as Done", key=f"done-{task[0]}"):
        update_task_state_in_db(task[0], TaskState.done)
        st.experimental_rerun()
    
  
    if st.button("Delete", key=f"delete-{task[0]}"):
        delete_task_from_db(task[0])
        st.experimental_rerun()
