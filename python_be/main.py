from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import router
import uvicorn
import threading
from bot import run_bot  # Import the function to start the bot


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
    return {"message": "Fantasy Basketball API is running"}

def start_bot():
    run_bot()

if __name__ == "__main__":
    # Start the Discord bot in a separate thread
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.start()

    # Start the FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8000)