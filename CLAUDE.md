# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Visionexa is a single-user Flask profile website with a REST API and server-rendered HTML views. It stores one profile (singleton pattern) with associated skills and projects in a SQLite database. There is no authentication layer.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server (default: http://localhost:5000)
python run.py

# Run with a specific config
FLASK_ENV=production python run.py

# Open a Flask shell with db and models pre-loaded
flask shell
```

There is no test suite or linter configured.

## Architecture

The app uses the Flask application factory pattern. `app/__init__.py` creates the app and calls `db.create_all()` on every startup — there are no migration files.

Two blueprints are registered:
- `main_bp` — renders `index.html` and `about.html` using the first `Profile` row
- `profile_bp` (prefix `/profile`) — JSON API for reading and writing profile, skills, and projects

**Singleton profile:** All write routes do `Profile.query.first()` and either create or update that single row. Skills and projects are always attached to this first profile. Adding multi-user support would require reworking every route.

`config.py` defines `DevelopmentConfig`, `TestingConfig` (in-memory SQLite), and `ProductionConfig`. The active config is selected by the `FLASK_ENV` env var in `run.py`.

## Working Notes

- `SQLALCHEMY_DATABASE_URI` in the base `Config` uses a path relative to the project root (`sqlite:///instance/visionexa.db`), not the Flask instance folder — the `instance/` directory must exist.
- `profile_image_url` and `image_url` on `Project` are stored as plain URL strings; there is no file upload handling.
- `Skill.level` is a free-text field; the convention in the model comment is `Beginner / Intermediate / Advanced / Expert`, but it is not enforced.
- `FLASK_DEBUG` in `run.py` defaults to the string `"True"` (truthy), not a boolean — passing `FLASK_DEBUG=False` via env will still evaluate as truthy.
