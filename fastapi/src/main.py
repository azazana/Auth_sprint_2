import logging
import aioredis
import uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1 import films, genres, persons
from core.config import settings
from core.logger import LOGGING
from db import elastic, redis
from models.enums import URLIndexName

app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)


@app.on_event("startup")
async def startup():
    redis.redis = aioredis.from_url(
        url=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"
    )
    elastic.es = AsyncElasticsearch(
        hosts=[f"{settings.ELASTIC_HOST}:{settings.ELASTIC_PORT}"]
    )


@app.on_event("shutdown")
async def shutdown():
    async with redis.redis.client() as conn:
        await conn.close()
        await conn.connection_pool.disconnect()
    await elastic.es.close()


app.include_router(films.router,
                   prefix=f"/api/v1/{URLIndexName.film.value}",
                   tags=["films"])
app.include_router(genres.router,
                   prefix=f"/api/v1/{URLIndexName.genre.value}",
                   tags=["genres"])
app.include_router(persons.router,
                   prefix=f"/api/v1/{URLIndexName.person.value}",
                   tags=["persons"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
