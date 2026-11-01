from fastapi import FastAPI

from app.database import engine, Base
from app import models
from app.routes import products

app = FastAPI(
    title="CampusCart Product Catalog",
    description="REST API for managing campus marketplace products",
    version="1.0.0"
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Register Product Catalog routes
app.include_router(products.router)


@app.get("/")
def home():
    return {
        "message": "Welcome to CampusCart Product Catalog Service",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {
        "service": "product-catalog",
        "status": "healthy"
    }
