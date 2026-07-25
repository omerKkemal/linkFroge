# File: utility/email_temp.py
# -*- coding: utf-8 -*-
"""
LinkFroge - Email Templates
Professional email templates for link management system
White & Gold Theme Edition - Email Client Compatible
"""
from string import Template
import smtplib
from email.message import EmailMessage
from datetime import datetime
import re
import logging
import traceback



from database.manage_db import config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailTemplate:
    """Email template generator for LinkFroge notifications.
    Generates HTML email templates with a white and gold theme,
    optimized for compatibility across various email clients.
    """
    def __init__(self, baseUrl, dashboard='/dashboard', login='/login'):
        # Use Template to avoid { } conflicts in CSS
        self.HTML_TEMP = Template(self._build_template())
        # Store endpoints
        self.dashboard = f'{baseUrl}{dashboard}'
        self.login = f'{baseUrl}{login}'

    def _build_template(self):
        return '''
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>LinkFroge Notification</title>
                <style type="text/css">
                    /* Reset for email clients */
                    .ExternalClass { width: 100%; }
                    .ExternalClass, .ExternalClass p, .ExternalClass span, .ExternalClass font, .ExternalClass td, .ExternalClass div { line-height: 100%; }
                    body { margin: 0; padding: 0; -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }
                    table { border-collapse: collapse; mso-table-lspace: 0pt; mso-table-rspace: 0pt; }
                    img { border: 0; height: auto; line-height: 100%; outline: none; text-decoration: none; -ms-interpolation-mode: bicubic; }
                    p { display: block; margin: 13px 0; }
                </style>
                <!--[if mso]>
                <style type="text/css">
                    .body-table { width: 600px !important; }
                </style>
                <![endif]-->
            </head>
            <body style="margin: 0; padding: 0; background-color: #f8f9fa; font-family: Arial, sans-serif;">
                <!--[if mso]>
                <center>
                <table align="center" border="0" cellpadding="0" cellspacing="0" width="600" class="body-table">
                <tr>
                <td>
                <![endif]-->
                
                <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; background-color: #ffffff; border: 2px solid #d4af37; border-radius: 0; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                    <!-- Gold Header -->
                    <tr>
                        <td align="center" bgcolor="#d4af37" style="padding: 30px; background: linear-gradient(135deg, #d4af37 0%, #f7ef8a 100%);">
                            <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                <tr>
                                    <td align="center" style="color: #1a1a1a; font-family: Arial, sans-serif; font-size: 28px; font-weight: bold; text-shadow: 1px 1px 2px rgba(0,0,0,0.1);">
                                        LINKFROGE
                                    </td>
                                </tr>
                                <tr>
                                    <td align="center" style="color: #1a1a1a; font-family: Arial, sans-serif; font-size: 14px; font-weight: 600; padding-top: 8px; opacity: 0.9;">
                                        PERMANENT LINK MANAGEMENT SYSTEM
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- White Content Area -->
                    <tr>
                        <td style="padding: 40px 30px;" bgcolor="#ffffff">
                            $content
                        </td>
                    </tr>
                    
                    <!-- Gold Footer -->
                    <tr>
                        <td align="center" bgcolor="#f8f9fa" style="padding: 25px; border-top: 2px solid #d4af37;">
                            <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                <tr>
                                    <td align="center" style="color: #666666; font-family: Arial, sans-serif; font-size: 13px; line-height: 1.5;">
                                        &copy; 2024 LinkFroge Link Management System. All rights reserved.<br>
                                        This is an automated message. Please do not reply to this email.
                                    </td>
                                </tr>
                                <tr>
                                    <td align="center" style="padding-top: 15px;">
                                        <span style="display: inline-block; background-color: rgba(212, 175, 55, 0.1); border: 1px solid #d4af37; border-radius: 20px; padding: 8px 20px; color: #8b6e1f; font-family: Arial, sans-serif; font-size: 12px; font-weight: 600;">
                                            Premium Link Management
                                        </span>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
                
                <!--[if mso]>
                </td>
                </tr>
                </table>
                </center>
                <![endif]-->
            </body>
            </html>
        '''

    def _inline_styles(self, content):
        """Convert CSS classes to inline styles for email compatibility"""
        styles_map = {
            'class="status-indicator"': 'style="display: inline-block; background-color: rgba(212, 175, 55, 0.1); border: 2px solid #d4af37; border-radius: 25px; padding: 10px 20px; color: #8b6e1f; font-family: Arial, sans-serif; font-size: 14px; font-weight: bold; margin: 15px 0; text-transform: uppercase; letter-spacing: 0.5px;"',
            'class="message-box"': 'style="background-color: #fefefe; border-left: 4px solid #d4af37; border: 2px solid #f0f0f0; padding: 25px; margin: 25px 0; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);"',
            'class="btn-container"': 'style="text-align: center; margin: 30px 0 20px;"',
            'class="btn"': 'style="display: inline-block; background: linear-gradient(135deg, #d4af37 0%, #f7ef8a 100%); color: #1a1a1a; text-decoration: none; padding: 16px 36px; font-family: Arial, sans-serif; font-size: 16px; font-weight: bold; border-radius: 6px; margin: 10px 0; border: none; box-shadow: 0 4px 12px rgba(212, 175, 55, 0.3);"',
            'class="info-grid"': 'style="margin: 25px 0;"',
            'class="info-item"': 'style="background-color: #f8f9fa; border: 2px solid #e9ecef; border-left: 4px solid #d4af37; padding: 20px; margin-bottom: 15px; border-radius: 6px;"',
            'class="info-label"': 'style="color: #8b6e1f; font-family: Arial, sans-serif; font-size: 12px; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;"',
            'class="info-value"': 'style="color: #2d2d2d; font-family: Arial, sans-serif; font-size: 16px; font-weight: bold;"',
            'class="warning"': 'style="background-color: rgba(212, 175, 55, 0.08); border-left: 4px solid #d4af37; padding: 16px 20px; margin: 20px 0; color: #8b6e1f; font-family: Arial, sans-serif; font-size: 14px; border-radius: 6px; border: 1px solid rgba(212, 175, 55, 0.2);"',
            'class="link-box"': 'style="background-color: #f8f9fa; border: 2px solid #d4af37; border-radius: 8px; padding: 20px; margin: 20px 0; text-align: center;"',
            'class="link-url"': 'style="color: #d4af37; font-family: Courier New, monospace; font-size: 18px; font-weight: bold; word-break: break-all;"',
        }
        
        for class_name, inline_style in styles_map.items():
            content = content.replace(class_name, inline_style)
        
        return content

    # ===== Validation Methods =====
    def validate_email(self, email):
        """Basic email validation"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def sanitize_input(self, text):
        """Basic input sanitization for email content"""
        if not text:
            return ""
        # Remove potentially dangerous characters
        sanitized = str(text).replace('<script>', '').replace('</script>', '')
        return sanitized[:1000]  # Limit length

    def check_smtp_config(self):
        """Check if SMTP configuration is valid"""
        try:
            with smtplib.SMTP(config.SMTP_LINK, config.SMTP_PORT) as smtp:
                smtp.starttls()
                smtp.login(config.EMAIL, config.EMAIL_PASSWORD)
                logger.info("SMTP configuration is valid")
                return True
        except Exception as e:
            logger.error(f"SMTP configuration error: {e}")
            return False

    # ===== Email templates =====

    def welcome_email(self, username, email):
        """Welcome email for new user registration"""
        safe_username = self.sanitize_input(username)
        safe_email = self.sanitize_input(email)
        safe_link = self.sanitize_input(self.dashboard)
        
        content = f'''
            <h1 style="color: #d4af37; font-family: Arial, sans-serif; font-size: 28px; font-weight: bold; margin-bottom: 20px; text-align: center;">Welcome to LinkFroge</h1>
            
            <div class="status-indicator">REGISTRATION SUCCESSFUL</div>
            
            <p style="color: #4a4a4a; font-family: Arial, sans-serif; font-size: 16px; margin-bottom: 20px; line-height: 1.6;">Dear {safe_username},</p>
            <p style="color: #4a4a4a; font-family: Arial, sans-serif; font-size: 16px; margin-bottom: 20px; line-height: 1.6;">Welcome to LinkFroge! Your account has been successfully created and is now active.</p>
            
            <div class="message-box">
                <p style="color: #4a4a4a; font-family: Arial, sans-serif; margin-bottom: 12px; font-size: 15px;"><strong style="color: #d4af37;">Account Email:</strong> {safe_email}</p>
                <p style="color: #4a4a4a; font-family: Arial, sans-serif; margin-bottom: 12px; font-size: 15px;"><strong style="color: #d4af37;">Registration Time:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                <p style="color: #4a4a4a; font-family: Arial, sans-serif; margin-bottom: 0; font-size: 15px;"><strong style="color: #d4af37;">Account Status:</strong> <span style="color: #d4af37; font-weight: bold;">ACTIVE</span></p>
            </div>
            
            <p style="color: #4a4a4a; font-family: Arial, sans-serif; font-size: 16px; margin-bottom: 20px; line-height: 1.6;">You can now create and manage your permanent links. Click the button below to access your dashboard.</p>
            
            <div class="btn-container">
                <a href="{safe_link}" class="btn">Access Dashboard</a>
            </div>
            
            <div class="warning">
                Please do not reply to this automated email. For assistance, contact support.
            </div>
        '''
        content = self._inline_styles(content)
        return self.HTML_TEMP.substitute(content=content)

    def link_created(self, username, link_title, link_url, link_slug):
        """Email notification when a new link is created"""
        safe_username = self.sanitize_input(username)
        safe_title = self.sanitize_input(link_title)
        safe_url = self.sanitize_input(link_url)
        safe_slug = self.sanitize_input(link_slug)
        safe_dashboard = self.sanitize_input(self.dashboard)
        
        content = f'''
            <h1 style="color: #d4af37; font-family: Arial, sans-serif; font-size: 28px; font-weight: bold; margin-bottom: 20px; text-align: center;">New Link Created</h1>
            
            <div class="status-indicator">LINK GENERATED</div>
            
            <p style="color: #4a4a4a; font-family: Arial, sans-serif; font-size: 16px; margin-bottom: 20px; line-height: 1.6;">Dear {safe_username},</p>
            <p style="color: #4a4a4a; font-family: Arial, sans-serif; font-size: 16px; margin-bottom: 20px; line-height: 1.6;">A new permanent link has been created successfully.</p>
            
            <div class="message-box">
                <p style="color: #4a4a4a; font-family: Arial, sans-serif; margin-bottom: 12px; font-size: 15px;"><strong style="color: #d4af37;">Link Title:</strong> {safe_title}</p>
                <p style="color: #4a4a4a; font-family: Arial, sans-serif; margin-bottom: 12px; font-size: 15px;"><strong style="color: #d4af37;">Original URL:</strong> {safe_url}</p>
                <p style="color: #4a4a4a; font-family: Arial, sans-serif; margin-bottom: 12px; font-size: 15px;"><strong style="color: #d4af37;">Link Slug:</strong> {safe_slug}</p>
                <p style="color: #4a4a4a; font-family: Arial, sans-serif; margin-bottom: 0; font-size: 15px;"><strong style="color: #d4af37;">Created At:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            </div>
            
            <div class="link-box">
                <p style="color: #4a4a4a; font-family: Arial, sans-serif; margin-bottom: 8px; font-size: 14px;">Your permanent link:</p>
                <div class="link-url">{safe_slug}</div>
            </div>
            
            <div class="btn-container">
                <a href="{safe_dashboard}" class="btn">View All Links</a>
            </div>
            
            <div class="warning">
                This link will remain active until you delete it or it expires.
            </div>
        '''
        content = self._inline_styles(content)
        return self.HTML_TEMP.substitute(content=content)

    def reset_password(self, username, code, email):
        """Password reset email template"""
        safe_username = self.sanitize_input(username)
        safe_email = self.sanitize_input(email)
        safe_code = self.sanitize_input(code)
        
        content = f'''
            <h1 style="color: #d4af37; font-family: Arial, sans-serif; font-size: 28px; font-weight: bold; margin-bottom: 20px; text-align: center;">Password Reset Request</h1>
            
            <div class="status-indicator">SECURITY VERIFICATION REQUIRED</div>
            
            <p style="color: #4a4a4a; font-family: Arial, sans-serif; font-size: 16px; margin-bottom: 20px; line-height: 1.6;">Dear {safe_username},</p>
            <p style="color: #4a4a4a; font-family: Arial, sans-serif; font-size: 16px; margin-bottom: 20px; line-height: 1.6;">We received a password reset request for your account: <strong style="color: #d4af37;">{safe_email}</strong></p>
            
            <div class="message-box">
                <p style="color: #4a4a4a; font-family: Arial, sans-serif; margin-bottom: 20px; font-size: 15px; text-align: center;">Use the verification code below to reset your password:</p>
                <p style="color: #d4af37; font-family: Arial, sans-serif; font-size: 32px; font-weight: bold; text-align: center; margin: 25px 0; letter-spacing: 4px; background: #f8f9fa; padding: 20px; border-radius: 8px; border: 2px dashed #d4af37;">{safe_code}</p>
                <p style="color: #8b6e1f; font-family: Arial, sans-serif; text-align: center; margin-bottom: 0; font-size: 14px; font-weight: bold;">SECURITY VERIFICATION CODE</p>
            </div>
            
            <div class="warning">
                This code will expire in 30 minutes for security reasons.
            </div>
            
            <p style="color: #4a4a4a; font-family: Arial, sans-serif; font-size: 15px; margin-bottom: 0; line-height: 1.6;">If you didn't request this password reset, please ignore this email or contact support immediately.</p>
        '''
        content = self._inline_styles(content)
        return self.HTML_TEMP.substitute(content=content)

    def link_accessed(self, username, link_title, link_slug, ip_address):
        """Notification when a link is accessed"""
        safe_username = self.sanitize_input(username)
        safe_title = self.sanitize_input(link_title)
        safe_slug = self.sanitize_input(link_slug)
        safe_ip = self.sanitize_input(ip_address)
        safe_dashboard = self.sanitize_input(self.dashboard)
        
        content = f'''
            <h1 style="color: #d4af37; font-family: Arial, sans-serif; font-size: 28px; font-weight: bold; margin-bottom: 20px; text-align: center;">Link Accessed</h1>
            
            <div class="status-indicator">ACCESS DETECTED</div>
            
            <p style="color: #4a4a4a; font-family: Arial, sans-serif; font-size: 16px; margin-bottom: 20px; line-height: 1.6;">Dear {safe_username},</p>
            <p style="color: #4a4a4a; font-family: Arial, sans-serif; font-size: 16px; margin-bottom: 20px; line-height: 1.6;">Your permanent link has been accessed.</p>
            
            <div class="message-box">
                <p style="color: #4a4a4a; font-family: Arial, sans-serif; margin-bottom: 12px; font-size: 15px;"><strong style="color: #d4af37;">Link Title:</strong> {safe_title}</p>
                <p style="color: #4a4a4a; font-family: Arial, sans-serif; margin-bottom: 12px; font-size: 15px;"><strong style="color: #d4af37;">Link Slug:</strong> {safe_slug}</p>
                <p style="color: #4a4a4a; font-family: Arial, sans-serif; margin-bottom: 12px; font-size: 15px;"><strong style="color: #d4af37;">Access Time:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                <p style="color: #4a4a4a; font-family: Arial, sans-serif; margin-bottom: 0; font-size: 15px;"><strong style="color: #d4af37;">IP Address:</strong> {safe_ip}</p>
            </div>
            
            <div class="btn-container">
                <a href="{safe_dashboard}" class="btn">View Link Statistics</a>
            </div>
            
            <div class="warning">
                Monitor your link activity regularly for security purposes.
            </div>
        '''
        content = self._inline_styles(content)
        return self.HTML_TEMP.substitute(content=content)

    def link_expiring(self, username, link_title, link_slug, days_until_expiry):
        """Notification when a link is about to expire"""
        safe_username = self.sanitize_input(username)
        safe_title = self.sanitize_input(link_title)
        safe_slug = self.sanitize_input(link_slug)
        safe_days = self.sanitize_input(str(days_until_expiry))
        safe_dashboard = self.sanitize_input(self.dashboard)
        
        content = f'''
            <h1 style="color: #d4af37; font-family: Arial, sans-serif; font-size: 28px; font-weight: bold; margin-bottom: 20px; text-align: center;">Link Expiration Warning</h1>
            
            <div class="status-indicator">EXPIRATION WARNING</div>
            
            <p style="color: #4a4a4a; font-family: Arial, sans-serif; font-size: 16px; margin-bottom: 20px; line-height: 1.6;">Dear {safe_username},</p>
            <p style="color: #4a4a4a; font-family: Arial, sans-serif; font-size: 16px; margin-bottom: 20px; line-height: 1.6;">One of your permanent links is about to expire.</p>
            
            <div class="message-box">
                <p style="color: #4a4a4a; font-family: Arial, sans-serif; margin-bottom: 12px; font-size: 15px;"><strong style="color: #d4af37;">Link Title:</strong> {safe_title}</p>
                <p style="color: #4a4a4a; font-family: Arial, sans-serif; margin-bottom: 12px; font-size: 15px;"><strong style="color: #d4af37;">Link Slug:</strong> {safe_slug}</p>
                <p style="color: #4a4a4a; font-family: Arial, sans-serif; margin-bottom: 0; font-size: 15px;"><strong style="color: #d4af37;">Days Until Expiry:</strong> <span style="color: #d4af37; font-weight: bold;">{safe_days}</span></p>
            </div>
            
            <p style="color: #4a4a4a; font-family: Arial, sans-serif; font-size: 16px; margin-bottom: 20px; line-height: 1.6;">To keep this link active, please extend its expiration date or create a new link.</p>
            
            <div class="btn-container">
                <a href="{safe_dashboard}" class="btn">Manage Your Links</a>
            </div>
            
            <div class="warning">
                Once expired, this link will no longer redirect to the destination URL.
            </div>
        '''
        content = self._inline_styles(content)
        return self.HTML_TEMP.substitute(content=content)

    def link_deleted(self, username, link_title, link_slug):
        """Notification when a link is deleted"""
        safe_username = self.sanitize_input(username)
        safe_title = self.sanitize_input(link_title)
        safe_slug = self.sanitize_input(link_slug)
        safe_dashboard = self.sanitize_input(self.dashboard)
        
        content = f'''
            <h1 style="color: #d4af37; font-family: Arial, sans-serif; font-size: 28px; font-weight: bold; margin-bottom: 20px; text-align: center;">Link Deleted</h1>
            
            <div class="status-indicator">LINK REMOVED</div>
            
            <p style="color: #4a4a4a; font-family: Arial, sans-serif; font-size: 16px; margin-bottom: 20px; line-height: 1.6;">Dear {safe_username},</p>
            <p style="color: #4a4a4a; font-family: Arial, sans-serif; font-size: 16px; margin-bottom: 20px; line-height: 1.6;">A link has been permanently deleted from your account.</p>
            
            <div class="message-box">
                <p style="color: #4a4a4a; font-family: Arial, sans-serif; margin-bottom: 12px; font-size: 15px;"><strong style="color: #d4af37;">Link Title:</strong> {safe_title}</p>
                <p style="color: #4a4a4a; font-family: Arial, sans-serif; margin-bottom: 12px; font-size: 15px;"><strong style="color: #d4af37;">Link Slug:</strong> {safe_slug}</p>
                <p style="color: #4a4a4a; font-family: Arial, sans-serif; margin-bottom: 0; font-size: 15px;"><strong style="color: #d4af37;">Deleted At:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            </div>
            
            <div class="btn-container">
                <a href="{safe_dashboard}" class="btn">View Remaining Links</a>
            </div>
            
            <div class="warning">
                This action cannot be undone. The link is no longer accessible.
            </div>
        '''
        content = self._inline_styles(content)
        return self.HTML_TEMP.substitute(content=content)

    def api_token_generated(self, username, email):
        """Notification when API token is generated"""
        safe_username = self.sanitize_input(username)
        safe_email = self.sanitize_input(email)
        safe_dashboard = self.sanitize_input(self.dashboard)
        
        content = f'''
            <h1 style="color: #d4af37; font-family: Arial, sans-serif; font-size: 28px; font-weight: bold; margin-bottom: 20px; text-align: center;">API Token Generated</h1>
            
            <div class="status-indicator">TOKEN CREATED</div>
            
            <p style="color: #4a4a4a; font-family: Arial, sans-serif; font-size: 16px; margin-bottom: 20px; line-height: 1.6;">Dear {safe_username},</p>
            <p style="color: #4a4a4a; font-family: Arial, sans-serif; font-size: 16px; margin-bottom: 20px; line-height: 1.6;">A new API token has been generated for your account.</p>
            
            <div class="message-box">
                <p style="color: #4a4a4a; font-family: Arial, sans-serif; margin-bottom: 12px; font-size: 15px;"><strong style="color: #d4af37;">Account Email:</strong> {safe_email}</p>
                <p style="color: #4a4a4a; font-family: Arial, sans-serif; margin-bottom: 12px; font-size: 15px;"><strong style="color: #d4af37;">Generated At:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                <p style="color: #4a4a4a; font-family: Arial, sans-serif; margin-bottom: 0; font-size: 15px;"><strong style="color: #d4af37;">Token Type:</strong> <span style="color: #d4af37; font-weight: bold;">API Access</span></p>
            </div>
            
            <p style="color: #4a4a4a; font-family: Arial, sans-serif; font-size: 16px; margin-bottom: 20px; line-height: 1.6;">You can use this token to access the LinkFroge API for programmatic link management.</p>
            
            <div class="btn-container">
                <a href="{safe_dashboard}" class="btn">View API Token</a>
            </div>
            
            <div class="warning">
                Keep your API token secure. Do not share it with anyone.
            </div>
        '''
        content = self._inline_styles(content)
        return self.HTML_TEMP.substitute(content=content)

    # ===== Email Sending Methods =====
    def send_email(self, subject, html_body, recipient):
        """
        Sends email safely with HTML and plain-text fallback.
        """
        try:
            if not self.validate_email(recipient):
                logger.error(f"Invalid email address: {recipient}")
                return False

            msg = EmailMessage()
            # Enhanced plain-text fallback
            plain_text = f"""
            LINKFROGE NOTIFICATION
            =========================
            
            Subject: {subject}
            
            This is an important notification from LinkFroge.
            Please use an HTML-compatible email client to view the full content.
            
            For security reasons, some content may only be visible in HTML format.
            
            (c) 2024 LinkFroge Link Management System
            """
            msg.set_content(plain_text)
            # HTML content
            msg.add_alternative(html_body, subtype="html")

            msg['Subject'] = subject
            msg['From'] = config.EMAIL
            msg['To'] = recipient

            with smtplib.SMTP(config.SMTP_LINK, config.SMTP_PORT) as smtp:
                smtp.starttls()
                smtp.login(config.EMAIL, config.EMAIL_PASSWORD)
                smtp.send_message(msg)

            logger.info(f"Email sent successfully to {recipient}")
            return True

        except smtplib.SMTPRecipientsRefused as e:
            logger.error(f"Recipient refused: {recipient} - {e}")
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed: {e}")
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error sending email: {e}")
            logger.error(traceback.format_exc())
        
        return False

    def send_batch_emails(self, subject, html_body, recipients):
        """Send email to multiple recipients"""
        success_count = 0
        failed_count = 0
        
        for recipient in recipients:
            if self.send_email(subject, html_body, recipient):
                success_count += 1
            else:
                failed_count += 1
                
        logger.info(f"Batch email result: {success_count} successful, {failed_count} failed")
        return success_count, failed_count


# ===== Testing =====
if __name__ == "__main__":
    def test_all_templates():
        email_bot = EmailTemplate('https://linkfroge.com')
        
        print("LinkFroge Email System - White & Gold Theme")
        print("=" * 50)
        
        # Test SMTP configuration first
        print("Testing SMTP configuration...")
        if not email_bot.check_smtp_config():
            print("SMTP configuration test failed. Please check your settings.")
            return
        
        test_email = 'testuser@example.com'
        templates_to_test = [
            ('Welcome to LinkFroge', email_bot.welcome_email('TestUser', test_email)),
            ('New Link Created', email_bot.link_created('TestUser', 'My Website', 'https://example.com', 'my-link')),
            ('Password Reset Request', email_bot.reset_password('TestUser', 'LF-789-XYZ', test_email)),
            ('Link Accessed', email_bot.link_accessed('TestUser', 'My Website', 'my-link', '192.168.1.100')),
            ('Link Expiring Soon', email_bot.link_expiring('TestUser', 'My Website', 'my-link', 5)),
            ('Link Deleted', email_bot.link_deleted('TestUser', 'My Website', 'my-link')),
            ('API Token Generated', email_bot.api_token_generated('TestUser', test_email))
        ]
        
        print("Testing all email templates...")
        print("-" * 50)
        
        success_count = 0
        for subject, content in templates_to_test:
            print(f"Sending: {subject}")
            if email_bot.send_email(subject, content, test_email):
                print(f"   {subject} sent successfully")
                success_count += 1
            else:
                print(f"   {subject} failed to send")
        
        print("-" * 50)
        print(f"Email testing completed: {success_count}/{len(templates_to_test)} successful")

    # Run comprehensive tests
    test_all_templates()