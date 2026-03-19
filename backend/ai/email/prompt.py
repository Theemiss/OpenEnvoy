"""Email drafting prompts."""

COVER_LETTER_PROMPT = """
Write a concise, professional cover letter for a job application.

## Job Details
Company: {company}
Position: {position}
Job Description: {job_description}

## Candidate Information
Name: {name}
Current Role: {current_role}
Key Skills: {skills}
Relevant Projects: {projects_summary}
Experience Summary: {experience_summary}

## Instructions
Write a cover letter that:
1. Is 150-250 words (3-4 short paragraphs)
2. Highlights the most relevant experience and skills
3. Shows genuine interest in the company and role
4. Is professional but not overly formal
5. Includes a clear call to action

Format it as plain text with proper paragraphs.
Do not include placeholders in brackets.
"""


INITIAL_OUTREACH_PROMPT = """
Write a brief, personalized email to introduce yourself to a recruiter or hiring manager.

## Context
You're applying for: {position} at {company}
Your Name: {name}
Relevant Project/Experience: {highlight}

## Instructions
Write a short email (100-150 words) that:
1. References the specific role you're applying for
2. Mentions 1-2 relevant achievements or projects
3. Attaches your resume (mention this)
4. Is polite and professional
5. Ends with a question or call to action

Subject line should be: Application for {position} - {name}

Return both subject and body as a JSON object.
"""


FOLLOW_UP_PROMPT = """
Write a polite follow-up email for a job application.

## Context
Position: {position}
Company: {company}
Days since application: {days_since}
Previous email sent: {previous_email_preview}

## Instructions
Write a brief follow-up email (under 100 words) that:
1. References your previous application
2. Reiterates your interest
3. Asks politely about the status
4. Is not pushy or demanding

Return both subject and body as JSON.
"""


THANK_YOU_PROMPT = """
Write a thank you email after an interview.

## Context
Position: {position}
Company: {company}
Interviewer: {interviewer_name} (if known)
Interview Date: {interview_date}
Key discussion points: {discussion_points}

## Instructions
Write a thank you email that:
1. Expresses gratitude for the interview
2. Mentions 1-2 specific topics discussed
3. Reaffirms your interest in the role
4. Is concise and professional

Return both subject and body as JSON.
"""


EMAIL_CACHE_KEY = "email:{job_id}:{profile_id}:{template_type}"