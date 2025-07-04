# TicketHub - task for Abysalto AI academy
## developer: Alan Đurđević
### version 1.0.0.

#### Simple middleware REST service for collecting and presenting tickets from external sources
#### External sources:
#### - https://dummyjson.com/todos
#### - https://dummyjson.com/users

## Prerequisites
- [Docker](https://www.docker.com/) installed on your machine
- [Docker Compose](https://docs.docker.com/compose/) plugin or standalone binary installed

## Usage

1. **Clone the repository:** `git clone https://github.com/AlanDurdevic/Alan_Durdevic.git`
2. **Start the services:** `docker compose --env-file .env up --build`
3. **Access the application:**
- Open your browser and go to `http://localhost:8080`

## Documentation
- `http://localhost:8080/docs`
- `http://localhost:8080/redoc`

## Additionally
#### If you want to change database username, password and name change '.env' file