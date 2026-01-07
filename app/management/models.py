from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from sqlalchemy.sql import func
from app.database import Base


class Task(Base):
    """
    Task model representing a user task in the database.
    
    Indexes:
    - status: For efficient filtering by task status
    - priority: For efficient filtering by priority
    - created_at: For sorting by creation date
    """
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=False)
    status = Column(
        String(20),
        nullable=False,
        default="todo",
        index=True  # Index for filtering
    )
    priority = Column(
        String(20),
        nullable=False,
        default="medium",
        index=True  # Index for filtering
    )
    
    # AI-generated fields
    ai_summary = Column(Text, nullable=True)
    ai_suggested_priority = Column(String(20), nullable=True)
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True  # Index for sorting
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}', status='{self.status}')>"


# Composite index for common query patterns
Index('idx_status_priority', Task.status, Task.priority)
