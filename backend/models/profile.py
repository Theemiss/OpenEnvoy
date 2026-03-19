from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, DateTime, JSON, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from ..core.database import Base


class Profile(Base):
    """Canonical user profile."""
    
    id: Mapped[int] = mapped_column(primary_key=True)
    version: Mapped[int] = mapped_column(default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Personal info
    full_name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50))
    location: Mapped[Optional[str]] = mapped_column(String(255))
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(1024))
    github_url: Mapped[Optional[str]] = mapped_column(String(1024))
    portfolio_url: Mapped[Optional[str]] = mapped_column(String(1024))
    
    # Professional summary
    title: Mapped[str] = mapped_column(String(255))  # Current title
    summary: Mapped[str] = mapped_column(Text)  # Professional summary
    
    # Structured data
    skills: Mapped[list] = mapped_column(JSON, default=list)
    languages: Mapped[list] = mapped_column(JSON, default=list)  # Programming languages
    tools: Mapped[list] = mapped_column(JSON, default=list)  # Tools/technologies
    domains: Mapped[list] = mapped_column(JSON, default=list)  # Domain expertise
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    source: Mapped[str] = mapped_column(String(50), default="manual")  # manual, github, linkedin
    
    # Relationships
    experiences: Mapped[list["Experience"]] = relationship(
        back_populates="profile",
        cascade="all, delete-orphan"
    )
    education: Mapped[list["Education"]] = relationship(
        back_populates="profile",
        cascade="all, delete-orphan"
    )
    projects: Mapped[list["Project"]] = relationship(
        back_populates="profile",
        cascade="all, delete-orphan"
    )
    certifications: Mapped[list["Certification"]] = relationship(
        back_populates="profile",
        cascade="all, delete-orphan"
    )
    resumes: Mapped[list["Resume"]] = relationship(
        back_populates="profile",
        cascade="all, delete-orphan"
    )


class Experience(Base):
    """Work experience entry."""
    
    id: Mapped[int] = mapped_column(primary_key=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("profile.id"))
    
    company: Mapped[str] = mapped_column(String(255))
    title: Mapped[str] = mapped_column(String(255))
    location: Mapped[Optional[str]] = mapped_column(String(255))
    
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    is_current: Mapped[bool] = mapped_column(Boolean, default=False)
    
    description: Mapped[str] = mapped_column(Text)
    achievements: Mapped[list] = mapped_column(JSON, default=list)
    skills_used: Mapped[list] = mapped_column(JSON, default=list)
    technologies: Mapped[list] = mapped_column(JSON, default=list)
    
    profile: Mapped["Profile"] = relationship(back_populates="experiences")


class Education(Base):
    """Education entry."""
    
    id: Mapped[int] = mapped_column(primary_key=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("profile.id"))
    
    institution: Mapped[str] = mapped_column(String(255))
    degree: Mapped[str] = mapped_column(String(255))
    field: Mapped[str] = mapped_column(String(255))
    
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    grade: Mapped[Optional[str]] = mapped_column(String(50))
    achievements: Mapped[list] = mapped_column(JSON, default=list)
    
    profile: Mapped["Profile"] = relationship(back_populates="education")


class Project(Base):
    """Project entry (from GitHub or manual)."""
    
    id: Mapped[int] = mapped_column(primary_key=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("profile.id"))
    
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    url: Mapped[Optional[str]] = mapped_column(String(1024))
    
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    is_current: Mapped[bool] = mapped_column(Boolean, default=False)
    
    technologies: Mapped[list] = mapped_column(JSON, default=list)
    role: Mapped[Optional[str]] = mapped_column(String(255))
    highlights: Mapped[list] = mapped_column(JSON, default=list)
    
    source: Mapped[str] = mapped_column(String(50), default="manual")  # manual, github
    source_id: Mapped[Optional[str]] = mapped_column(String(255))  # GitHub repo ID
    
    stars: Mapped[Optional[int]] = mapped_column(default=0)  # GitHub stars
    forks: Mapped[Optional[int]] = mapped_column(default=0)  # GitHub forks
    language: Mapped[Optional[str]] = mapped_column(String(50))  # Primary language
    
    profile: Mapped["Profile"] = relationship(back_populates="projects")


class Certification(Base):
    """Certification entry."""
    
    id: Mapped[int] = mapped_column(primary_key=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("profile.id"))
    
    name: Mapped[str] = mapped_column(String(255))
    issuing_org: Mapped[str] = mapped_column(String(255))
    credential_id: Mapped[Optional[str]] = mapped_column(String(255))
    credential_url: Mapped[Optional[str]] = mapped_column(String(1024))
    
    issue_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    expiry_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    does_not_expire: Mapped[bool] = mapped_column(Boolean, default=False)
    
    profile: Mapped["Profile"] = relationship(back_populates="certifications")


class Resume(Base):
    """Resume versions."""
    
    id: Mapped[int] = mapped_column(primary_key=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("profile.id"))
    
    version: Mapped[str] = mapped_column(String(50))  # canonical, tailored
    name: Mapped[str] = mapped_column(String(255))  # Display name
    is_canonical: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Storage
    file_path: Mapped[str] = mapped_column(String(1024))  # S3 key or local path
    file_type: Mapped[str] = mapped_column(String(10))  # pdf, docx
    file_size: Mapped[int] = mapped_column(default=0)
    
    # Structured data
    content_json: Mapped[dict] = mapped_column(JSON)  # Parsed resume data
    
    # For tailored resumes
    job_id: Mapped[Optional[int]] = mapped_column(ForeignKey("job.id"))
    prompt_used: Mapped[Optional[str]] = mapped_column(Text)
    model_used: Mapped[Optional[str]] = mapped_column(String(50))
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    
    profile: Mapped["Profile"] = relationship(back_populates="resumes")