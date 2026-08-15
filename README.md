# what-to-do

A deliberately simple personal task and planning application.

## Idea

* Project groups contain projects.
* Projects contain task cards.
* Tasks contain the actual work/item to be done.
* Tasks can be scheduled for one or more time slots.
* A calendar/week planner is a second view of the same tasks.
* Eventually support drag-and-drop between projects/groups.

The goal is simple, not Jira.

## Architecture
```ascii
CLI/TUI ──┐
          ├── Service ── Domain
Web API ──┘                │
                           ▼
                       Repository
                           │
                           ▼
                         SQLite
```
Layers

* Domain — ProjectGroup, Project, Task, ScheduleEntry.
* Repository — persistence abstraction + SQLAlchemy implementation.
* Service — application/use-case logic and orchestration.
* API — FastAPI routers + Pydantic request/response models.
* CLI/TUI — first frontend; can use the same service layer.
* Core — configuration, exceptions, logging, etc.

Keep domain models independent from SQLAlchemy models and API DTOs.

## Initial stack

* Python
* FastAPI
* SQLAlchemy
* SQLite
* Pydantic
* uv

Start with a CLI/TUI if useful, then add the web frontend later.

The application should be structured so SQLite can eventually be replaced by PostgreSQL and accessed by multiple devices without redesigning the domain/application layers.