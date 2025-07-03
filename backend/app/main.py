from fastapi import FastAPI

from app.api.v1.routers import user
from app.api.v1.routers import login

app = FastAPI(docs_url='/api/v1/docs')


@app.get('/', include_in_schema=False)
async def root():
    return {'message': 'Root page'}

@app.get('/api/v1/healthcheck', include_in_schema=False)
async def healthcheck():
    return {'status': '200'}

app.include_router(router=user.router, prefix='/api/v1/user')

app.include_router(router=login.router, prefix='/api/v1/login')
