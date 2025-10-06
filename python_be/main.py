from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import router
from bot import run_bot
import asyncio
import logging

logger = logging.getLogger(__name__)
app = FastAPI(title="Fantasy Basketball API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
async def root():
    logger.info("Root endpoint hit")
    logger.debug("Root endpoint hit")
    logger.warning("Root endpoint hit")
    logger.error("Root endpoint hit")
    logger.critical("Root endpoint hit")
    loop = asyncio.get_event_loop()
    loop.create_task(run_bot())
    return {"message": "Fantasy Basketball API is running"}
    

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up the bot")
    loop = asyncio.get_event_loop()
    loop.create_task(run_bot())

if __name__ == "__main__":
    # Start the FastAPI server
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)