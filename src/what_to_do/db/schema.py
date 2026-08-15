"""Database schema / table definitions."""

from uuid import UUID

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from what_to_do.tasks.models import Priority


class Base(DeclarativeBase):
    pass


class DBGroup(Base):
    __tablename__ = "groups"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    tasks: Mapped[list[DBTask]] = relationship(back_populates="group")
    projects: Mapped[list[DBProject]] = relationship(back_populates="group")


class DBProject(Base):
    __tablename__ = "projects"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    group_id: Mapped[UUID] = mapped_column(ForeignKey("groups.id"))
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(nullable=True)
    tasks: Mapped[list[DBTask]] = relationship(back_populates="project")
    group: Mapped[DBGroup] = relationship(back_populates="projects")


class DBTask(Base):
    __tablename__ = "tasks"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    group_id: Mapped[UUID] = mapped_column(ForeignKey("groups.id"))
    project_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("projects.id"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(nullable=True)
    priority: Mapped[Priority | None] = mapped_column(Enum(Priority), nullable=True)

    # object-level relations in sql-alchemy (not the db schema)
    group: Mapped[DBGroup] = relationship(back_populates="tasks")
    project: Mapped[DBProject] = relationship(back_populates="tasks")
