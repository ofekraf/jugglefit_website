from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/suggest_trick")
async def suggest_trick(request: Request):
    try:
        data = await request.json()
        # Here you would process and store the suggestion, e.g., save to a database or Google Sheet
        # For now, just return the received data as a success message
        return JSONResponse(content={"message": "Suggestion submitted successfully", "data": data}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)