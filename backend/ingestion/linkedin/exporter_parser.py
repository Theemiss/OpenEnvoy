"""Parser for LinkedIn data export files."""

import json
import csv
import zipfile
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from ...models.profile import Profile, Experience, Education, Project
from ...core.database import db_manager

logger = logging.getLogger(__name__)


class LinkedInExportParser:
    """Parse LinkedIn data export (GDPR download)."""
    
    def __init__(self, export_path: Path):
        self.export_path = export_path
        self.data = {}
    
    async def parse(self) -> Dict[str, Any]:
        """Parse the entire export."""
        
        if self.export_path.suffix == '.zip':
            return await self._parse_zip()
        elif self.export_path.is_dir():
            return await self._parse_directory()
        else:
            raise ValueError(f"Unsupported export format: {self.export_path}")
    
    async def _parse_zip(self) -> Dict[str, Any]:
        """Parse a zip file export."""
        
        with zipfile.ZipFile(self.export_path, 'r') as zip_file:
            # Extract to temp directory
            import tempfile
            with tempfile.TemporaryDirectory() as temp_dir:
                zip_file.extractall(temp_dir)
                
                # Parse extracted files
                return await self._parse_directory(Path(temp_dir))
    
    async def _parse_directory(self, dir_path: Optional[Path] = None) -> Dict[str, Any]:
        """Parse a directory of exported files."""
        
        base_path = dir_path or self.export_path
        
        # Parse profile information
        profile = await self._parse_profile(base_path)
        
        # Parse connections
        connections = await self._parse_connections(base_path)
        
        # Parse positions (experience)
        positions = await self._parse_positions(base_path)
        
        # Parse education
        education = await self._parse_education(base_path)
        
        # Parse skills
        skills = await self._parse_skills(base_path)
        
        # Parse recommendations
        recommendations = await self._parse_recommendations(base_path)
        
        # Parse messages
        messages = await self._parse_messages(base_path)
        
        return {
            "profile": profile,
            "connections": connections,
            "positions": positions,
            "education": education,
            "skills": skills,
            "recommendations": recommendations,
            "messages": messages
        }
    
    async def _parse_profile(self, base_path: Path) -> Dict[str, Any]:
        """Parse profile information."""
        profile_data = {}
        
        # Try various possible file names
        profile_files = [
            base_path / "Profile.csv",
            base_path / "profile.csv",
            base_path / "profile.json"
        ]
        
        for file_path in profile_files:
            if file_path.exists():
                if file_path.suffix == '.csv':
                    with open(file_path, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            profile_data.update(row)
                elif file_path.suffix == '.json':
                    with open(file_path, 'r', encoding='utf-8') as f:
                        profile_data = json.load(f)
                break
        
        # Try to find in other files
        if not profile_data:
            # Check for Positions.csv which often contains current role
            positions_file = base_path / "Positions.csv"
            if positions_file.exists():
                with open(positions_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row.get('Current Position') == 'Yes':
                            profile_data['current_title'] = row.get('Title')
                            profile_data['current_company'] = row.get('Company Name')
        
        return profile_data
    
    async def _parse_connections(self, base_path: Path) -> List[Dict[str, Any]]:
        """Parse connections."""
        connections = []
        
        connections_file = base_path / "Connections.csv"
        if connections_file.exists():
            with open(connections_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    connections.append({
                        "first_name": row.get("First Name"),
                        "last_name": row.get("Last Name"),
                        "email": row.get("Email Address"),
                        "company": row.get("Company"),
                        "position": row.get("Position"),
                        "connected_on": row.get("Connected On")
                    })
        
        return connections
    
    async def _parse_positions(self, base_path: Path) -> List[Dict[str, Any]]:
        """Parse work experience."""
        positions = []
        
        positions_file = base_path / "Positions.csv"
        if positions_file.exists():
            with open(positions_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Parse dates
                    start_date = None
                    end_date = None
                    
                    if row.get("Started On"):
                        try:
                            start_date = datetime.strptime(row["Started On"], "%Y-%m-%d")
                        except:
                            pass
                    
                    if row.get("Finished On") and row["Finished On"] != "Present":
                        try:
                            end_date = datetime.strptime(row["Finished On"], "%Y-%m-%d")
                        except:
                            pass
                    
                    position = {
                        "title": row.get("Title"),
                        "company": row.get("Company Name"),
                        "location": row.get("Location"),
                        "description": row.get("Description"),
                        "start_date": start_date.isoformat() if start_date else None,
                        "end_date": end_date.isoformat() if end_date else None,
                        "is_current": row.get("Current Position") == "Yes"
                    }
                    positions.append(position)
        
        return positions
    
    async def _parse_education(self, base_path: Path) -> List[Dict[str, Any]]:
        """Parse education."""
        education = []
        
        education_file = base_path / "Education.csv"
        if education_file.exists():
            with open(education_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    edu = {
                        "school": row.get("School Name"),
                        "degree": row.get("Degree Name"),
                        "field": row.get("Field Of Study"),
                        "start_date": row.get("Start Date"),
                        "end_date": row.get("End Date"),
                        "notes": row.get("Notes")
                    }
                    education.append(edu)
        
        return education
    
    async def _parse_skills(self, base_path: Path) -> List[Dict[str, Any]]:
        """Parse skills and endorsements."""
        skills = []
        
        skills_file = base_path / "Skills.csv"
        if skills_file.exists():
            with open(skills_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    skills.append({
                        "name": row.get("Name"),
                        "endorsements": row.get("Endorsement Count")
                    })
        
        return skills
    
    async def _parse_recommendations(self, base_path: Path) -> List[Dict[str, Any]]:
        """Parse recommendations."""
        recommendations = []
        
        rec_file = base_path / "Recommendations.csv"
        if rec_file.exists():
            with open(rec_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    recommendations.append(row)
        
        return recommendations
    
    async def _parse_messages(self, base_path: Path) -> List[Dict[str, Any]]:
        """Parse messages."""
        messages = []
        
        messages_file = base_path / "Messages.csv"
        if messages_file.exists():
            with open(messages_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    messages.append({
                        "from": row.get("From"),
                        "to": row.get("To"),
                        "date": row.get("Date"),
                        "subject": row.get("Subject"),
                        "content": row.get("Content")
                    })
        
        return messages
    
    async def import_to_profile(self, profile_id: int) -> Dict[str, Any]:
        """Import LinkedIn data to existing profile."""
        
        data = await self.parse()
        
        async with db_manager.session() as session:
            profile = await session.get(Profile, profile_id)
            if not profile:
                raise ValueError(f"Profile {profile_id} not found")
            
            # Update profile with LinkedIn data
            if data["profile"]:
                profile_data = data["profile"]
                
                if profile_data.get("current_title") and not profile.title:
                    profile.title = profile_data["current_title"]
                
                if profile_data.get("email") and not profile.email:
                    profile.email = profile_data["email"]
            
            # Add positions as experience
            for pos in data["positions"]:
                # Check if already exists
                existing = next(
                    (e for e in profile.experiences 
                     if e.company == pos["company"] and e.title == pos["title"]),
                    None
                )
                
                if not existing:
                    experience = Experience(
                        profile_id=profile_id,
                        company=pos["company"],
                        title=pos["title"],
                        location=pos["location"],
                        description=pos["description"],
                        is_current=pos["is_current"]
                    )
                    
                    if pos["start_date"]:
                        experience.start_date = datetime.fromisoformat(pos["start_date"])
                    
                    if pos["end_date"]:
                        experience.end_date = datetime.fromisoformat(pos["end_date"])
                    
                    session.add(experience)
            
            # Add education
            for edu in data["education"]:
                existing = next(
                    (e for e in profile.education 
                     if e.institution == edu["school"] and e.degree == edu["degree"]),
                    None
                )
                
                if not existing:
                    education = Education(
                        profile_id=profile_id,
                        institution=edu["school"],
                        degree=edu["degree"],
                        field=edu["field"]
                    )
                    session.add(education)
            
            # Add skills
            if data["skills"]:
                current_skills = set(profile.skills or [])
                for skill in data["skills"]:
                    if skill["name"] not in current_skills:
                        current_skills.add(skill["name"])
                
                profile.skills = list(current_skills)
            
            await session.commit()
            
            return {
                "profile_updated": True,
                "positions_added": len(data["positions"]),
                "education_added": len(data["education"]),
                "skills_added": len([s for s in data["skills"] if s["name"] not in current_skills])
            }