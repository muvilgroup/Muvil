import resend
from django.conf import settings

resend.api_key = settings.RESEND_API_KEY

def send_email(from_email,to_email, subject, html_content):
    try:
        response = resend.Emails.send({
            "from": from_email,  # replace with your verified domain
            "to": [to_email],
            "subject": subject,
            "html": html_content,
        })
        return response
    except Exception as e:
        print("Email failed:", e)
        return None