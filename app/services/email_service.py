import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class EmailService:
    """Service for sending emails"""
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html: bool = True
    ) -> bool:
        """Send an email"""
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
            message["To"] = to_email
            message["Subject"] = subject
            
            # Add body
            if html:
                message.attach(MIMEText(body, "html"))
            else:
                message.attach(MIMEText(body, "plain"))
            
            # Send email
            await aiosmtplib.send(
                message,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USER,
                password=settings.SMTP_PASSWORD,
                start_tls=True,
            )
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    async def send_otp_email(self, to_email: str, otp: str) -> bool:
        """Send OTP verification email"""
        subject = "Your Admin Login OTP"
        
        # Email template
        html_template = Template("""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: #4CAF50; color: white; padding: 20px; text-align: center; }
                .content { background: #f9f9f9; padding: 20px; border-radius: 5px; margin-top: 20px; }
                .otp { font-size: 32px; font-weight: bold; color: #4CAF50; text-align: center; padding: 20px; background: white; border-radius: 5px; letter-spacing: 5px; }
                .footer { text-align: center; margin-top: 20px; color: #777; font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{{ project_name }}</h1>
                </div>
                <div class="content">
                    <h2>Admin Login Verification</h2>
                    <p>Your one-time password (OTP) for admin login is:</p>
                    <div class="otp">{{ otp }}</div>
                    <p>This code will expire in {{ expire_minutes }} minutes.</p>
                    <p>If you did not request this code, please ignore this email.</p>
                </div>
                <div class="footer">
                    <p>This is an automated email. Please do not reply.</p>
                </div>
            </div>
        </body>
        </html>
        """)
        
        html_body = html_template.render(
            project_name=settings.PROJECT_NAME,
            otp=otp,
            expire_minutes=settings.OTP_EXPIRE_MINUTES
        )
        
        return await self.send_email(to_email, subject, html_body, html=True)
    
    async def send_notification_email(
        self,
        to_email: str,
        title: str,
        message: str
    ) -> bool:
        """Send a notification email"""
        subject = f"{settings.PROJECT_NAME} - {title}"
        
        html_template = Template("""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: #2196F3; color: white; padding: 20px; text-align: center; }
                .content { background: #f9f9f9; padding: 20px; border-radius: 5px; margin-top: 20px; }
                .footer { text-align: center; margin-top: 20px; color: #777; font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{{ project_name }}</h1>
                </div>
                <div class="content">
                    <h2>{{ title }}</h2>
                    <p>{{ message }}</p>
                </div>
                <div class="footer">
                    <p>This is an automated email. Please do not reply.</p>
                </div>
            </div>
        </body>
        </html>
        """)
        
        html_body = html_template.render(
            project_name=settings.PROJECT_NAME,
            title=title,
            message=message
        )
        
        return await self.send_email(to_email, subject, html_body, html=True)

email_service = EmailService()
