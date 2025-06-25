from fastapi import FastAPI

from app.api.v1.routers import user
from app.api.v1.routers import login

app = FastAPI()


@app.get('/api/v1/healthcheck', include_in_schema=False)
def healthcheck():
    return {'status': '200'}

app.include_router(router=user.router, prefix='/api/v1/user')

app.include_router(router=login.router, prefix='/api/v1/login')
