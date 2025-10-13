import fastapi as _fastapi

app = _fastapi.FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "gion"}