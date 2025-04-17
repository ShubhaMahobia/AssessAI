class ConsentPrompts:
    """GDPR consent prompts for interview data storage."""
    
    def __init__(self, company_name: str):
        """Initialize consent prompts.
        
        Args:
            company_name: Name of the company conducting interviews
        """
        self.company_name = company_name
        
        # Initial consent request prompt
        self.CONSENT_REQUEST = f"""This data will include:
- Your name, email, and phone number
- Your professional experience and skills
- Your answers to technical questions

We follow GDPR guidelines, meaning:
1. Your data will be stored securely
2. It will be retained for a maximum of 12 months
3. You can request access, correction, or deletion of your data at any time
4. We will not share your data with third parties without your consent

Do you consent to {company_name} storing this information? Please reply with 'yes' or 'no'.
"""

        # Consent confirmation
        self.CONSENT_GIVEN = f"""Thank you for your consent. Your information will be stored securely in accordance with our privacy policy.

You may revoke this consent at any time by contacting our data protection team at privacy@{company_name.lower()}.com.

Let me now explain the interview process:
- This interview will take approximately 15-20 minutes
- First, I'll collect some basic information about you
- Then, I'll ask some theoretical technical questions (no coding required)
- Feel free to ask clarifying questions at any point

Now, let's begin. Could you please tell me your full name?
"""

        # Consent declined
        self.CONSENT_DECLINED = f"""I understand your decision. {company_name} will not store your personal data beyond this interview session.

Let me now explain the interview process:
- This interview will take approximately 15-20 minutes
- First, I'll collect some basic information about you
- Then, I'll ask some theoretical technical questions (no coding required)
- Feel free to ask clarifying questions at any point
- Since you declined data storage, your responses will not be saved after our conversation ends

Now, let's begin. Could you please tell me your full name?
"""

        # Data rights information
        self.DATA_RIGHTS_INFO = f"""As per GDPR, you have the following rights regarding your data:

1. Right to access: You can request a copy of your personal data
2. Right to rectification: You can correct inaccurate information
3. Right to erasure: You can request deletion of your data
4. Right to restrict processing: You can limit how we use your data
5. Right to data portability: You can request transfer of your data
6. Right to object: You can object to processing of your data

To exercise these rights, please contact privacy@{company_name.lower()}.com.
"""

        # End of interview data usage
        self.END_OF_INTERVIEW_DATA_NOTICE = f"""This concludes our interview. As you've consented, {company_name} will store your interview responses for evaluation.

Your data will be processed in accordance with our privacy policy and GDPR regulations.

If you have any questions about how your data is handled, please contact our data protection team.
""" 