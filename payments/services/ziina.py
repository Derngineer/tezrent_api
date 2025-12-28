"""
Ziina Payment Gateway Client

Handles all interactions with the Ziina API for payment processing.
Documentation: https://docs.ziina.com
"""

import requests
import logging
from django.conf import settings
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class ZiinaClient:
    """
    Client for interacting with Ziina Payment API
    
    Usage:
        client = ZiinaClient()
        
        # Create a payment
        result = client.create_payment_intent(
            amount=1500,  # Amount in cents (15.00 AED)
            rental_reference="RNT-2024-001",
            success_url="tezrent://payment/success",
            cancel_url="tezrent://payment/failed"
        )
        
        # Verify payment status
        status = client.get_payment_status(payment_id)
    """
    
    BASE_URL = "https://api-v2.ziina.com/api"
    
    def __init__(self):
        self.api_key = getattr(settings, 'ZIINA_API_KEY', None)
        self.test_mode = getattr(settings, 'ZIINA_TEST_MODE', True)
        
        if not self.api_key:
            logger.warning("ZIINA_API_KEY not configured in settings")
    
    @property
    def headers(self) -> Dict[str, str]:
        """Return headers for Ziina API requests"""
        return {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {self.api_key}"
        }
    
    def create_payment_intent(
        self,
        amount: int,
        rental_reference: str,
        success_url: str,
        cancel_url: str,
        currency_code: str = "AED",
        message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a Ziina payment intent
        
        Args:
            amount: Amount in the smallest currency unit (e.g., fils for AED)
                    For AED: 1500 = 15.00 AED
            rental_reference: Reference ID for the rental (used in message)
            success_url: URL to redirect on successful payment
            cancel_url: URL to redirect on cancelled/failed payment
            currency_code: Currency code (default: AED)
            message: Custom message for the payment
            
        Returns:
            dict with keys:
                - success: bool
                - payment_id: str (Ziina payment intent ID)
                - redirect_url: str (URL to redirect user for payment)
                - error: str (if success is False)
        """
        url = f"{self.BASE_URL}/payment_intent"
        
        payload = {
            "currency_code": currency_code,
            "amount": amount,
            "message": message or f"Payment for rental {rental_reference}",
            "success_url": success_url,
            "cancel_url": cancel_url,
            "test": self.test_mode
        }
        
        try:
            logger.info(f"Creating Ziina payment intent for {rental_reference}, amount: {amount}")
            response = requests.post(url, json=payload, headers=self.headers, timeout=30)
            response_data = response.json()
            
            if response.status_code == 200 or response.status_code == 201:
                logger.info(f"Ziina payment intent created: {response_data.get('id')}")
                return {
                    "success": True,
                    "payment_id": response_data.get('id'),
                    "redirect_url": response_data.get('redirect_url'),
                    "raw_response": response_data
                }
            else:
                logger.error(f"Ziina API error: {response_data}")
                return {
                    "success": False,
                    "error": response_data.get('message', 'Payment creation failed'),
                    "raw_response": response_data
                }
                
        except requests.exceptions.Timeout:
            logger.error("Ziina API timeout")
            return {
                "success": False,
                "error": "Payment gateway timeout. Please try again."
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Ziina API request error: {str(e)}")
            return {
                "success": False,
                "error": "Payment gateway unavailable. Please try again later."
            }
        except Exception as e:
            logger.error(f"Unexpected error creating Ziina payment: {str(e)}")
            return {
                "success": False,
                "error": "An unexpected error occurred."
            }
    
    def get_payment_status(self, payment_id: str) -> Dict[str, Any]:
        """
        Get the status of a Ziina payment intent
        
        Args:
            payment_id: The Ziina payment intent ID
            
        Returns:
            dict with keys:
                - success: bool
                - status: str (pending, completed, failed, etc.)
                - amount: int
                - currency_code: str
                - error: str (if success is False)
        """
        url = f"{self.BASE_URL}/payment_intent/{payment_id}"
        
        try:
            logger.info(f"Checking Ziina payment status for: {payment_id}")
            response = requests.get(url, headers=self.headers, timeout=30)
            response_data = response.json()
            
            if response.status_code == 200:
                status = response_data.get('status')
                logger.info(f"Ziina payment {payment_id} status: {status}")
                return {
                    "success": True,
                    "status": status,
                    "amount": response_data.get('amount'),
                    "currency_code": response_data.get('currency_code'),
                    "is_completed": status == 'completed',
                    "raw_response": response_data
                }
            else:
                logger.error(f"Ziina API error getting status: {response_data}")
                return {
                    "success": False,
                    "error": response_data.get('message', 'Could not retrieve payment status')
                }
                
        except requests.exceptions.Timeout:
            logger.error("Ziina API timeout while checking status")
            return {
                "success": False,
                "error": "Payment gateway timeout."
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Ziina API request error: {str(e)}")
            return {
                "success": False,
                "error": "Payment gateway unavailable."
            }
        except Exception as e:
            logger.error(f"Unexpected error checking Ziina payment: {str(e)}")
            return {
                "success": False,
                "error": "An unexpected error occurred."
            }
    
    def is_payment_completed(self, payment_id: str) -> bool:
        """
        Quick check if a payment is completed
        
        Args:
            payment_id: The Ziina payment intent ID
            
        Returns:
            True if payment is completed, False otherwise
        """
        result = self.get_payment_status(payment_id)
        return result.get('is_completed', False)
