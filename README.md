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


# IMPLEMENTATION CLI 

### Command tree

```
what-to-do
│
├── task
│   ├── list
│   ├── get <id>
│   ├── create [--title ...] [--description ...] [--group ...] [--project ...]
│   ├── update <id> [--title ...] [--description ...] [--group ...] [--project ...]
│   ├── delete <id>
│   └── assign <id> [--group ...] [--project ...]
│
├── project
│   ├── list
│   ├── get <id>
│   ├── create [--name ...] [--description ...] [--group ...]
│   ├── update <id> [--name ...] [--description ...] [--group ...]
│   ├── delete <id> [--keep-tasks]
│   ├── tasks <id>
│   └── assign <id> --group ...
│
├── group
│   ├── list
│   ├── get <id>
│   ├── create [--name ...]
│   ├── update <id> [--name ...]
│   ├── delete <id>
│   ├── tasks <id>
│   └── projects <id>
│
└── config
    ├── get
    ├── set
    └── reset


```

## Repo tree 

```
src/what_to_do/
│
├── api/
│   ├── server.py
│   ├── errors.py
│   └── v1/
│       ├── tasks.py
│       ├── projects.py
│       ├── groups.py
│       └── models.py
│
├── cli/
│   ├── entrypoint.py
│   ├── routing/
│   │   ├── tasks.py
│   │   ├── projects.py
│   │   ├── groups.py
│   │   └── config.py
│   ├── clients/
│   │   ├── client.py
│   │   ├── local.py
│   │   └── remote.py
│   └── messages/
│       └── ...
│
├── core/
│   ├── settings.py
│   └── ...
│
├── service/
│   ├── task_service.py
│   ├── project_service.py
│   └── group_service.py
│
├── db/
│   └── ...
│
└── domain/
    └── ...
```
## Implementation Plan

### 1. Implement local clients
- [x] Define `Client[T]` protocol
- [x] Implement generic `LocalClient[T]`
- [x] Implement resource-specific local clients where needed
    - [x] `LocalTaskClient`
    - [x] `LocalProjectClient`
- [x] Keep groups on generic `LocalClient[Group]`
- [x] Add unit tests for clients
- [x] Verify local clients use existing services + SQLite repositories

### 2. Implement client factory
- [x] Centralize client selection
- [x] Initially support local clients only
- [ ] Keep CLI/TUI unaware of concrete client implementations
- [ ] Return `Client[T]` to callers

### 3. Implement task routing
- [ ] Typer command group
- [ ] Argument/option handling
- [ ] Prompting
- [ ] Client calls
- [ ] CLI error handling
- [ ] Output formatting

### 4. Implement project routing
- [ ] Typer command group
- [ ] Argument/option handling
- [ ] Prompting
- [ ] Client calls
- [ ] CLI error handling
- [ ] Output formatting

### 5. Implement group routing
- [ ] Typer command group
- [ ] Argument/option handling
- [ ] Prompting
- [ ] Client calls
- [ ] CLI error handling
- [ ] Output formatting

### 6. Implement config routing
- [ ] `get`
- [ ] `set`
- [ ] `reset`
- [ ] Initially support local mode only
- [ ] Configure local database path

### 7. Implement CLI entrypoint
- [ ] Create main Typer app
- [ ] Register command groups
- [ ] Configure client selection
- [ ] Keep entrypoint free of command/business logic

### 8. CLI integration tests
- [ ] Use Typer `CliRunner` to invoke the actual application
- [ ] Test exit codes, output, input, routing, and wiring
- [ ] Use the same test database infrastructure/configuration as the API integration tests
- [ ] Test meaningful end-to-end CLI flows
- [ ] Don’t duplicate service tests

### 9. Local CLI installation
- [ ] Expose the CLI as an installed executable
- [ ] Configure the package entry point
- [ ] Verify `what-to-do` works outside the repository
- [ ] Use `uv tool install` / editable installation as appropriate
- [ ] Verify source changes are reflected with editable installation

### 10. Makefile
- [ ] `make test` → run pytest + coverage
- [ ] `make cli-local` → install/setup local CLI
- [ ] `make cli-update` → update/reinstall the installed CLI
- [ ] Possibly `make cli-uninstall` if useful
- [ ] Keep the exact pytest invocation in one memorable project-level command

### 11. Production/local release setup
- [ ] Finalize package metadata and CLI entry point
- [ ] Verify clean installation from outside the repository
- [ ] Verify configuration works for an installed CLI
- [ ] Verify local database creation/location
- [ ] Verify upgrades/reinstallation work
- [ ] Document basic installation and usage
- [ ] Make sure the local CLI is solid before adding remote functionality

### 12. Prepare remote architecture
- [ ] Define `RemoteClient[T]` around the existing `Client[T]` protocol
- [ ] Decide how HTTP requests/errors map to client/domain errors
- [ ] Add remote API configuration
- [ ] Add remote API URL to persistent config
- [ ] Update client factory to support local vs. remote mode
- [ ] Keep CLI routing unchanged

### 13. Implement remote clients
- [ ] Implement generic `RemoteClient[T]`
- [ ] Implement resource-specific remote clients where needed
    - [ ] `RemoteTaskClient`
    - [ ] `RemoteProjectClient`
- [ ] Keep groups on generic `RemoteClient[Group]`
- [ ] Reuse the existing API endpoints
- [ ] Add unit tests for remote clients

### 14. Remote CLI integration tests
- [ ] Test the CLI against the remote API
- [ ] Test meaningful end-to-end remote flows
- [ ] Test remote error handling
- [ ] Test switching between local and remote modes
- [ ] Avoid duplicating API integration tests unnecessarily

### 15. Production remote deployment
- [ ] Set up production Docker Compose
- [ ] Set up PostgreSQL
- [ ] Set up GCP VM
- [ ] Configure production environment/secrets
- [ ] Deploy FastAPI + PostgreSQL
- [ ] Verify API health and persistence
- [ ] Configure the CLI with the production API URL
- [ ] Verify remote CLI against the deployed API

### 16. After CLI is solid → TUI
- [ ] Reuse the same `Client[T]`
- [ ] Reuse the same configuration
- [ ] Reuse the same local/remote client factory
- [ ] Reuse the same domain/service layer
- [ ] No duplication of backend/business logic