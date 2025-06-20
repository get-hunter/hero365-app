"""
Twilio SMS Service Adapter

Implementation of SMSServicePort interface using Twilio API.
"""

import os
from typing import Optional, Dict, Any
try:
    from twilio.rest import Client
    from twilio.base.exceptions import TwilioException
except ImportError:
    # Fallback for when Twilio is not installed
    Client = None
    TwilioException = Exception

from ...application.ports.sms_service import (
    SMSServicePort, SMSMessage, SMSResult
)


class TwilioSMSAdapter(SMSServicePort):
    """
    Twilio implementation of SMSServicePort.
    
    This adapter handles SMS operations using Twilio API.
    """
    
    def __init__(self, account_sid: Optional[str] = None, auth_token: Optional[str] = None,
                 phone_number: Optional[str] = None):
        if Client is None:
            raise ImportError("Twilio package is required. Install with: pip install twilio")
        
        self.account_sid = account_sid or os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = auth_token or os.getenv("TWILIO_AUTH_TOKEN")
        self.phone_number = phone_number or os.getenv("TWILIO_PHONE_NUMBER")
        
        if not self.account_sid or not self.auth_token:
            raise ValueError("Twilio Account SID and Auth Token must be provided")
        
        if not self.phone_number:
            raise ValueError("Twilio phone number must be provided")
        
        self.client = Client(self.account_sid, self.auth_token)
    
    async def send_sms(self, message: SMSMessage) -> SMSResult:
        """Send a single SMS message."""
        try:
            response = self.client.messages.create(
                body=message.body,
                from_=message.from_number or self.phone_number,
                to=message.to_number
            )
            
            return SMSResult(
                success=True,
                message_id=response.sid,
                status=response.status,
                provider_response=response
            )
            
        except TwilioException as e:
            return SMSResult(
                success=False,
                error_message=str(e),
                error_code=getattr(e, 'code', None)
            )
        except Exception as e:
            return SMSResult(
                success=False,
                error_message=str(e)
            )
    
    async def send_verification_code(self, phone_number: str, code: str) -> SMSResult:
        """Send a verification code via SMS."""
        message = SMSMessage(
            to_number=phone_number,
            body=f"Your verification code is: {code}. This code will expire in 10 minutes."
        )
        
        return await self.send_sms(message)
    
    async def send_two_factor_code(self, phone_number: str, code: str) -> SMSResult:
        """Send a two-factor authentication code via SMS."""
        message = SMSMessage(
            to_number=phone_number,
            body=f"Your 2FA code is: {code}. Do not share this code with anyone."
        )
        
        return await self.send_sms(message)
    
    async def send_password_reset_code(self, phone_number: str, code: str) -> SMSResult:
        """Send a password reset code via SMS."""
        message = SMSMessage(
            to_number=phone_number,
            body=f"Your password reset code is: {code}. This code will expire in 15 minutes."
        )
        
        return await self.send_sms(message)
    
    async def send_notification(self, phone_number: str, message: str) -> SMSResult:
        """Send a general notification via SMS."""
        sms_message = SMSMessage(
            to_number=phone_number,
            body=message
        )
        
        return await self.send_sms(sms_message)
    
    async def validate_phone_number(self, phone_number: str) -> bool:
        """Validate a phone number format."""
        try:
            # Use Twilio's phone number lookup
            phone_number_info = self.client.lookups.phone_numbers(phone_number).fetch()
            return phone_number_info.phone_number is not None
        except TwilioException:
            return False
        except Exception:
            return False
    
    async def get_sms_status(self, message_id: str) -> Dict[str, Any]:
        """Get the delivery status of a sent SMS."""
        try:
            message = self.client.messages(message_id).fetch()
            
            return {
                "message_id": message.sid,
                "status": message.status,
                "error_code": message.error_code,
                "error_message": message.error_message,
                "direction": message.direction,
                "price": message.price,
                "price_unit": message.price_unit,
                "date_sent": str(message.date_sent) if message.date_sent else None,
                "date_updated": str(message.date_updated) if message.date_updated else None,
                "provider": "twilio"
            }
            
        except TwilioException as e:
            return {
                "message_id": message_id,
                "status": "error",
                "error": str(e),
                "provider": "twilio"
            }
        except Exception as e:
            return {
                "message_id": message_id,
                "status": "error",
                "error": str(e),
                "provider": "twilio"
            }
    
    async def get_delivery_statistics(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get SMS delivery statistics for a date range."""
        try:
            # Fetch messages in date range
            messages = self.client.messages.list(
                date_sent_after=start_date,
                date_sent_before=end_date
            )
            
            total_sent = len(messages)
            delivered = sum(1 for msg in messages if msg.status == 'delivered')
            failed = sum(1 for msg in messages if msg.status in ['failed', 'undelivered'])
            pending = sum(1 for msg in messages if msg.status in ['queued', 'sending', 'sent'])
            
            return {
                "start_date": start_date,
                "end_date": end_date,
                "total_sent": total_sent,
                "delivered": delivered,
                "failed": failed,
                "pending": pending,
                "provider": "twilio"
            }
            
        except TwilioException as e:
            return {
                "start_date": start_date,
                "end_date": end_date,
                "error": str(e),
                "provider": "twilio"
            }
        except Exception as e:
            return {
                "start_date": start_date,
                "end_date": end_date,
                "error": str(e),
                "provider": "twilio"
            }
    
    async def get_account_balance(self) -> Dict[str, Any]:
        """Get Twilio account balance."""
        try:
            balance = self.client.balance.fetch()
            
            return {
                "currency": balance.currency,
                "balance": balance.balance,
                "provider": "twilio"
            }
            
        except TwilioException as e:
            return {
                "error": str(e),
                "provider": "twilio"
            }
        except Exception as e:
            return {
                "error": str(e),
                "provider": "twilio"
            } 