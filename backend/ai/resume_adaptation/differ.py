"""Resume diffing and change tracking."""

import difflib
from typing import Dict, Any, List, Tuple


class ResumeDiffer:
    """Track changes between canonical and tailored resumes."""
    
    def __init__(self, canonical: Dict[str, Any], tailored: Dict[str, Any]):
        self.canonical = canonical
        self.tailored = tailored
    
    def generate_diff_report(self) -> Dict[str, Any]:
        """Generate a report of changes made."""
        changes = {
            "summary_changed": self._summary_changed(),
            "skills_reordered": self._skills_reordered(),
            "skills_added": self._skills_added(),
            "skills_removed": self._skills_removed(),
            "experience_reordered": self._experience_reordered(),
            "experience_bullets_changed": self._experience_bullets_changed(),
            "projects_reordered": self._projects_reordered(),
            "change_count": 0
        }
        
        changes["change_count"] = sum(1 for v in changes.values() if v)
        
        return changes
    
    def _summary_changed(self) -> bool:
        """Check if summary was changed."""
        canonical_summary = self.canonical.get("summary", "")
        tailored_summary = self.tailored.get("summary", "")
        
        if not canonical_summary or not tailored_summary:
            return False
        
        # Check if significantly different (not just whitespace)
        return canonical_summary.strip() != tailored_summary.strip()
    
    def _skills_reordered(self) -> bool:
        """Check if skills were reordered."""
        canonical_skills = self.canonical.get("skills", [])
        tailored_skills = self.tailored.get("skills", [])
        
        return canonical_skills != tailored_skills
    
    def _skills_added(self) -> List[str]:
        """Find skills added in tailored version."""
        canonical_set = set(self.canonical.get("skills", []))
        tailored_set = set(self.tailored.get("skills", []))
        
        return list(tailored_set - canonical_set)
    
    def _skills_removed(self) -> List[str]:
        """Find skills removed in tailored version."""
        canonical_set = set(self.canonical.get("skills", []))
        tailored_set = set(self.tailored.get("skills", []))
        
        return list(canonical_set - tailored_set)
    
    def _experience_reordered(self) -> bool:
        """Check if experience entries were reordered."""
        canonical_exp = [e.get("company", "") + e.get("title", "") 
                        for e in self.canonical.get("experience", [])]
        tailored_exp = [e.get("company", "") + e.get("title", "") 
                       for e in self.tailored.get("experience", [])]
        
        return canonical_exp != tailored_exp
    
    def _experience_bullets_changed(self) -> List[Tuple[str, str, List[str]]]:
        """Find changes in experience bullet points."""
        changes = []
        
        canonical_exp = {e.get("company", ""): e for e in self.canonical.get("experience", [])}
        tailored_exp = {e.get("company", ""): e for e in self.tailored.get("experience", [])}
        
        for company, exp in tailored_exp.items():
            if company in canonical_exp:
                canonical_bullets = canonical_exp[company].get("achievements", [])
                tailored_bullets = exp.get("achievements", [])
                
                if canonical_bullets != tailored_bullets:
                    # Find reordered or modified bullets
                    diff = list(difflib.ndiff(canonical_bullets, tailored_bullets))
                    changes.append((company, diff))
        
        return changes
    
    def _projects_reordered(self) -> bool:
        """Check if projects were reordered."""
        canonical_projects = [p.get("name", "") for p in self.canonical.get("projects", [])]
        tailored_projects = [p.get("name", "") for p in self.tailored.get("projects", [])]
        
        return canonical_projects != tailored_projects
    
    def get_summary_text(self) -> str:
        """Get human-readable summary of changes."""
        changes = self.generate_diff_report()
        
        if not changes["change_count"]:
            return "No significant changes made to resume."
        
        parts = []
        
        if changes["summary_changed"]:
            parts.append("• Professional summary was rewritten")
        
        if changes["skills_reordered"]:
            added = changes["skills_added"]
            removed = changes["skills_removed"]
            
            if added:
                parts.append(f"• Added skills: {', '.join(added)}")
            if removed:
                parts.append(f"• De-emphasized: {', '.join(removed)}")
            if not added and not removed:
                parts.append("• Skills were reordered for relevance")
        
        if changes["experience_reordered"]:
            parts.append("• Experience entries were reordered")
        
        if changes["projects_reordered"]:
            parts.append("• Projects were reordered")
        
        return "\n".join(parts)