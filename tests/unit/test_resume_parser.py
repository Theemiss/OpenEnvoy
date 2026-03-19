"""Tests for resume parser."""

import pytest
from pathlib import Path
import json

from backend.ingestion.resume.parser import ResumeParser, ResumeStorage
from backend.ingestion.resume.extractors import DateExtractor, SkillExtractor


@pytest.mark.asyncio
async def test_resume_parser_text(sample_resume_path):
    """Test parsing text resume."""
    parser = ResumeParser()
    
    # Create a simple text file
    with open(sample_resume_path, 'r') as f:
        content = f.read()
    
    # Parse as text (simulating with _structure_resume)
    result = parser._structure_resume(content)
    
    assert result["personal"]["email"] == "john@example.com"
    assert "Python" in result["skills"]
    assert len(result["experience"]) > 0
    assert len(result["education"]) > 0


def test_extract_sections():
    """Test section extraction."""
    parser = ResumeParser()
    
    lines = [
        "SUMMARY",
        "This is a summary",
        "EXPERIENCE",
        "Company - Title",
        "SKILLS",
        "Python, JavaScript"
    ]
    
    sections = parser._extract_sections(lines)
    
    assert "summary" in sections
    assert "experience" in sections
    assert "skills" in sections


def test_extract_personal_info():
    """Test personal info extraction."""
    parser = ResumeParser()
    
    text = """
    John Developer
    john@example.com
    555-123-4567
    linkedin.com/in/johndeveloper
    """
    
    info = parser._extract_personal_info(text)
    
    assert info["email"] == "john@example.com"
    assert info["phone"] == "555-123-4567"
    assert info["linkedin"] == "linkedin.com/in/johndeveloper"


def test_extract_skills():
    """Test skill extraction."""
    parser = ResumeParser()
    
    text = """
    Skills: Python, JavaScript, React, FastAPI
    Also experienced with Docker and AWS.
    """
    
    skills = parser._extract_skills(text)
    
    assert "python" in skills
    assert "javascript" in skills
    assert "react" in skills
    assert "docker" in skills
    assert "aws" in skills


def test_parse_experience():
    """Test experience parsing."""
    parser = ResumeParser()
    
    lines = [
        "Senior Developer at Tech Corp (2021-Present)",
        "• Led development team",
        "• Implemented new features",
        "",
        "Developer at Startup Inc (2018-2020)",
        "• Built web applications"
    ]
    
    experiences = parser._parse_experience(lines)
    
    assert len(experiences) == 2
    assert experiences[0]["title"] == "Senior Developer at Tech Corp"
    assert len(experiences[0]["description"]) == 2


def test_date_extractor():
    """Test date extraction."""
    # Test year range
    result = DateExtractor.extract_date_range("2020 - 2023")
    assert result["start_date"].year == 2020
    assert result["end_date"].year == 2023
    assert not result["is_current"]
    
    # Test with present
    result = DateExtractor.extract_date_range("2021 - Present")
    assert result["start_date"].year == 2021
    assert result["end_date"] is None
    assert result["is_current"]
    
    # Test with months
    result = DateExtractor.extract_date_range("Jan 2020 - Mar 2023")
    assert result["start_date"].month == 1
    assert result["start_date"].year == 2020
    assert result["end_date"].month == 3
    assert result["end_date"].year == 2023


def test_skill_extractor_categorize():
    """Test skill categorization."""
    skills = ["Python", "React", "AWS", "Docker", "Git", "Unknown Skill"]
    
    categorized = SkillExtractor.extract_with_categories(skills)
    
    assert "Python" in categorized["languages"]
    assert "React" in categorized["frameworks"]
    assert "AWS" in categorized["cloud"]
    assert "Docker" in categorized["devops"]
    assert "Git" in categorized["tools"]
    assert "Unknown Skill" in categorized["other"]


@pytest.mark.asyncio
async def test_resume_storage(session, test_profile, sample_resume_path, cleanup_files):
    """Test resume storage."""
    storage = ResumeStorage()
    
    # Store resume
    resume_id = await storage.store_canonical_resume(
        sample_resume_path,
        "txt",
        test_profile.id
    )
    
    assert resume_id is not None
    
    # Retrieve
    from backend.models.profile import Resume
    resume = await session.get(Resume, resume_id)
    
    assert resume is not None
    assert resume.profile_id == test_profile.id
    assert resume.is_canonical
    assert resume.content_json is not None
    assert "personal" in resume.content_json