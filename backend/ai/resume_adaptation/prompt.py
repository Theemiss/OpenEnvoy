"""Prompt templates for resume adaptation."""

RESUME_ADAPTATION_PROMPT = """
You are an expert resume writer. Your task is to adapt a candidate's canonical resume to match a specific job description.

## Job Description
Title: {job_title}
Company: {job_company}
Description:
{job_description}

## Key Requirements
{key_requirements}

## Canonical Resume (JSON format)
{canonical_resume_json}

## Instructions
Create a tailored version of this resume that:
1. Prioritizes experience and projects most relevant to the job
2. Rewrites the professional summary to match the job's language
3. Emphasizes skills mentioned in the job description
4. Reorders bullet points to highlight relevant achievements
5. Keeps all information truthful - do not invent experience

Return the adapted resume as a JSON object with the same structure as the input, but with modified content.

The response should include:
- Updated professional summary
- Reordered and possibly reworded experience bullets
- Reordered skills with relevant ones first
- Reordered projects with most relevant first
- A brief explanation of the changes made

Return format:
{{
    "adapted_resume": {{
        "personal": {{...}},
        "summary": "adapted summary...",
        "skills": ["skill1", "skill2", ...],
        "experience": [...],
        "education": [...],
        "projects": [...],
        "certifications": [...]
    }},
    "changes_made": "Explanation of key adaptations",
    "targeted_skills": ["skill1", "skill2"],
    "confidence": <0-100>
}}
"""


RESUME_REORDER_PROMPT = """
Reorder and slightly modify this experience section to better match the job requirements.

Job Keywords: {job_keywords}

Original Experience:
{experience_json}

Instructions:
- Reorder bullet points within each role to put relevant achievements first
- Keep all facts unchanged, only reorder and possibly rephrase for relevance
- Ensure each bullet starts with a strong action verb

Return only the reordered experience JSON array.
"""


SUMMARY_ADAPTATION_PROMPT = """
Rewrite this professional summary to target this specific role:

Original Summary: {original_summary}

Job Title: {job_title}
Key Requirements: {key_requirements}

Write a 2-3 sentence summary that highlights the most relevant experience and skills.
Keep it professional and impactful.
"""