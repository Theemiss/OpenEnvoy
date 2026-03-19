"""Prompt templates for job scoring."""

JOB_SCORING_PROMPT = """
You are an expert job matching system. Your task is to score how well a candidate's profile matches a job description.

## Candidate Profile
{profile_json}

## Job Description
Title: {job_title}
Company: {job_company}
Location: {job_location}
Description:
{job_description}

## Instructions
Score this match from 0-100 based on the following criteria:
- Skills match (40% weight): How well do the candidate's skills align with requirements?
- Experience match (30% weight): Does the candidate's experience level and domain match?
- Role alignment (20% weight): Is the job title and level appropriate for the candidate?
- Location/Culture (10% weight): Is the location acceptable? Does the company seem like a good fit?

Provide your response as a JSON object with the following structure:
{{
    "score": <integer 0-100>,
    "reasoning": "<brief explanation of the score>",
    "strengths": ["strength1", "strength2", ...],
    "weaknesses": ["weakness1", "weakness2", ...],
    "skill_match_percentage": <integer 0-100>,
    "experience_match": "<brief description>"
}}

Be honest and critical. A score of 70+ means the candidate is a strong match worth pursuing.
"""


CHEAP_SCORING_PROMPT = """
Score this job match (0-100) for the candidate:

Job: {job_title} at {job_company}
Requirements: {job_requirements_summary}

Candidate Skills: {candidate_skills}
Experience: {candidate_experience_summary}

Return only a JSON object with "score" (integer) and "reasoning" (string).
"""


SCORE_CACHE_KEY = "score:{job_id}:{profile_id}"