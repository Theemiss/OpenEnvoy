"""Prompts for email classification."""

REPLY_CLASSIFICATION_PROMPT = """
You are an AI assistant that categorizes recruiter email replies.

## Email Content
Subject: {subject}
From: {from_email}
Body:
{body}

## Instructions
Classify this email into one of the following categories:

1. INTERVIEW - Interview invitation, scheduling request
2. REJECTION - Rejection, not moving forward
3. INFO_REQUEST - Request for more information, portfolio, availability
4. ASSESSMENT - Coding challenge, technical assessment
5. FOLLOW_UP - Follow-up on previous communication
6. OFFER - Job offer
7. OTHER - Something else

Also determine:
- urgency: high/medium/low
- requires_action: true/false
- requires_human: true/false
- sentiment: positive/neutral/negative

Return your response as a JSON object with the following structure:
{{
    "category": "INTERVIEW|REJECTION|INFO_REQUEST|ASSESSMENT|FOLLOW_UP|OFFER|OTHER",
    "confidence": <0-100>,
    "urgency": "high|medium|low",
    "requires_action": true|false,
    "requires_human": true|false,
    "sentiment": "positive|neutral|negative",
    "key_points": ["point1", "point2"],
    "suggested_response": "Brief suggestion for how to respond"
}}
"""


ACTION_EXTRACTION_PROMPT = """
Extract action items from this recruiter email:

Email: {email_text}

What specific actions are requested? Examples:
- Schedule an interview (provide available times)
- Submit additional documents
- Complete an assessment
- Reply with salary expectations
- Provide references

Return as JSON:
{{
    "actions": ["action1", "action2"],
    "deadline": "date if mentioned",
    "contact_person": "name if mentioned",
    "next_steps": "summary"
}}
"""