import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.health import router as base_health_router
from app.routers import admin, attendance, auth, employees, health, onboarding, passes, renewals

configure_logging()
settings = get_settings()
logger = get_logger(__name__)

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown events."""
    # Startup
    logger.info("Application startup", extra={"env": settings.app_env})

    # Create database tables if they don't exist
    try:
        from app.models import Base
        from app.database import engine, AsyncSessionLocal
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database tables created/verified")

        # Run startup migrations (seeding) immediately after table creation
        try:
            from app.startup_migrations import run_startup_migrations
            async with AsyncSessionLocal() as session:
                await run_startup_migrations(session)
            logger.info("✅ Startup migrations completed in lifespan")
        except Exception as e:
            logger.error(f"❌ Startup migrations failed in lifespan: {e}")
            import traceback
            logger.error(traceback.format_exc())
    except Exception as e:
        logger.error(f"❌ Failed to create database tables: {e}")
        import traceback
        logger.error(traceback.format_exc())

    # Start attendance scheduler for background jobs
    try:
        from app.services.attendance_scheduler import start_attendance_scheduler
        start_attendance_scheduler()
        logger.info("Attendance scheduler started")
    except Exception as e:
        logger.warning(f"Could not start attendance scheduler: {e}")

    yield
    
    # Shutdown
    try:
        from app.services.attendance_scheduler import stop_attendance_scheduler
        stop_attendance_scheduler()
        logger.info("Attendance scheduler stopped")
    except Exception as e:
        logger.warning(f"Could not stop attendance scheduler: {e}")
    
    logger.info("Application shutdown")


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)
    
    app.state.limiter = limiter

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
        return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.get_allowed_origins_list(),
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        allow_headers=["Content-Type", "Authorization"]
    )

    app.include_router(base_health_router)
    app.include_router(health.router, prefix=settings.api_prefix)
    app.include_router(auth.router, prefix=settings.api_prefix)
    app.include_router(employees.router, prefix=settings.api_prefix)
    app.include_router(renewals.router, prefix=settings.api_prefix)
    app.include_router(passes.router, prefix=settings.api_prefix)
    app.include_router(onboarding.router, prefix=settings.api_prefix)
    app.include_router(attendance.router, prefix=settings.api_prefix)
    app.include_router(admin.router, prefix=settings.api_prefix)
    from app.routers import templates, audit_logs, notifications, activity_logs
    from app.routers import employee_compliance, employee_bank, employee_documents
    from app.routers import recruitment, interview  # , performance
    app.include_router(templates.router, prefix=settings.api_prefix)
    app.include_router(audit_logs.router, prefix=settings.api_prefix)
    app.include_router(notifications.router, prefix=settings.api_prefix)
    app.include_router(activity_logs.router, prefix=settings.api_prefix)
    app.include_router(employee_compliance.router)
    app.include_router(employee_bank.router)
    app.include_router(employee_documents.router)
    # Recruitment module - under admin section
    app.include_router(recruitment.router, prefix=settings.api_prefix)
    # Interview scheduling
    app.include_router(interview.router, prefix=settings.api_prefix)
    
    # SIMPLIFICATION: Commented out low-usage features for solo HR
    # To re-enable, uncomment the imports and include_router lines below
    
    # Performance management - typically used yearly, can use Excel instead
    # app.include_router(performance.router, prefix=settings.api_prefix)
    
    # Employee of the Year nominations - seasonal feature (EOY only)
    # from app.routers import nominations
    # app.include_router(nominations.router, prefix=settings.api_prefix)
    
    # Insurance Census management - quarterly, may be overkill for small teams
    # from app.routers import insurance_census
    # app.include_router(insurance_census.router, prefix=settings.api_prefix)
    
    # Timesheets - can be replaced with Excel export of attendance logs
    # from app.routers import timesheets
    # app.include_router(timesheets.router, prefix=settings.api_prefix)
    
    # Enhanced Attendance Module routers - keeping core leave and holidays
    from app.routers import leave, public_holidays  # , timesheets, geofences
    app.include_router(leave.router, prefix=settings.api_prefix)
    app.include_router(public_holidays.router, prefix=settings.api_prefix)
    
    # Geofences - advanced attendance feature, may not be needed for basic operations
    # from app.routers import geofences
    # app.include_router(geofences.router, prefix=settings.api_prefix)

    @app.on_event("startup")
    async def on_startup():
        # Legacy startup hook (kept for compatibility, main logic in lifespan)
        logger.info("Application startup", extra={"env": settings.app_env})

        # Run startup migrations for data consistency
        try:
            from app.startup_migrations import run_startup_migrations
            from app.database import AsyncSessionLocal
            async with AsyncSessionLocal() as session:
                await run_startup_migrations(session)
            logger.info("✅ Startup migrations completed successfully")
        except Exception as e:
            import traceback
            logger.error(f"❌ Startup migrations failed: {e}")
            logger.error(f"Startup migration traceback: {traceback.format_exc()}")
            logger.error("=" * 80)
            logger.error("STARTUP MIGRATION FAILURE - RECOVERY INSTRUCTIONS:")
            logger.error("1. Check database connectivity: curl http://localhost:8000/api/health/db")
            logger.error("2. Reset admin password: curl -X POST http://localhost:8000/api/health/reset-admin-password -H 'X-Admin-Secret: YOUR_SECRET'")
            logger.error("3. Check logs above for specific error details")
            logger.error("=" * 80)
            
            # In production, log but continue (don't crash the app)
            # Admins can use /api/health/reset-admin-password to recover
            if settings.app_env == "development":
                logger.warning("⚠️  Continuing in development mode despite migration failure")
            else:
                logger.error("⚠️  Continuing in production mode - use emergency endpoints to recover")

    @app.on_event("shutdown")
    async def on_shutdown():
        # Legacy shutdown hook (kept for compatibility, main logic in lifespan)
        pass

    # Serve static files in production (frontend build)
    # Check multiple possible locations for the frontend build
    possible_static_dirs = [
        Path(__file__).parent.parent / "static",  # backend/static
        Path(__file__).parent.parent.parent / "frontend" / "dist",  # frontend/dist
    ]
    
    static_dir = None
    for dir_path in possible_static_dirs:
        if dir_path.exists() and (dir_path / "index.html").exists():
            static_dir = dir_path
            break
    
    if static_dir:
        assets_dir = static_dir / "assets"
        if assets_dir.exists():
            app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")
        
        @app.get("/{full_path:path}")
        async def serve_spa(full_path: str):
            # Don't intercept API routes
            if full_path.startswith("api/"):
                return JSONResponse(status_code=404, content={"detail": "Not found"})
            # Serve index.html for all other routes (SPA routing)
            index_file = static_dir / "index.html"
            if index_file.exists():
                # Prevent stale cached index.html so new builds show immediately
                return FileResponse(
                    str(index_file),
                    headers={
                        "Cache-Control": "no-store, no-cache, must-revalidate",
                        "Pragma": "no-cache",
                    },
                )
            return JSONResponse(status_code=404, content={"detail": "Frontend not built"})

    return app


app = create_app()
