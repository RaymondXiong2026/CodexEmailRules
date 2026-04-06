import logging

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes.review import router as review_router
from app.core.config import get_settings
from app.core.exceptions import BizException
from app.core.logging import setup_logging
from app.db.base import Base
from app.db.session import engine
from app.schemas import ApiResponse
from app.tasks.email_poller import EmailPoller

settings = get_settings()
setup_logging(settings.log_level)
logger = logging.getLogger(__name__)
poller = EmailPoller()

app = FastAPI(title=settings.app_name)
app.include_router(review_router)


@app.on_event("startup")
async def startup_event():
    logger.info("Starting app...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    poller.start()


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Stopping app...")
    poller.shutdown()


@app.exception_handler(BizException)
async def biz_exception_handler(_: Request, exc: BizException):
    return JSONResponse(status_code=exc.status_code, content=ApiResponse(code=exc.status_code, message=exc.detail).model_dump())


@app.exception_handler(Exception)
async def global_exception_handler(_: Request, exc: Exception):
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(status_code=500, content=ApiResponse(code=500, message="Internal Server Error").model_dump())


if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=False)
