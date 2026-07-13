# hello-world
just testing

Hi, this is Bettina and this is my first version and I would like to learn to code. 

## To-Do App

A simple command-line to-do list manager written in Python (no external dependencies).

Tasks are stored in a JSON file (`~/.todo.json` by default; override with `--db`).

### Usage

```bash
# Add a task
python3 todo.py add "Buy milk"

# List all tasks
python3 todo.py list

# Mark a task as done
python3 todo.py complete 1

# Delete a task
python3 todo.py delete 1

# Use a custom database file
python3 todo.py --db my_tasks.json add "Custom list task"
```

### Running Tests

```bash
pip install pytest
python3 -m pytest test_todo.py
```
