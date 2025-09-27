from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
import uuid


app = FastAPI()
# cross origin resource sharing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data
products = [
    {"id": 1, "name": "Shirt", "price": 20.0, "category": "Clothing"},
    {"id": 2, "name": "Hat", "price": 15.0, "category": "Accessories"},
    {"id": 3, "name": "Skirt", "price": 30.0, "category": "Clothing"},
    {"id": 4, "name": "Socks", "price": 5.0, "category": "Clothing"},
    {"id": 5, "name": "Belt", "price": 10.0, "category": "Accessories"},
    {"id": 6, "name": "Jacket", "price": 50.0, "category": "Clothing"},
    {"id": 7, "name": "Phone", "price": 699.0, "category": "Electronics"},
    {"id": 8, "name": "Laptop", "price": 999.0, "category": "Electronics"}
]

orders = []

class LoginRequest(BaseModel):
    username: str
    password: str

class CartItem(BaseModel):
    productId: int
    qty: int

class CartRequest(BaseModel):
    items: List[CartItem]

class Address(BaseModel):
    street: str
    city: str
    state: str
    zip: str
    country: str

class CardInfo(BaseModel):
    number: str
    expiry: str
    cvv: str
    name: str

class CheckoutRequest(BaseModel):
    cartId: str
    address: Address
    card: CardInfo



@app.get("/")
async def root():
    return {"message": "Mock backend is running"}

@app.post("/api/login")
async def login(req: LoginRequest):
    if req.username == "test" and req.password == "pass":
        return {"token": "abc123"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/api/products")
async def get_products(category: Optional[str] = None, minPrice: Optional[float] = 0, maxPrice: Optional[float] = float('inf')):
    filtered = [p for p in products if p["price"] >= minPrice and p["price"] <= maxPrice]
    if category:
        filtered = [p for p in filtered if p["category"] == category]
    return filtered

@app.post("/api/cart")
async def add_to_cart(req: CartRequest):
    total = 0
    cartId ="cart"
    for item in req.items:
        product = next((p for p in products if p["id"] == item.productId), None)
        if not product:
            raise HTTPException(status_code=400, detail="Product not found")
        cartId += f"-{item.productId}x{item.qty}"
        total += product["price"] * item.qty
    return {"cartId": cartId, "totalBeforeTax": total}

@app.post("/api/checkout")
async def checkout(req: CheckoutRequest):
    if not req.card:
        raise HTTPException(status_code=422, detail="Missing address or card")
    if not all([req.address.street, req.address.city, req.address.state, req.address.zip, req.address.country]):
        raise HTTPException(status_code=422, detail="Missing address or card")

    if not all([req.card.number, req.card.expiry, req.card.cvv, req.card.name]):
        raise HTTPException(status_code=422, detail="Missing address or card")

    # Check cartId format 
    cart_parts = req.cartId.split('-')[1:]  # Splits cartId like 'cart-1x2-2x1'
    if not cart_parts:
        raise HTTPException(status_code=400, detail="Invalid cartId format")
    
    total = 0
    for q in req.cartId.split('-')[1:]:
        
        pid, qty = "",""
        try:
            pid, qty = q.split('x')
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid cartId format")
            
        product = next((p for p in products if p["id"] == int(pid)), None)
        if product:
            total += product["price"]*int(qty)
    total_with_tax = total + total * 0.2  # 20% tax
    order_id = str(uuid.uuid4())  # Unique order ID
    order = {
        "orderId": order_id,
        "cartId": req.cartId,
        "items": [{"productId": int(q.split('x')[0]), "qty": int(q.split('x')[1])} for q in cart_parts],
        "totalWithTax":total_with_tax,
        "taxApplied": total * 0.2 
    }
    orders.append(order)

    return {"orderId": order_id, "totalWithTax": total_with_tax, "taxApplied": total * 0.2}

@app.get("/api/order/{orderId}")
async def get_order(orderId: str):
    order = next((o for o in orders if o["orderId"] == orderId), None)
    if not order:
        return HTTPException(status_code=404, detail="Order not found")
    
    return {"orderId": order["orderId"], "items": order["items"], "totals": order["totalWithTax"]}

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}
