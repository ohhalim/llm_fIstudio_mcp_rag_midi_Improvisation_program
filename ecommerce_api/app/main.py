from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

# Import core components
from app.core.config import settings
from app.core.database import create_tables

# Import all models to ensure they're registered with SQLAlchemy
from app.models import user, category, product, order, cart, payment, review

# Import routers (will be created next)
# from app.controllers import auth, users, products, orders, cart, admin

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="A comprehensive e-commerce API with payment integration",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for uploads
if not os.path.exists(settings.UPLOAD_DIR):
    os.makedirs(settings.UPLOAD_DIR)

app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Database initialization
@app.on_event("startup")
async def startup():
    """Initialize database tables on startup"""
    create_tables()
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} started!")
    print(f"📊 Environment: {settings.ENVIRONMENT}")
    print(f"🔍 Debug mode: {settings.DEBUG}")


# Health check endpoint
@app.get("/", tags=["Health"])
async def root():
    """Root endpoint for health check"""
    return {
        "message": f"Welcome to {settings.APP_NAME}!",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "status": "healthy"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check endpoint"""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG
    }


# Include routers
from app.controllers import auth, products, cart

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(products.router, prefix="/api/v1/products", tags=["Products"])
app.include_router(cart.router, prefix="/api/v1/cart", tags=["Cart"])
# app.include_router(orders.router, prefix="/api/v1/orders", tags=["Orders"])
# app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )