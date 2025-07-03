from fastapi import FastAPI, HTTPException, status, Depends
from service import Service

app = FastAPI(title="TicketHub", description="Ticket Hub application", version="0.0.1")

service = Service()


def get_service() -> Service:
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service not available"
        )
    return service

@app.get(
    "/"
)
async def get_hello_message():
    return {"message" : "Hello from TicketHub"}


@app.get(
    "/tickets/{id}"
)
async def get_ticket(id: int, service: Service = Depends(get_service)):
    try:
        ticket = await service.get_ticket(id)
        if ticket is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
        return ticket
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", port=8080, reload=True)
