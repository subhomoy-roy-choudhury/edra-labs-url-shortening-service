from datetime import datetime
from fastapi import FastAPI, Request, Response, HTTPException, status
from fastapi.responses import RedirectResponse
from models import (
    CreateShortenURLRequest,
    CreateShortenURLResponse,
    ShortenedURL,
    URLAnalyticsResponse,
    UpdateShortenURLRequest,
)
from cache import CacheManager
from utils import random_alias_string

# Constants
ALIAS_NAME_RANDOM_STRING_LENGTH = 20

# Cache Manager
cache_manager = CacheManager()

app = FastAPI()


@app.post("/shorten")
async def create_shorten_url(request: Request, data: CreateShortenURLRequest):
    if not data.custom_alias or data.custom_alias in cache_manager.keys():
        data.custom_alias = random_alias_string(
            ALIAS_NAME_RANDOM_STRING_LENGTH, cache_manager.keys()
        )
    shortened_url = ShortenedURL(
        alias=data.custom_alias,
        long_url=data.long_url,
        ttl_seconds=data.ttl_seconds,
        created_at=datetime.now(),
    )
    cache_manager.set_cache(data.custom_alias, shortened_url, data.ttl_seconds)
    # Base URL
    base_url = str(request.url).split(request.url.path)[0]
    return CreateShortenURLResponse(short_url=f"{base_url}/{data.custom_alias}")


@app.get("/analytics/{alias}")
async def url_analytics(alias: str):
    shortened_url = cache_manager.get_cache(alias)
    if not shortened_url:
        return HTTPException(status_code=404, detail="Alias does not exist")
    return URLAnalyticsResponse(
        alias=shortened_url.alias,
        long_url=shortened_url.long_url,
        access_count=shortened_url.access_count,
        access_times=shortened_url.access_times,
    )


@app.put("/update/{alias}")
async def update_shorten_url(alias: str, data: UpdateShortenURLRequest):
    try:
        shortened_url = cache_manager.get_cache(alias)
        if not shortened_url:
            return HTTPException(
                status_code=404, detail="Alias does not exist or has expired"
            )
        cache_manager.delete_cache(alias)
        cache_manager.set_cache(
            data.custom_alias,
            ShortenedURL(
                alias=data.custom_alias,
                long_url=shortened_url.long_url,
                ttl_seconds=data.ttl_seconds,
                created_at=shortened_url.created_at,
            ),
            data.ttl_seconds,
        )
        return Response("Successfully updated.", status_code=status.HTTP_200_OK)
    except Exception as _:
        return HTTPException(status_code=400, detail="Invalid request.")


@app.delete("/delete/{alias}")
async def delete_shorten_url(alias: str):
    shortened_url = cache_manager.get_cache(alias)
    if not shortened_url:
        return HTTPException(status_code=404, detail="Alias does not exist or has expired")
    cache_manager.delete_cache(alias)
    return Response("Successfully deleted.", status_code=status.HTTP_200_OK)


@app.get("/{alias}")
async def redirect_url(alias: str):
    shortened_url = cache_manager.get_cache(alias)
    if not shortened_url:
        return HTTPException(status_code=404, detail="Alias does not exist or has expired")
    shortened_url.access_count += 1
    shortened_url.access_times.append(datetime.now())
    return RedirectResponse(shortened_url.long_url, status_code=status.HTTP_302_FOUND)
