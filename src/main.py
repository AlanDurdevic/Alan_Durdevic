from fastapi import FastAPI

app = FastAPI(title="TicketHub", description="Ticket Hub application", version="0.0.1")


@app.get(
    "/"
)
async def get_hello_message():
    return "Hello from TicketHub"


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", port=8080, reload=True)
