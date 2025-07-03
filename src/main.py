from fastapi import FastAPI, HTTPException, Depends, Query
from service import Service
from typing import Optional, Literal
from models import PaginatedResponse, Ticket
from starlette.status import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
import logging

app = FastAPI(title="TicketHub", description="TicketHub application for Abysalto AI Academy ", version="0.0.1")

service = Service()

logger = logging.getLogger(__name__)


def get_service() -> Service:
    return service


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

        total = len(filtered_tickets)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        tickets_page = filtered_tickets[start_idx:end_idx]

        pages = (total + per_page - 1) // per_page

        return PaginatedResponse(
            items=tickets_page,
            total=total,
            page=page,
            per_page=per_page,
            pages=pages
        )

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

        total = len(filtered_tickets)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        tickets_page = filtered_tickets[start_idx:end_idx]

        pages = (total + per_page - 1) // per_page

        return PaginatedResponse(
            items=tickets_page,
            total=total,
            page=page,
            per_page=per_page,
            pages=pages
        )

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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", port=8080, reload=True)
