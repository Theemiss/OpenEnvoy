#!/usr/bin/env python3
"""Seed initial data for development."""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.core.database import db_manager
from backend.core.config import settings
from backend.models.profile import Profile, Experience, Education, Project, Resume
from backend.models.job import Job


async def seed_profile():
    """Seed a sample profile."""
    async with db_manager.session() as session:
        # Check if profile exists
        from sqlalchemy import select
        result = await session.execute(select(Profile).where(Profile.email == "user@example.com"))
        if result.scalar_one_or_none():
            print("Profile already exists, skipping...")
            return
        
        # Create profile
        profile = Profile(
            full_name="John Developer",
            email="user@example.com",
            title="Senior Software Engineer",
            summary="Experienced full-stack developer with 8 years of expertise in Python, React, and cloud architecture. Passionate about building scalable systems and mentoring junior developers.",
            skills=["Python", "JavaScript", "TypeScript", "React", "Node.js", "FastAPI", "Django", "AWS", "Docker", "Kubernetes", "PostgreSQL", "Redis"],
            languages=["Python", "JavaScript", "TypeScript", "SQL"],
            tools=["Git", "Docker", "Kubernetes", "Terraform", "Jenkins", "VS Code"],
            domains=["FinTech", "E-commerce", "SaaS"],
            source="manual"
        )
        session.add(profile)
        await session.flush()
        
        # Add experiences
        experiences = [
            Experience(
                profile_id=profile.id,
                company="Tech Corp",
                title="Senior Software Engineer",
                start_date=datetime(2021, 1, 1),
                is_current=True,
                description="Leading development of microservices architecture. Mentoring 4 junior developers. Implementing CI/CD pipelines.",
                achievements=[
                    "Reduced API response time by 40% through query optimization",
                    "Led migration from monolith to microservices",
                    "Implemented automated testing increasing coverage to 85%"
                ],
                skills_used=["Python", "FastAPI", "AWS", "Docker", "Kubernetes"],
                technologies=["Python", "FastAPI", "PostgreSQL", "Redis", "Kafka"]
            ),
            Experience(
                profile_id=profile.id,
                company="Startup Inc",
                title="Full Stack Developer",
                start_date=datetime(2018, 3, 1),
                end_date=datetime(2020, 12, 31),
                description="Developed and maintained multiple client projects. Worked across the full stack from database design to frontend implementation.",
                achievements=[
                    "Built real-time dashboard used by 500+ customers",
                    "Integrated 3rd-party APIs reducing manual work by 20 hours/week",
                    "Won company innovation award for automation tool"
                ],
                skills_used=["JavaScript", "React", "Node.js", "MongoDB"],
                technologies=["React", "Node.js", "Express", "MongoDB", "Socket.io"]
            )
        ]
        session.add_all(experiences)
        
        # Add education
        education = Education(
            profile_id=profile.id,
            institution="University of Technology",
            degree="Bachelor of Science",
            field="Computer Science",
            start_date=datetime(2014, 9, 1),
            end_date=datetime(2018, 6, 1),
            grade="3.8 GPA",
            achievements=["Dean's List 4 semesters", "Senior Project Award"]
        )
        session.add(education)
        
        # Add projects
        projects = [
            Project(
                profile_id=profile.id,
                name="E-commerce Platform",
                description="Full-stack e-commerce platform with real-time inventory management",
                url="https://github.com/user/ecommerce",
                technologies=["React", "Node.js", "PostgreSQL", "Redis"],
                highlights=[
                    "Implemented real-time inventory updates using WebSockets",
                    "Designed scalable database schema handling 10k+ products",
                    "Integrated Stripe payment processing"
                ],
                source="manual"
            ),
            Project(
                profile_id=profile.id,
                name="Task Automation CLI",
                description="CLI tool for automating development workflows",
                url="https://github.com/user/task-cli",
                technologies=["Python", "Click", "Docker"],
                highlights=[
                    "Reduced setup time for new projects by 70%",
                    "Published to PyPI with 1k+ downloads",
                    "Open source with 5 contributors"
                ],
                source="manual"
            )
        ]
        session.add_all(projects)
        
        # Add canonical resume
        resume = Resume(
            profile_id=profile.id,
            version="canonical",
            name="Canonical Resume",
            is_canonical=True,
            file_path="resumes/canonical.json",
            file_type="json",
            content_json={
                "personal": {
                    "name": "John Developer",
                    "email": "user@example.com",
                    "phone": "+1-555-123-4567",
                    "location": "San Francisco, CA",
                    "linkedin": "linkedin.com/in/johndeveloper",
                    "github": "github.com/user"
                },
                "summary": profile.summary,
                "skills": profile.skills,
                "languages": profile.languages,
                "experience": [
                    {
                        "company": "Tech Corp",
                        "title": "Senior Software Engineer",
                        "start_date": "2021-01",
                        "current": True,
                        "description": "Leading development...",
                        "achievements": experiences[0].achievements
                    }
                ]
            }
        )
        session.add(resume)
        
        await session.commit()
        print(f"Profile created with ID: {profile.id}")


async def seed_jobs():
    """Seed sample jobs for testing."""
    async with db_manager.session() as session:
        from sqlalchemy import select
        
        # Check if jobs exist
        result = await session.execute(select(Job).limit(1))
        if result.scalar_one_or_none():
            print("Jobs already exist, skipping...")
            return
        
        # Sample jobs
        jobs = [
            Job(
                source="linkedin",
                url="https://linkedin.com/jobs/1",
                title="Senior Python Developer",
                company="Tech Company A",
                location="San Francisco, CA",
                salary_min=150000,
                salary_max=180000,
                salary_currency="USD",
                job_type="full-time",
                experience_level="senior",
                description="Looking for a senior Python developer with FastAPI and AWS experience...",
                posted_at=datetime.now() - timedelta(days=2),
                is_active=True
            ),
            Job(
                source="linkedin",
                url="https://linkedin.com/jobs/2",
                title="Full Stack Engineer",
                company="Startup B",
                location="Remote",
                salary_min=120000,
                salary_max=150000,
                salary_currency="USD",
                job_type="full-time",
                experience_level="mid",
                description="Join our fast-growing startup as a full stack engineer. React and Node.js experience required...",
                posted_at=datetime.now() - timedelta(days=5),
                is_active=True
            ),
            Job(
                source="adzuna",
                url="https://adzuna.com/jobs/3",
                title="Backend Developer",
                company="Enterprise C",
                location="New York, NY",
                salary_min=130000,
                salary_max=160000,
                salary_currency="USD",
                job_type="full-time",
                experience_level="mid",
                description="Backend developer needed for enterprise financial applications. Experience with distributed systems required...",
                posted_at=datetime.now() - timedelta(days=1),
                is_active=True
            )
        ]
        
        session.add_all(jobs)
        await session.commit()
        print(f"Seeded {len(jobs)} jobs")


async def main():
    """Main seed function."""
    print("Seeding development database...")
    
    await db_manager.initialize()
    
    try:
        await seed_profile()
        await seed_jobs()
    finally:
        await db_manager.close()
    
    print("Seeding complete!")


if __name__ == "__main__":
    asyncio.run(main())