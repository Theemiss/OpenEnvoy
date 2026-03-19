"""Email templates for common scenarios."""

from typing import Dict, Any, Optional


class EmailTemplates:
    """Collection of email templates."""
    
    @staticmethod
    def application_email(name: str, job_title: str, company: str) -> Dict[str, str]:
        """Standard application email template."""
        return {
            "subject": f"Application for {job_title} - {name}",
            "body": f"""Dear Hiring Manager,

I am writing to express my strong interest in the {job_title} position at {company}. With my background in software development and passion for building scalable systems, I believe I would be a valuable addition to your team.

I have attached my resume for your review. I would welcome the opportunity to discuss how my experience aligns with your needs.

Thank you for your time and consideration.

Best regards,
{name}"""
        }
    
    @staticmethod
    def follow_up_email(name: str, job_title: str, company: str, 
                        days_since: int) -> Dict[str, str]:
        """Follow-up email template."""
        return {
            "subject": f"Follow-up on {job_title} application",
            "body": f"""Dear Hiring Manager,

I hope this email finds you well. I'm writing to follow up on my application for the {job_title} position at {company}, which I submitted {days_since} days ago.

I remain very interested in this opportunity and would welcome the chance to discuss how my skills could benefit your team.

Thank you for your consideration.

Best regards,
{name}"""
        }
    
    @staticmethod
    def interview_thank_you(name: str, job_title: str, company: str,
                            interviewer: Optional[str] = None) -> Dict[str, str]:
        """Post-interview thank you email."""
        recipient = interviewer or "the team"
        
        return {
            "subject": f"Thank you - {job_title} interview",
            "body": f"""Dear {recipient},

Thank you so much for taking the time to interview me for the {job_title} position today. I truly enjoyed learning more about {company} and the exciting work you're doing.

Our conversation reinforced my interest in this role, and I'm confident that my skills and experience would make me a valuable contributor to your team.

Please don't hesitate to reach out if you need any additional information from me. I look forward to hearing about the next steps.

Best regards,
{name}"""
        }
    
    @staticmethod
    def info_request_response(name: str, requested_info: str) -> Dict[str, str]:
        """Response to information request."""
        return {
            "subject": "Re: Additional Information",
            "body": f"""Dear Hiring Manager,

Thank you for getting back to me. Regarding your request for {requested_info}, I'm happy to provide the following:

[Insert requested information here]

Please let me know if you need anything else. I look forward to hearing from you.

Best regards,
{name}"""
        }
    
    @staticmethod
    def acceptance_email(name: str, job_title: str, company: str,
                         start_date: Optional[str] = None) -> Dict[str, str]:
        """Job offer acceptance email."""
        date_text = f"starting {start_date}" if start_date else "as discussed"
        
        return {
            "subject": f"Job Offer Acceptance - {job_title}",
            "body": f"""Dear Hiring Team,

I am delighted to accept the offer for the {job_title} position at {company}. Thank you for this wonderful opportunity.

I am excited to join the team and look forward to contributing to {company}'s success. I confirm that I can begin {date_text}.

Please let me know if there are any additional steps I need to take before my start date.

Best regards,
{name}"""
        }
    
    @staticmethod
    def withdrawal_email(name: str, job_title: str, company: str) -> Dict[str, str]:
        """Application withdrawal email."""
        return {
            "subject": f"Application Withdrawal - {job_title}",
            "body": f"""Dear Hiring Team,

Thank you for considering my application for the {job_title} position. After careful consideration, I have decided to withdraw my application at this time.

I appreciate the time and consideration you've given to my application and wish you the best in finding the right candidate for this role.

Best regards,
{name}"""
        }


# Template categories for easy access
TEMPLATES = {
    "application": EmailTemplates.application_email,
    "follow_up": EmailTemplates.follow_up_email,
    "thank_you": EmailTemplates.interview_thank_you,
    "info_response": EmailTemplates.info_request_response,
    "acceptance": EmailTemplates.acceptance_email,
    "withdrawal": EmailTemplates.withdrawal_email,
}


def get_template(template_name: str, **kwargs) -> Dict[str, str]:
    """Get a template by name."""
    if template_name not in TEMPLATES:
        raise ValueError(f"Unknown template: {template_name}")
    
    return TEMPLATES[template_name](**kwargs)