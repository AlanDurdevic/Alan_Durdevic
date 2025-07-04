from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, Query, Request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from service import Service
from typing import Optional, Literal, List
from schemas import PaginatedResponse, Ticket, TicketStats
from starlette.status import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
import logging
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from models import *

import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)

    app.state.engine = engine
    app.state.SessionLocal = SessionLocal
    app.state.service = Service(db_session_factory=SessionLocal)

    yield

    engine.dispose()


app = FastAPI(title="TicketHub",
              description="TicketHub application for Abysalto AI Academy ",
              version="0.0.1",
              lifespan=lifespan)

# rate limiting
app.state.limiter = Limiter(key_func=get_remote_address, default_limits=["5/minute"])
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# logger
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")


def get_service(request: Request) -> Service:
    return request.app.state.service


def get_db(request: Request) -> Session:
    db = request.app.state.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "service": "TicketHub"}


@app.get(
    "/"
)
async def get_hello_message():
    return {"message": "Hello from TicketHub"}


@app.get(
    "/tickets",
    response_model=PaginatedResponse,
    tags=["Tickets"],
    summary="Get paginated list of tickets"
)
async def get_tickets(
        page: int = Query(1, ge=1, description="Page number"),
        per_page: int = Query(10, ge=1, le=100, description="Items per page"),
        status: Optional[Literal["open", "closed"]] = Query(None, description="Filter by status"),
        priority: Optional[Literal["low", "medium", "high"]] = Query(None, description="Filter by priority"),
        service: Service = Depends(get_service)
):
    try:
        all_tickets = await service.get_tickets()

        filtered_tickets = all_tickets
        if status:
            filtered_tickets = [t for t in filtered_tickets if t.status == status]
        if priority:
            filtered_tickets = [t for t in filtered_tickets if t.priority == priority]

        return paginate(filtered_tickets, page, per_page)

    except Exception as e:
        logger.error("Error fetching tickets")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching tickets: {str(e)}"
        )


@app.get(
    "/tickets/search",
    response_model=PaginatedResponse,
    tags=["Tickets"],
    summary="Search tickets by title"
)
async def search_tickets(
        q: str = Query(".", min_length=1, description="Search query"),
        page: int = Query(1, ge=1, description="Page number"),
        per_page: int = Query(10, ge=1, le=100, description="Items per page"),
        service: Service = Depends(get_service)
):
    try:

        all_tickets = await service.get_tickets()

        query_lower = q.lower()
        filtered_tickets = [
            t for t in all_tickets
            if query_lower in t.title.lower()
        ]

        return paginate(filtered_tickets, page, per_page)

    except Exception as e:
        logger.error("Error searching tickets")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching tickets: {str(e)}"
        )


@app.get(
    "/tickets/{ticket_id}",
    response_model=Ticket,
    tags=["Tickets"],
    summary="Get ticket details by ID"
)
async def get_ticket(ticket_id: int,
                     service: Service = Depends(get_service)):
    try:
        ticket = await service.get_ticket(ticket_id)
        if ticket is None:
            logger.error(f"Ticket not found, ID={ticket_id}")
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Ticket not found")
        return ticket
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching ticket, ID={ticket_id}")
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.get(
    "/stats",
    response_model=TicketStats,
    tags=["Statistics"],
    summary="Get ticket statistics"
)
async def get_ticket_stats(
        service: Service = Depends(get_service)
):
    try:
        tickets = await service.get_tickets()
        stats = await service.calculate_stats(tickets)
        return stats

    except Exception as e:
        logger.error(f"Error calculating stats: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating statistics: {str(e)}"
        )


def paginate(items: List, page: int, per_page: int) -> PaginatedResponse:
    total = len(items)
    start = (page - 1) * per_page
    end = start + per_page
    pages = (total + per_page - 1) // per_page
    return PaginatedResponse(
        items=items[start:end],
        total=total,
        page=page,
        per_page=per_page,
        pages=pages
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app",  host="0.0.0.0", port=8080, reload=True)
