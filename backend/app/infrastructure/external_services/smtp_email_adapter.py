"""
SMTP Email Service Adapter

Implementation of EmailServicePort interface using SMTP.
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional, List, Dict, Any

from ...application.ports.email_service import (
    EmailServicePort, EmailMessage, EmailResult, EmailTemplate, 
    EmailAttachment, EmailPriority
)


class SMTPEmailAdapter(EmailServicePort):
    """
    SMTP implementation of EmailServicePort.
    
    This adapter handles email operations using SMTP server.
    """
    
    def __init__(self, smtp_host: Optional[str] = None, smtp_port: Optional[int] = None,
                 smtp_username: Optional[str] = None, smtp_password: Optional[str] = None,
                 use_tls: bool = True):
        self.smtp_host = smtp_host or os.getenv("SMTP_HOST", "localhost")
        self.smtp_port = smtp_port or int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = smtp_username or os.getenv("SMTP_USERNAME")
        self.smtp_password = smtp_password or os.getenv("SMTP_PASSWORD")
        self.use_tls = use_tls
        self.default_from_email = os.getenv("DEFAULT_FROM_EMAIL", "noreply@example.com")
        self.default_from_name = os.getenv("DEFAULT_FROM_NAME", "Hero365 App")
    
    async def send_email(self, message: EmailMessage) -> EmailResult:
        """Send a single email message."""
        try:
            # Create MIME message
            mime_message = self._create_mime_message(message)
            
            # Connect to SMTP server and send
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                
                if self.smtp_username and self.smtp_password:
                    server.login(self.smtp_username, self.smtp_password)
                
                # Send email
                text = mime_message.as_string()
                from_email = message.from_email or self.default_from_email
                server.sendmail(from_email, message.to, text)
                
                return EmailResult(
                    success=True,
                    message_id=f"smtp_{hash(text)}",  # Simple message ID
                )
                
        except Exception as e:
            return EmailResult(
                success=False,
                error_message=str(e)
            )
    
    async def send_bulk_emails(self, messages: List[EmailMessage]) -> List[EmailResult]:
        """Send multiple email messages."""
        results = []
        for message in messages:
            result = await self.send_email(message)
            results.append(result)
        return results
    
    async def send_template_email(self, template: EmailTemplate, 
                                 to: List[str], **kwargs) -> EmailResult:
        """Send an email using a predefined template."""
        try:
            # Simple template processing (replace variables)
            subject = template.subject
            html_body = None
            text_body = None
            
            # Replace template variables
            for key, value in template.variables.items():
                subject = subject.replace(f"{{{key}}}", str(value))
                if html_body:
                    html_body = html_body.replace(f"{{{key}}}", str(value))
                if text_body:
                    text_body = text_body.replace(f"{{{key}}}", str(value))
            
            # Override with kwargs
            for key, value in kwargs.items():
                subject = subject.replace(f"{{{key}}}", str(value))
                if html_body:
                    html_body = html_body.replace(f"{{{key}}}", str(value))
                if text_body:
                    text_body = text_body.replace(f"{{{key}}}", str(value))
            
            message = EmailMessage(
                to=to,
                subject=subject,
                html_body=html_body,
                text_body=text_body,
                template=template
            )
            
            return await self.send_email(message)
            
        except Exception as e:
            return EmailResult(
                success=False,
                error_message=str(e)
            )
    
    async def send_welcome_email(self, to_email: str, user_name: str, 
                                activation_link: Optional[str] = None) -> EmailResult:
        """Send a welcome email to a new user."""
        subject = f"Welcome to {self.default_from_name}, {user_name}!"
        
        html_body = f"""
        <html>
        <body>
            <h2>Welcome to {self.default_from_name}!</h2>
            <p>Hi {user_name},</p>
            <p>Thank you for joining {self.default_from_name}. We're excited to have you on board!</p>
            {f'<p><a href="{activation_link}">Click here to activate your account</a></p>' if activation_link else ''}
            <p>Best regards,<br>The {self.default_from_name} Team</p>
        </body>
        </html>
        """
        
        text_body = f"""
        Welcome to {self.default_from_name}!
        
        Hi {user_name},
        
        Thank you for joining {self.default_from_name}. We're excited to have you on board!
        
        {f'Please visit this link to activate your account: {activation_link}' if activation_link else ''}
        
        Best regards,
        The {self.default_from_name} Team
        """
        
        message = EmailMessage(
            to=[to_email],
            subject=subject,
            html_body=html_body,
            text_body=text_body
        )
        
        return await self.send_email(message)
    
    async def send_password_reset_email(self, to_email: str, user_name: str,
                                       reset_link: str, reset_token: str) -> EmailResult:
        """Send a password reset email."""
        subject = "Password Reset Request"
        
        html_body = f"""
        <html>
        <body>
            <h2>Password Reset Request</h2>
            <p>Hi {user_name},</p>
            <p>You requested a password reset for your {self.default_from_name} account.</p>
            <p><a href="{reset_link}">Click here to reset your password</a></p>
            <p>This link will expire in 24 hours for security reasons.</p>
            <p>If you didn't request this reset, please ignore this email.</p>
            <p>Best regards,<br>The {self.default_from_name} Team</p>
        </body>
        </html>
        """
        
        text_body = f"""
        Password Reset Request
        
        Hi {user_name},
        
        You requested a password reset for your {self.default_from_name} account.
        
        Please visit this link to reset your password: {reset_link}
        
        This link will expire in 24 hours for security reasons.
        
        If you didn't request this reset, please ignore this email.
        
        Best regards,
        The {self.default_from_name} Team
        """
        
        message = EmailMessage(
            to=[to_email],
            subject=subject,
            html_body=html_body,
            text_body=text_body,
            priority=EmailPriority.HIGH
        )
        
        return await self.send_email(message)
    
    async def send_verification_email(self, to_email: str, user_name: str,
                                     verification_link: str, verification_code: str) -> EmailResult:
        """Send an email verification message."""
        subject = "Please verify your email address"
        
        html_body = f"""
        <html>
        <body>
            <h2>Email Verification</h2>
            <p>Hi {user_name},</p>
            <p>Please verify your email address for your {self.default_from_name} account.</p>
            <p><a href="{verification_link}">Click here to verify your email</a></p>
            <p>Or use this verification code: <strong>{verification_code}</strong></p>
            <p>Best regards,<br>The {self.default_from_name} Team</p>
        </body>
        </html>
        """
        
        text_body = f"""
        Email Verification
        
        Hi {user_name},
        
        Please verify your email address for your {self.default_from_name} account.
        
        Visit this link: {verification_link}
        
        Or use this verification code: {verification_code}
        
        Best regards,
        The {self.default_from_name} Team
        """
        
        message = EmailMessage(
            to=[to_email],
            subject=subject,
            html_body=html_body,
            text_body=text_body,
            priority=EmailPriority.HIGH
        )
        
        return await self.send_email(message)
    
    async def send_notification_email(self, to_email: str, user_name: str,
                                     subject: str, message: str,
                                     action_link: Optional[str] = None) -> EmailResult:
        """Send a general notification email."""
        html_body = f"""
        <html>
        <body>
            <h2>{subject}</h2>
            <p>Hi {user_name},</p>
            <p>{message}</p>
            {f'<p><a href="{action_link}">Take Action</a></p>' if action_link else ''}
            <p>Best regards,<br>The {self.default_from_name} Team</p>
        </body>
        </html>
        """
        
        text_body = f"""
        {subject}
        
        Hi {user_name},
        
        {message}
        
        {f'Visit: {action_link}' if action_link else ''}
        
        Best regards,
        The {self.default_from_name} Team
        """
        
        email_message = EmailMessage(
            to=[to_email],
            subject=subject,
            html_body=html_body,
            text_body=text_body
        )
        
        return await self.send_email(email_message)
    
    async def validate_email_address(self, email: str) -> bool:
        """Validate an email address format."""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    async def get_email_status(self, message_id: str) -> Dict[str, Any]:
        """Get the delivery status of a sent email."""
        # SMTP doesn't provide delivery status tracking
        return {
            "message_id": message_id,
            "status": "sent",
            "provider": "smtp"
        }
    
    async def get_delivery_statistics(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get email delivery statistics for a date range."""
        # SMTP doesn't provide delivery statistics
        return {
            "start_date": start_date,
            "end_date": end_date,
            "total_sent": 0,
            "total_delivered": 0,
            "total_bounced": 0,
            "provider": "smtp"
        }
    
    def _create_mime_message(self, message: EmailMessage) -> MIMEMultipart:
        """Create MIME message from EmailMessage."""
        mime_message = MIMEMultipart('alternative')
        
        # Set headers
        mime_message['Subject'] = message.subject
        mime_message['From'] = f"{message.from_name or self.default_from_name} <{message.from_email or self.default_from_email}>"
        mime_message['To'] = ', '.join(message.to)
        
        if message.cc:
            mime_message['Cc'] = ', '.join(message.cc)
        
        if message.reply_to:
            mime_message['Reply-To'] = message.reply_to
        
        # Add text body
        if message.text_body:
            text_part = MIMEText(message.text_body, 'plain')
            mime_message.attach(text_part)
        
        # Add HTML body
        if message.html_body:
            html_part = MIMEText(message.html_body, 'html')
            mime_message.attach(html_part)
        
        # Add attachments
        if message.attachments:
            for attachment in message.attachments:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.content)
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {attachment.filename}'
                )
                mime_message.attach(part)
        
        return mime_message 