"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.core.config import settings
from app.database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown."""
    # Create tables (for development; use Alembic in production)
    Base.metadata.create_all(bind=engine)

    # Seed initial data
    from app.database import SessionLocal
    from app.models.user import User
    from app.models.role import Role
    from app.core.security import get_password_hash

    db = SessionLocal()
    try:
        # Check if admin user exists
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                password_hash=get_password_hash("admin123"),
                real_name="系统管理员",
                is_active=True,
                is_admin=True,
            )
            db.add(admin)
            db.commit()
            print("[Startup] Created default admin user: admin / admin123")

        # Create default roles if none exist
        if db.query(Role).count() == 0:
            roles = [
                Role(name="管理员", code="admin", description="系统管理员，拥有全部权限"),
                Role(name="运维人员", code="operator", description="运维人员，可查看和管理资产"),
                Role(name="普通用户", code="user", description="普通用户，仅可查看"),
            ]
            for role in roles:
                db.add(role)
            db.commit()
            print("[Startup] Created default roles")
    finally:
        db.close()

    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="IT 综合运维管理系统 API",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["健康检查"])
def root():
    """Root endpoint."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/api/docs",
    }


@app.get("/api/health", tags=["健康检查"])
def health():
    """Health check endpoint."""
    return {"status": "ok"}
