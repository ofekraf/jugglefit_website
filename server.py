import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from backend.utils.google_sheets_trick_suggestions import append_trick_suggestion
from pylib.classes.prop import Prop
from pylib.classes.trick import Trick

# Load environment variables
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/suggest_trick")
async def suggest_trick(request: Request):
    try:
        data = await request.json()
        # Validate required fields
        required_fields = ['name', 'prop', 'props_count', 'difficulty']
        for field in required_fields:
            if field not in data:
                return JSONResponse(content={"error": f"Missing required field: {field}"}, status_code=400)
        # Convert to Trick and Prop objects
        prop = Prop.get_key_by_value(data.get("prop"))
        trick = Trick.from_dict(data)
        append_trick_suggestion(prop=prop, trick=trick)
        return JSONResponse(content={"message": "Suggestion submitted successfully"}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400) 