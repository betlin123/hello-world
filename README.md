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

## Car Counter App

A simple command-line app to count cars per location, stored in a JSON file (`~/.car_counter.json` by default; override with `--db`).

### Usage

```bash
# Add 1 car at a location
python3 car_counter.py add "Main Street"

# Add multiple cars at once
python3 car_counter.py add "Highway 1" 5

# List all counts
python3 car_counter.py list

# Reset count for a specific location
python3 car_counter.py reset "Main Street"

# Reset all counts
python3 car_counter.py reset

# Use a custom database file
python3 car_counter.py --db my_counts.json add "Parking Lot A" 3
```

---

### Running Tests

```bash
pip install pytest
python3 -m pytest test_todo.py
```
