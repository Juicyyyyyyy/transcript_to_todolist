# from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from routes.api import router
from config.logging_config import setup_logging


# load_dotenv()

logger = setup_logging()
logger.info("Starting Reunion to Code API")

app = FastAPI(
    title="Reunion to Code API",
    description="Transform meeting transcripts into actionable technical todos",
    version="1.0.0"
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(router)

@app.get("/")
async def read_root():
    return FileResponse("static/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)