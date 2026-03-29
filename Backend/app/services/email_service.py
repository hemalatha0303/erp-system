"""Email service for sending emails via SMTP"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from app.core.config import SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, SENDER_EMAIL


def send_password_reset_email(recipient_email: str, reset_link: str, user_name: str = "User"):
    """
    Send password reset email to user.
    
    Args:
        recipient_email: Email address to send to
        reset_link: Password reset link
        user_name: User's name for personalization
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = "🔐 Password Reset Request - SIH25103 ERP System"
        message["From"] = SENDER_EMAIL
        message["To"] = recipient_email

        # HTML body with professional styling
        html = f"""\
        <html>
          <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; background: #f5f5f5; margin: 0; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); overflow: hidden;">
              <!-- Header -->
              <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px 20px; text-align: center;">
                <h1 style="margin: 0; font-size: 28px; font-weight: 600;">🔐 Password Reset</h1>
              </div>

              <!-- Content -->
              <div style="padding: 40px 30px;">
                <p style="font-size: 16px; margin: 0 0 20px 0;">Hi {user_name},</p>
                
                <p style="font-size: 14px; color: #555; margin: 0 0 20px 0;">
                  We received a request to reset the password for your SIH25103 ERP System account. If you didn't make this request, you can safely ignore this email.
                </p>

                <p style="font-size: 14px; color: #555; margin: 0 0 30px 0;">
                  Click the button below to create a new password:
                </p>

                <!-- CTA Button -->
                <div style="text-align: center; margin: 30px 0;">
                  <a href="{reset_link}" style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 14px 40px; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px; transition: transform 0.2s; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);">
                    Reset Password
                  </a>
                </div>

                <!-- Or copy link -->
                <p style="font-size: 12px; color: #999; text-align: center; margin: 30px 0;">Or copy this link:</p>
                <div style="background: #f8f9fa; border-left: 4px solid #667eea; padding: 12px 15px; border-radius: 5px; word-break: break-all; font-size: 12px; color: #666; font-family: monospace;">
                  {reset_link}
                </div>

                <!-- Important Info -->
                <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin-top: 30px; border-radius: 5px;">
                  <p style="margin: 0; font-size: 13px; color: #856404;">
                    <strong>⏰ Important:</strong> This link will expire in <strong>24 hours</strong> for security reasons.
                  </p>
                </div>

                <!-- Security Notice -->
                <p style="font-size: 12px; color: #999; margin-top: 25px; line-height: 1.8;">
                  <strong>Security Notice:</strong> Never share your password reset link with anyone. 
                  Our team will never ask for your password or reset link via email or phone.
                </p>
              </div>

              <!-- Footer -->
              <div style="background: #f8f9fa; padding: 20px; text-align: center; border-top: 1px solid #e0e0e0;">
                <p style="margin: 0; font-size: 12px; color: #999;">
                  SIH25103 ERP System - Integrated Student Management System<br>
                  © 2026 All rights reserved
                </p>
                <p style="margin: 10px 0 0 0; font-size: 11px; color: #ccc;">
                  If you have questions, contact support
                </p>
              </div>
            </div>
          </body>
        </html>
        """
        
        # Attach HTML version
        part = MIMEText(html, "html")
        message.attach(part)

        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipient_email, message.as_string())
        
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False


def send_test_email(recipient_email: str):
    """
    Send a test email to verify SMTP configuration.
    
    Args:
        recipient_email: Email address to send test email to
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        message = MIMEMultipart("alternative")
        message["Subject"] = "Test Email - SIH25103 ERP System"
        message["From"] = SENDER_EMAIL
        message["To"] = recipient_email

        html = """\
        <html>
          <body>
            <p>This is a test email from SIH25103 ERP System.</p>
            <p>If you received this, the email service is working correctly.</p>
          </body>
        </html>
        """
        
        part = MIMEText(html, "html")
        message.attach(part)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipient_email, message.as_string())
        
        return True
    except Exception as e:
        print(f"Error sending test email: {str(e)}")
        return False
