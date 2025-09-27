"""
API client utilities for MiniShop automation.
"""
import requests
from typing import Dict, Any, Optional, List
import json
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class APIClient:
    """Robust API client with retry logic and error handling."""
    
    def __init__(self, base_url: str, timeout: int = 10):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request with error handling."""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                timeout=self.timeout,
                **kwargs
            )
            return response
        except requests.exceptions.RequestException as e:
            raise APIClientError(f"Request failed: {str(e)}")
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> requests.Response:
        """Make GET request."""
        return self._make_request('GET', endpoint, params=params)
    
    def post(self, endpoint: str, data: Optional[Dict] = None, json_data: Optional[Dict] = None) -> requests.Response:
        """Make POST request."""
        kwargs = {}
        if json_data is not None:
            kwargs['json'] = json_data
        elif data is not None:
            kwargs['data'] = json.dumps(data)
            kwargs['headers'] = {'Content-Type': 'application/json'}
        
        return self._make_request('POST', endpoint, **kwargs)
    
    def put(self, endpoint: str, data: Optional[Dict] = None, json_data: Optional[Dict] = None) -> requests.Response:
        """Make PUT request."""
        kwargs = {}
        if json_data is not None:
            kwargs['json'] = json_data
        elif data is not None:
            kwargs['data'] = json.dumps(data)
            kwargs['headers'] = {'Content-Type': 'application/json'}
        
        return self._make_request('PUT', endpoint, **kwargs)
    
    def delete(self, endpoint: str) -> requests.Response:
        """Make DELETE request."""
        return self._make_request('DELETE', endpoint)
    
    def health_check(self) -> bool:
        """Check if API is healthy."""
        try:
            response = self.get('/health')
            return response.status_code == 200
        except:
            return False


class APIClientError(Exception):
    """Custom exception for API client errors."""
    pass


class MiniShopAPI:
    """High-level API client for MiniShop endpoints."""
    
    def __init__(self, base_url: str):
        self.client = APIClient(base_url)
        self.token = None
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Login and get authentication token."""
        response = self.client.post('/login', json_data={
            'username': username,
            'password': password
        })
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get('token')
            return data
        else:
            raise APIClientError(f"Login failed: {response.status_code} - {response.text}")
    
    def get_products(self, category: Optional[str] = None, 
                    min_price: Optional[float] = None, 
                    max_price: Optional[float] = None) -> List[Dict[str, Any]]:
        """Get products with optional filtering."""
        params = {}
        if category:
            params['category'] = category
        if min_price is not None:
            params['minPrice'] = min_price
        if max_price is not None:
            params['maxPrice'] = max_price
        
        response = self.client.get('/products', params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise APIClientError(f"Get products failed: {response.status_code} - {response.text}")
    
    def add_to_cart(self, items: List[Dict[str, int]]) -> Dict[str, Any]:
        """Add items to cart."""
        response = self.client.post('/cart', json_data={'items': items})
        
        if response.status_code == 200:
            return response.json()
        else:
            raise APIClientError(f"Add to cart failed: {response.status_code} - {response.text}")
    
    def checkout(self, cart_id: str, address: Dict[str, str], card: Dict[str, str]) -> Dict[str, Any]:
        """Checkout with address and card information."""
        response = self.client.post('/checkout', json_data={
            'cartId': cart_id,
            'address': address,
            'card': card
        })
        
        if response.status_code == 200:
            return response.json()
        else:
            raise APIClientError(f"Checkout failed: {response.status_code} - {response.text}")
    
    def get_order(self, order_id: str) -> Dict[str, Any]:
        """Get order details by ID."""
        response = self.client.get(f'/order/{order_id}')
        
        if response.status_code == 200:
            return response.json()
        else:
            raise APIClientError(f"Get order failed: {response.status_code} - {response.text}")
    
    def is_healthy(self) -> bool:
        """Check if the API is healthy."""
        return self.client.health_check()