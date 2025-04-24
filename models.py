from flask_login import UserMixin
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime

@dataclass
class User(UserMixin):
    id: str
    username: str
    email: str
    password_hash: str
    is_seller: bool = False
    is_admin: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    
    def get_id(self):
        return self.id

@dataclass
class Product:
    id: str
    name: str
    description: str
    price: float
    category_id: str
    seller_id: str
    details: str
    image_urls: List[str]
    specs: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class Category:
    id: str
    name: str
    description: str
    image_url: Optional[str] = None

@dataclass
class Cart:
    user_id: str
    items: Dict[str, int]  # product_id: quantity

@dataclass
class Order:
    id: str
    user_id: str
    total: float
    status: str  # pending, paid, shipped, delivered
    shipping_address: str
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class OrderItem:
    id: str
    order_id: str
    product_id: str
    quantity: int
    price: float
