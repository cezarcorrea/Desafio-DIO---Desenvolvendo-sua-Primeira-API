from fastapi import FastAPI
from fastapi_pagination import add_pagination, set_page, LimitOffsetPage
from workout_api.routers import api_router 

app = FastAPI(title='WorkoutApi')

set_page(LimitOffsetPage) 
add_pagination(app)       

app.include_router(api_router)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run("workout_api.main:app", host="0.0.0.0", port=8000, reload=True) 