"""
Custom email backend for macOS SSL certificate issues
"""
import ssl
import smtplib
from django.core.mail.backends.smtp import EmailBackend as SMTPBackend


class CustomEmailBackend(SMTPBackend):
    """
    Custom SMTP backend that bypasses SSL certificate verification.
    Use only for development on macOS where certificate verification fails.
    """
    
    def open(self):
        """
        Override open to use an unverified SSL context
        """
        if self.connection:
            return False
        
        try:
            if self.use_ssl:
                # Use SMTP_SSL with unverified context for port 465
                self.connection = smtplib.SMTP_SSL(
                    self.host,
                    self.port,
                    timeout=self.timeout,
                    context=ssl._create_unverified_context()
                )
            else:
                # Use regular SMTP
                self.connection = smtplib.SMTP(
                    self.host,
                    self.port,
                    timeout=self.timeout
                )
                
            # TLS/STARTTLS for port 587
            if self.use_tls:
                self.connection.ehlo()
                self.connection.starttls(context=ssl._create_unverified_context())
                self.connection.ehlo()
                
            if self.username and self.password:
                self.connection.login(self.username, self.password)
                
            return True
        except Exception as e:
            if not self.fail_silently:
                raise
            return False
