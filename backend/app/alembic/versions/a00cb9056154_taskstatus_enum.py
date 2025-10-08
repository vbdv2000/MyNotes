"""TaskStatus enum

Revision ID: a00cb9056154
Revises: 04fd03807608
Create Date: 2025-10-09 00:24:27.290109

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import enum


# revision identifiers, used by Alembic.
revision: str = "a00cb9056154"
down_revision: Union[str, Sequence[str], None] = "04fd03807608"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class TaskStatus(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"


# Definimos el tipo ENUM específico para PostgreSQL
from sqlalchemy.dialects import postgresql

task_status_enum = postgresql.ENUM(
    "todo", "in_progress", "review", "done", name="taskstatus"
)


def upgrade() -> None:
    # 1. Crear el nuevo tipo ENUM en PostgreSQL
    op.execute(
        "CREATE TYPE taskstatus AS ENUM ('todo', 'in_progress', 'review', 'done')"
    )

    # 2. LIMPIEZA DE DATOS (Mapeo de valores antiguos, crucial para el casting)
    # Se mantienen las sentencias de limpieza de datos para evitar el error de "invalid input value"
    op.execute("UPDATE tasks SET status = 'todo' WHERE status = 'To Do'")
    op.execute("UPDATE tasks SET status = 'in_progress' WHERE status = 'In Progress'")
    op.execute("UPDATE tasks SET status = 'done' WHERE status = 'Done'")

    # 3. ELIMINAR EL DEFAULT ANTIGUO (String)
    # Esto es vital para que el cambio de tipo no falle por el default incompatible.
    op.alter_column(
        "tasks",
        "status",
        existing_type=sa.String(),
        server_default=None,  # Quitar el default
        existing_nullable=True,
    )

    # 4. Alterar la columna 'status' para cambiar el TIPO (usando el casting 'USING')
    op.alter_column(
        "tasks",
        "status",
        existing_type=sa.String(),
        type_=task_status_enum,
        postgresql_using="status::taskstatus",
        existing_nullable=True,
        server_default=None,  # Aseguramos que no se intente aplicar default aquí
    )

    # 5. APLICAR EL NUEVO DEFAULT (Enum)
    # Aplicamos el default 'todo' que es compatible con el nuevo tipo taskstatus
    op.alter_column(
        "tasks",
        "status",
        existing_type=task_status_enum,
        server_default="todo",
        existing_nullable=True,
    )


def downgrade() -> None:
    # 1. Alterar la columna 'status' de vuelta a String (antes de eliminar el tipo ENUM)
    op.alter_column(
        "tasks", "status", existing_type=task_status_enum, server_default=None
    )

    # 2. Alterar la columna 'status' de vuelta a String
    op.alter_column(
        "tasks",
        "status",
        existing_type=task_status_enum,
        type_=sa.String(),
        existing_nullable=True,
        # Mantenemos el antiguo default de tipo String, si es necesario.
        server_default="To Do",
    )

    # 3. Eliminar el tipo ENUM de PostgreSQL
    op.execute("DROP TYPE taskstatus")
