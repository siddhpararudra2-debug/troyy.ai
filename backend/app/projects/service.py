"""
Troy — Project Service
Business logic for project management.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.projects.schemas import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse,
)
from app.core.logging import get_logger

logger = get_logger("projects")


async def create_project(data: ProjectCreate, db: AsyncSession) -> ProjectResponse:
    """Create a new engineering project."""
    project_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()

    await db.execute(
        text("""
            INSERT INTO projects (id, name, description, domain, status, created_at, updated_at)
            VALUES (:id, :name, :desc, :domain, 'active', :now, :now)
        """),
        {"id": project_id, "name": data.name, "desc": data.description,
         "domain": data.domain, "now": now},
    )
    await db.commit()

    return ProjectResponse(
        id=project_id, name=data.name, description=data.description,
        domain=data.domain, status="active", created_at=now, updated_at=now,
    )


async def list_projects(db: AsyncSession) -> ProjectListResponse:
    """List all projects with calculation counts."""
    result = await db.execute(
        text("""
            SELECT p.id, p.name, p.description, p.domain, p.status,
                   p.created_at, p.updated_at,
                   COUNT(DISTINCT c.id) as calc_count,
                   COUNT(DISTINCT d.id) as doc_count
            FROM projects p
            LEFT JOIN calculations c ON c.project_id = p.id
            LEFT JOIN documents d ON d.project_id = p.id
            GROUP BY p.id
            ORDER BY p.updated_at DESC
        """)
    )
    rows = result.fetchall()

    projects = [
        ProjectResponse(
            id=row[0], name=row[1], description=row[2],
            domain=row[3], status=row[4],
            created_at=row[5] or "", updated_at=row[6] or "",
            calculation_count=row[7], document_count=row[8],
        )
        for row in rows
    ]

    return ProjectListResponse(projects=projects, total=len(projects))


async def get_project(project_id: str, db: AsyncSession) -> ProjectResponse | None:
    """Get a single project by ID."""
    result = await db.execute(
        text("""
            SELECT p.id, p.name, p.description, p.domain, p.status,
                   p.created_at, p.updated_at,
                   COUNT(DISTINCT c.id) as calc_count,
                   COUNT(DISTINCT d.id) as doc_count
            FROM projects p
            LEFT JOIN calculations c ON c.project_id = p.id
            LEFT JOIN documents d ON d.project_id = p.id
            WHERE p.id = :id
            GROUP BY p.id
        """),
        {"id": project_id},
    )
    row = result.fetchone()
    if not row:
        return None

    return ProjectResponse(
        id=row[0], name=row[1], description=row[2],
        domain=row[3], status=row[4],
        created_at=row[5] or "", updated_at=row[6] or "",
        calculation_count=row[7], document_count=row[8],
    )


async def update_project(
    project_id: str, data: ProjectUpdate, db: AsyncSession
) -> ProjectResponse | None:
    """Update an existing project."""
    existing = await get_project(project_id, db)
    if not existing:
        return None

    updates = {}
    if data.name is not None:
        updates["name"] = data.name
    if data.description is not None:
        updates["description"] = data.description
    if data.domain is not None:
        updates["domain"] = data.domain
    if data.status is not None:
        updates["status"] = data.status

    if updates:
        set_clause = ", ".join(f"{k} = :{k}" for k in updates)
        updates["id"] = project_id
        updates["now"] = datetime.utcnow().isoformat()
        await db.execute(
            text(f"UPDATE projects SET {set_clause}, updated_at = :now WHERE id = :id"),
            updates,
        )
        await db.commit()

    return await get_project(project_id, db)


async def delete_project(project_id: str, db: AsyncSession) -> bool:
    """Delete (archive) a project."""
    result = await db.execute(
        text("UPDATE projects SET status = 'archived', updated_at = :now WHERE id = :id"),
        {"id": project_id, "now": datetime.utcnow().isoformat()},
    )
    await db.commit()
    return result.rowcount > 0
