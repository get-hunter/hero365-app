"""
Resend Email Service Adapter

Implementation of EmailServicePort interface using Resend.
"""

import os
import resend
from typing import Optional, List, Dict, Any
import re
import logging

from ...application.ports.email_service import (
    EmailServicePort, EmailMessage, EmailResult, EmailTemplate, 
    EmailAttachment, EmailPriority
)

logger = logging.getLogger(__name__)


class ResendEmailAdapter(EmailServicePort):
    """
    Resend implementation of EmailServicePort.
    
    This adapter handles email operations using Resend service.
    """
    
    def __init__(self, api_key: Optional[str] = None, 
                 default_from_email: Optional[str] = None,
                 default_from_name: Optional[str] = None):
        """
        Initialize the Resend adapter.
        
        Args:
            api_key: Resend API key (optional, can be set via environment)
            default_from_email: Default from email address (optional, can be set via environment)
            default_from_name: Default from name (optional, can be set via environment)
        """
        self.api_key = api_key or os.getenv("RESEND_API_KEY")
        if not self.api_key:
            raise ValueError("Resend API key is required. Set RESEND_API_KEY environment variable.")
        
        resend.api_key = self.api_key
        
        self.default_from_email = default_from_email or os.getenv("DEFAULT_FROM_EMAIL", "onboarding@hero365.app")
        self.default_from_name = default_from_name or os.getenv("DEFAULT_FROM_NAME", "Hero365")
    
    async def send_email(self, message: EmailMessage) -> EmailResult:
        """Send a single email message using Resend."""
        try:
            # Prepare email parameters
            params = self._prepare_email_params(message)
            
            # Send email using Resend
            response = resend.Emails.send(params)
            
            return EmailResult(
                success=True,
                message_id=response.get("id"),
                provider_response=response
            )
            
        except Exception as e:
            logger.error(f"Failed to send email via Resend: {str(e)}")
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
            # Process template variables
            subject = template.subject
            html_body = None
            text_body = None
            
            # Replace template variables with provided values
            all_variables = {**template.variables, **kwargs}
            
            for key, value in all_variables.items():
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
            logger.error(f"Failed to send template email via Resend: {str(e)}")
            return EmailResult(
                success=False,
                error_message=str(e)
            )
    
    async def send_welcome_email(self, to_email: str, user_name: str, 
                                activation_link: Optional[str] = None) -> EmailResult:
        """Send a welcome email to a new user."""
        subject = f"Welcome to Hero365, {user_name}!"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Welcome to Hero365</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 20px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0; font-size: 28px;">Welcome to Hero365!</h1>
            </div>
            
            <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px;">
                <h2 style="color: #333; margin-top: 0;">Hi {user_name},</h2>
                
                <p style="font-size: 16px; margin-bottom: 20px;">
                    Thank you for joining Hero365! We're excited to have you on board. 
                    Hero365 is your AI-native ERP solution designed specifically for home-services 
                    firms and independent contractors.
                </p>
                
                <p style="font-size: 16px; margin-bottom: 20px;">
                    With Hero365, you can automatically manage:
                </p>
                
                <ul style="font-size: 16px; margin-bottom: 20px; padding-left: 20px;">
                    <li>Contracts and agreements</li>
                    <li>Invoices and payments</li>
                    <li>Job scheduling and tracking</li>
                    <li>Client communications</li>
                    <li>Maintenance reminders</li>
                </ul>
                
                {f'''
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{activation_link}" style="background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">
                        Activate Your Account
                    </a>
                </div>
                ''' if activation_link else ''}
                
                <p style="font-size: 16px; margin-bottom: 20px;">
                    Get ready to streamline your business operations with the power of AI!
                </p>
                
                <p style="font-size: 16px;">
                    Best regards,<br>
                    <strong>The Hero365 Team</strong>
                </p>
            </div>
            
            <div style="text-align: center; padding: 20px; font-size: 12px; color: #666;">
                <p>© 2024 Hero365. All rights reserved.</p>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Welcome to Hero365!
        
        Hi {user_name},
        
        Thank you for joining Hero365! We're excited to have you on board. 
        Hero365 is your AI-native ERP solution designed specifically for home-services 
        firms and independent contractors.
        
        With Hero365, you can automatically manage:
        - Contracts and agreements
        - Invoices and payments
        - Job scheduling and tracking
        - Client communications
        - Maintenance reminders
        
        {f'Please visit this link to activate your account: {activation_link}' if activation_link else ''}
        
        Get ready to streamline your business operations with the power of AI!
        
        Best regards,
        The Hero365 Team
        """
        
        message = EmailMessage(
            to=[to_email],
            subject=subject,
            html_body=html_body,
            text_body=text_body,
            tags=["welcome", "onboarding"]
        )
        
        return await self.send_email(message)
    
    async def send_password_reset_email(self, to_email: str, user_name: str,
                                       reset_link: str, reset_token: str) -> EmailResult:
        """Send a password reset email."""
        subject = "Password Reset Request - Hero365"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Password Reset Request</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: #f8f9fa; padding: 30px; border-radius: 10px; border-left: 4px solid #dc3545;">
                <h2 style="color: #dc3545; margin-top: 0;">Password Reset Request</h2>
                
                <p style="font-size: 16px; margin-bottom: 20px;">Hi {user_name},</p>
                
                <p style="font-size: 16px; margin-bottom: 20px;">
                    You requested a password reset for your Hero365 account. 
                    Click the button below to reset your password:
                </p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_link}" style="background: #dc3545; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">
                        Reset Password
                    </a>
                </div>
                
                <p style="font-size: 14px; color: #666; margin-bottom: 20px;">
                    This link will expire in 24 hours for security reasons.
                </p>
                
                <p style="font-size: 14px; color: #666; margin-bottom: 20px;">
                    If you didn't request this reset, please ignore this email and your password will remain unchanged.
                </p>
                
                <p style="font-size: 16px;">
                    Best regards,<br>
                    <strong>The Hero365 Team</strong>
                </p>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Password Reset Request
        
        Hi {user_name},
        
        You requested a password reset for your Hero365 account.
        
        Please visit this link to reset your password: {reset_link}
        
        This link will expire in 24 hours for security reasons.
        
        If you didn't request this reset, please ignore this email and your password will remain unchanged.
        
        Best regards,
        The Hero365 Team
        """
        
        message = EmailMessage(
            to=[to_email],
            subject=subject,
            html_body=html_body,
            text_body=text_body,
            priority=EmailPriority.HIGH,
            tags=["password-reset", "security"]
        )
        
        return await self.send_email(message)
    
    async def send_verification_email(self, to_email: str, user_name: str,
                                     verification_link: str, verification_code: str) -> EmailResult:
        """Send an email verification message."""
        subject = "Verify Your Email - Hero365"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Email Verification</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: #f8f9fa; padding: 30px; border-radius: 10px; border-left: 4px solid #28a745;">
                <h2 style="color: #28a745; margin-top: 0;">Verify Your Email</h2>
                
                <p style="font-size: 16px; margin-bottom: 20px;">Hi {user_name},</p>
                
                <p style="font-size: 16px; margin-bottom: 20px;">
                    Please verify your email address to complete your Hero365 account setup.
                </p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verification_link}" style="background: #28a745; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">
                        Verify Email
                    </a>
                </div>
                
                <p style="font-size: 14px; color: #666; margin-bottom: 20px;">
                    Verification code: <strong>{verification_code}</strong>
                </p>
                
                <p style="font-size: 14px; color: #666; margin-bottom: 20px;">
                    This verification link will expire in 24 hours.
                </p>
                
                <p style="font-size: 16px;">
                    Best regards,<br>
                    <strong>The Hero365 Team</strong>
                </p>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Verify Your Email
        
        Hi {user_name},
        
        Please verify your email address to complete your Hero365 account setup.
        
        Verification link: {verification_link}
        Verification code: {verification_code}
        
        This verification link will expire in 24 hours.
        
        Best regards,
        The Hero365 Team
        """
        
        message = EmailMessage(
            to=[to_email],
            subject=subject,
            html_body=html_body,
            text_body=text_body,
            priority=EmailPriority.HIGH,
            tags=["verification", "onboarding"]
        )
        
        return await self.send_email(message)
    
    async def send_notification_email(self, to_email: str, user_name: str,
                                     subject: str, message: str,
                                     action_link: Optional[str] = None) -> EmailResult:
        """Send a general notification email."""
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{subject}</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: #f8f9fa; padding: 30px; border-radius: 10px; border-left: 4px solid #667eea;">
                <h2 style="color: #667eea; margin-top: 0;">{subject}</h2>
                
                <p style="font-size: 16px; margin-bottom: 20px;">Hi {user_name},</p>
                
                <p style="font-size: 16px; margin-bottom: 20px;">{message}</p>
                
                {f'''
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{action_link}" style="background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">
                        Take Action
                    </a>
                </div>
                ''' if action_link else ''}
                
                <p style="font-size: 16px;">
                    Best regards,<br>
                    <strong>The Hero365 Team</strong>
                </p>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        {subject}
        
        Hi {user_name},
        
        {message}
        
        {f'Action link: {action_link}' if action_link else ''}
        
        Best regards,
        The Hero365 Team
        """
        
        email_message = EmailMessage(
            to=[to_email],
            subject=subject,
            html_body=html_body,
            text_body=text_body,
            tags=["notification"]
        )
        
        return await self.send_email(email_message)
    
    async def validate_email_address(self, email: str) -> bool:
        """Validate an email address format."""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, email) is not None
    
    async def get_email_status(self, message_id: str) -> Dict[str, Any]:
        """Get the delivery status of a sent email."""
        try:
            # Resend doesn't have a direct API for getting email status
            # This would need to be implemented using webhooks or other methods
            return {
                "message_id": message_id,
                "status": "sent",
                "note": "Status tracking requires webhook implementation"
            }
        except Exception as e:
            logger.error(f"Failed to get email status: {str(e)}")
            return {
                "message_id": message_id,
                "status": "unknown",
                "error": str(e)
            }
    
    async def get_delivery_statistics(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get email delivery statistics."""
        try:
            # This would need to be implemented using Resend's analytics API
            # when it becomes available
            return {
                "start_date": start_date,
                "end_date": end_date,
                "total_sent": 0,
                "delivered": 0,
                "bounced": 0,
                "opened": 0,
                "clicked": 0,
                "note": "Statistics require analytics API implementation"
            }
        except Exception as e:
            logger.error(f"Failed to get delivery statistics: {str(e)}")
            return {
                "error": str(e)
            }
    
    def _prepare_email_params(self, message: EmailMessage) -> Dict[str, Any]:
        """Prepare email parameters for Resend API."""
        # Determine sender
        from_email = message.from_email or self.default_from_email
        if message.from_name:
            from_sender = f"{message.from_name} <{from_email}>"
        else:
            from_sender = f"{self.default_from_name} <{from_email}>"
        
        # Prepare basic parameters
        params = {
            "from": from_sender,
            "to": message.to,
            "subject": message.subject,
        }
        
        # Add email content
        if message.html_body:
            params["html"] = message.html_body
        if message.text_body:
            params["text"] = message.text_body
        
        # Add optional parameters
        if message.cc:
            params["cc"] = message.cc
        if message.bcc:
            params["bcc"] = message.bcc
        if message.reply_to:
            params["reply_to"] = message.reply_to
        
        # Add tags
        if message.tags:
            params["tags"] = message.tags
        
        # Add attachments (if supported by Resend in future)
        if message.attachments:
            logger.warning("Attachments are not yet supported by Resend")
        
        return params 