from fastapi import FastAPI, HTTPException, Depends, Query
from service import Service
from typing import Optional, Literal
from models import PaginatedResponse
from starlette.status import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR

app = FastAPI(title="TicketHub", description="Ticket Hub application", version="0.0.1")

service = Service()


def get_service() -> Service:
    return service


@app.get(
    "/"
)
async def get_hello_message():
    return {"message": "Hello from TicketHub"}


@app.get(
    "/tickets",
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
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching tickets: {str(e)}"
        )


@app.get(
    "/tickets/{id}"
)
async def get_ticket(id: int, service: Service = Depends(get_service)):
    try:
        ticket = await service.get_ticket(id)
        if ticket is None:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Ticket not found")
        return ticket
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", port=8080, reload=True)
