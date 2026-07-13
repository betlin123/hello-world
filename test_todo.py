import json
from pathlib import Path

import pytest

import todo


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    return tmp_path / "tasks.json"


def test_list_empty(db_path: Path, capsys):
    todo.list_tasks(db_path)
    assert "No tasks yet." in capsys.readouterr().out


def test_add_task(db_path: Path):
    todo.add_task(db_path, "Buy milk")
    tasks = json.loads(db_path.read_text())
    assert tasks == [{"id": 1, "text": "Buy milk", "done": False}]


def test_add_multiple_tasks_increments_id(db_path: Path):
    todo.add_task(db_path, "Buy milk")
    todo.add_task(db_path, "Walk dog")
    tasks = json.loads(db_path.read_text())
    assert [t["id"] for t in tasks] == [1, 2]


def test_complete_task(db_path: Path):
    todo.add_task(db_path, "Buy milk")
    todo.complete_task(db_path, 1)
    tasks = json.loads(db_path.read_text())
    assert tasks[0]["done"] is True


def test_complete_missing_task_exits(db_path: Path):
    with pytest.raises(SystemExit):
        todo.complete_task(db_path, 99)


def test_delete_task(db_path: Path):
    todo.add_task(db_path, "Buy milk")
    todo.delete_task(db_path, 1)
    tasks = json.loads(db_path.read_text())
    assert tasks == []


def test_delete_missing_task_exits(db_path: Path):
    with pytest.raises(SystemExit):
        todo.delete_task(db_path, 99)


def test_list_shows_tasks(db_path: Path, capsys):
    todo.add_task(db_path, "Buy milk")
    capsys.readouterr()
    todo.list_tasks(db_path)
    out = capsys.readouterr().out
    assert "Buy milk" in out
    assert "[ ]" in out
