
import os

import httpx
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models
from app.database import Base, engine
from app.dependencies import get_current_user
from app.dependencies import get_db
from app.schemas import (
    CartItemCreate,
    CartItemUpdate,
    CartResponse,
)


# Register models and create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CampusCart Cart Service",
    description="Cart management API for CampusCart",
    version="1.0.0"
)

PRODUCT_CATALOG_URL = os.getenv(
    "PRODUCT_CATALOG_URL",
    "http://localhost:8000"
)


# Fetch products from Product Catalog
def get_product(product_id: int):

    try:
        response = httpx.get(
            f"{PRODUCT_CATALOG_URL}/products/",
            timeout=5.0
        )
        response.raise_for_status()

    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Product Catalog service is unavailable"
        )

    except httpx.HTTPStatusError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Product Catalog returned an error"
        )

    products = response.json()

    for product in products:
        if product["id"] == product_id:
            return product

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Product not found"
    )


# Check whether a product can be added
def validate_product(product: dict, quantity: int):

    if not product.get("is_active"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Product is not available"
        )

    if quantity > product.get("stock_quantity", 0):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Requested quantity exceeds available stock"
        )


# Get or create the authenticated user's cart
def get_or_create_cart(db: Session, user_id: int):

    cart = db.query(models.Cart).filter(
        models.Cart.user_id == user_id
    ).first()

    if cart is None:
        cart = models.Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)

    return cart


@app.get("/")
def root():
    return {"message": "CampusCart Cart Service is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


# Add a product to the user's cart
@app.post(
    "/cart/items",
    response_model=CartResponse,
    status_code=status.HTTP_201_CREATED
)
def add_cart_item(
    item: CartItemCreate,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    product = get_product(item.product_id)

    cart = get_or_create_cart(db, user_id)

    existing_item = db.query(models.CartItem).filter(
        models.CartItem.cart_id == cart.id,
        models.CartItem.product_id == item.product_id
    ).first()

    new_quantity = item.quantity

    if existing_item:
        new_quantity += existing_item.quantity

    validate_product(product, new_quantity)

    if existing_item:
        existing_item.quantity = new_quantity
    else:
        new_item = models.CartItem(
            cart_id=cart.id,
            product_id=item.product_id,
            quantity=item.quantity
        )
        db.add(new_item)

    db.commit()
    db.refresh(cart)

    return cart


# View the authenticated user's cart
@app.get("/cart", response_model=CartResponse)
def get_cart(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    cart = db.query(models.Cart).filter(
        models.Cart.user_id == user_id
    ).first()

    if cart is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found"
        )

    return cart


# Update the quantity of a cart item
@app.put("/cart/items/{item_id}", response_model=CartResponse)
def update_cart_item(
    item_id: int,
    item: CartItemUpdate,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    cart = db.query(models.Cart).filter(
        models.Cart.user_id == user_id
    ).first()

    if cart is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found"
        )

    cart_item = db.query(models.CartItem).filter(
        models.CartItem.id == item_id,
        models.CartItem.cart_id == cart.id
    ).first()

    if cart_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )

    product = get_product(cart_item.product_id)
    validate_product(product, item.quantity)

    cart_item.quantity = item.quantity

    db.commit()
    db.refresh(cart)

    return cart


# Remove one item from the cart
@app.delete("/cart/items/{item_id}")
def remove_cart_item(
    item_id: int,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    cart = db.query(models.Cart).filter(
        models.Cart.user_id == user_id
    ).first()

    if cart is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found"
        )

    cart_item = db.query(models.CartItem).filter(
        models.CartItem.id == item_id,
        models.CartItem.cart_id == cart.id
    ).first()

    if cart_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )

    db.delete(cart_item)
    db.commit()

    return {"message": "Cart item removed successfully"}


# Clear the authenticated user's cart
@app.delete("/cart")
def clear_cart(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    cart = db.query(models.Cart).filter(
        models.Cart.user_id == user_id
    ).first()

    if cart is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found"
        )

    db.query(models.CartItem).filter(
        models.CartItem.cart_id == cart.id
    ).delete(synchronize_session=False)

    db.commit()

    return {"message": "Cart cleared successfully"}
