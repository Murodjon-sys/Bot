"""
TSPay to'lov tizimi integratsiyasi
API: https://tspay.uz/api/v1/
"""
import requests
import logging
from typing import Optional, Dict, Tuple
from config import TSPAY_API_KEY

logger = logging.getLogger(__name__)


class TSPayError(Exception):
    """TSPay API xatolari"""
    pass


class TSPayService:
    """TSPay to'lov tizimi bilan ishlash"""
    
    BASE_URL = "https://tspay.uz/api/v1"
    
    def __init__(self):
        self.api_key = TSPAY_API_KEY
        if not self.api_key:
            logger.error("TSPAY_API_KEY not configured!")
    
    def _get_headers(self) -> Dict[str, str]:
        """
        API so'rovlar uchun headerlar
        """
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def create_payment(
        self, 
        amount: int, 
        description: str,
        order_id: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        To'lov yaratish
        
        Args:
            amount: Summa (so'm)
            description: To'lov tavsifi
            order_id: Buyurtma ID (ixtiyoriy)
        
        Returns:
            (payment_url, transaction_id) - To'lov havolasi va tranzaksiya ID
        """
        if not self.api_key:
            raise TSPayError("API key not configured")
        
        try:
            url = f"{self.BASE_URL}/transactions/create/"
            
            # Description ga order_id qo'shish (keyinchalik topish uchun)
            full_description = description
            if order_id:
                full_description = f"{description} (Order: {order_id})"
            
            data = {
                'amount': amount,
                'access_token': self.api_key,
                'description': full_description
            }
            
            logger.info(f"TSPay: To'lov yaratilmoqda - {amount} so'm")
            response = requests.post(url, json=data, headers=self._get_headers(), timeout=10)
            response.raise_for_status()
            
            result = response.json()
            transaction = result.get('transaction')
            
            if not transaction:
                raise TSPayError("Tranzaksiya yaratilmadi")
            
            payment_url = transaction['payment_url']
            cheque_id = transaction['cheque_id']
            
            logger.info(f"TSPay: To'lov yaratildi - ID: {cheque_id}")
            return payment_url, cheque_id
            
        except requests.RequestException as e:
            logger.error(f"TSPay to'lov yaratishda xato: {e}")
            raise TSPayError(f"To'lov yaratishda xato: {e}")
    
    def check_payment_status(self, transaction_id: str) -> str:
        """
        To'lov statusini tekshirish
        
        Args:
            transaction_id: Tranzaksiya ID (cheque_id)
        
        Returns:
            status: 'success', 'pending', 'failed', 'cancelled'
        """
        if not self.api_key:
            raise TSPayError("API key not configured")
        
        try:
            url = f"{self.BASE_URL}/transactions/{transaction_id}/"
            
            logger.info(f"TSPay: Status tekshirilmoqda - {transaction_id}")
            response = requests.get(url, headers=self._get_headers(), timeout=10)
            response.raise_for_status()
            
            result = response.json()
            status = result.get('status', 'unknown')
            
            logger.info(f"TSPay: Status - {status}")
            return status
            
        except requests.RequestException as e:
            logger.error(f"TSPay status tekshirishda xato: {e}")
            raise TSPayError(f"Status tekshirishda xato: {e}")
    
    def get_transaction_details(self, transaction_id: str) -> Dict:
        """
        To'lov to'liq ma'lumotlarini olish
        
        Args:
            transaction_id: Tranzaksiya ID
        
        Returns:
            dict: To'lov ma'lumotlari
        """
        if not self.api_key:
            raise TSPayError("API key not configured")
        
        try:
            url = f"{self.BASE_URL}/transactions/{transaction_id}/"
            
            response = requests.get(url, headers=self._get_headers(), timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"TSPay ma'lumot olishda xato: {e}")
            raise TSPayError(f"Ma'lumot olishda xato: {e}")


# Global instance
tspay = TSPayService()
