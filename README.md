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

## Facebook Page Watcher

A script that watches a public Facebook page (no login required, since the
content is public) and emails you when a new post appears. Standard library
only, no external dependencies.

Facebook has no official no-login API for arbitrary public pages, so this
works by periodically fetching the mobile page and diffing posts against a
local state file. It clearly reports when Facebook blocks the request with a
login wall rather than failing silently. You may need to tweak the parsing
regex in `extract_posts()` if Facebook changes its page markup.

### Setup

1. Enable 2-Step Verification on the Gmail account you want to send from,
   then create an App Password: https://myaccount.google.com/apppasswords
2. Export credentials:
   ```bash
   export GMAIL_USER="you@gmail.com"
   export GMAIL_APP_PASSWORD="xxxx xxxx xxxx xxxx"
   ```

### Usage

```bash
# First run just records the current posts (no email sent yet)
python3 facebook_page_watcher.py --to you@example.com

# Preview what would be emailed without actually sending
python3 facebook_page_watcher.py --to you@example.com --dry-run

# Watch a different page
python3 facebook_page_watcher.py --page-url "https://m.facebook.com/SomePage/" --to you@example.com
```

### Scheduling

Run it on a recurring basis with cron (every 30 minutes, for example):

```cron
*/30 * * * * cd /path/to/hello-world && /usr/bin/python3 facebook_page_watcher.py --to you@example.com >> watcher.log 2>&1
```

Note: this script must run somewhere with real network access to Facebook
and persistent storage for `facebook_watcher_state.json` (e.g. your own
computer or a small server) — it doesn't run on its own.

## Learning Coach — Azure (Claude Code skill)

A Claude Code skill at `.claude/skills/learning-coach-azure/SKILL.md` that
turns Claude into a personal Azure tutor: it grounds explanations in official
Microsoft Learn docs, teaches one concept at a time with quizzes and hands-on
checks, and keeps a running progress log in `azure-learning-progress.md` so
sessions pick up where you left off.

Just ask Claude to help you learn Azure (or study for an Azure certification
like AZ-900) and the skill activates automatically.
