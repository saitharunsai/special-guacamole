import uvicorn
from fastapi import FastAPI
from starlette.responses import RedirectResponse

from special.routes.address import address_router
from special.models.address import Address
from db import engine

app = FastAPI()

Address.metadata.create_all(bind=engine)


@app.get("/")
def main():
    return RedirectResponse(url="/docs/")


app.include_router(address_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
