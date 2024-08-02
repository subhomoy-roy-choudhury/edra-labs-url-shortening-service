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

# URL Shortened Master Data
MASTER_URL_SHORTEN_DATA = {}

app = FastAPI()


@app.post("/shorten")
async def create_shorten_url(request: Request, data: CreateShortenURLRequest):
    # Base URL
    base_url = str(request.url).split(request.url.path)[0]
    MASTER_URL_SHORTEN_DATA[data.custom_alias] = ShortenedURL(
        alias=data.custom_alias,
        long_url=data.long_url,
        ttl_seconds=data.ttl_seconds,
        created_at=datetime.now(),
    )
    return CreateShortenURLResponse(short_url=f"{base_url}/{data.custom_alias}")


@app.get("/analytics/{alias}")
async def url_analytics(alias: str):
    shortened_url = MASTER_URL_SHORTEN_DATA.get(alias, None)
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
        shortened_url = MASTER_URL_SHORTEN_DATA.get(alias, None)
        if not shortened_url:
            return HTTPException(status_code=404, detail="Alias does not exist")
        elif (
            datetime.now() - shortened_url.created_at
        ).total_seconds() > shortened_url.ttl_seconds:
            del MASTER_URL_SHORTEN_DATA[alias]
            return HTTPException(status_code=404, detail="Alias has expired")
        del MASTER_URL_SHORTEN_DATA[alias]
        MASTER_URL_SHORTEN_DATA[data.custom_alias] = ShortenedURL(
            alias=data.custom_alias,
            long_url=shortened_url.long_url,
            ttl_seconds=data.ttl_seconds,
            created_at=shortened_url.created_at,
        )
        return Response("Successfully updated.", status_code=status.HTTP_200_OK)
    except Exception as _:
        return HTTPException(status_code=400, detail="Invalid request.")


@app.delete("/delete/{alias}")
async def delete_shorten_url(alias: str):
    shortened_url = MASTER_URL_SHORTEN_DATA.get(alias, None)
    if not shortened_url:
        return HTTPException(status_code=404, detail="Alias does not exist")
    elif (
        datetime.now() - shortened_url.created_at
    ).total_seconds() > shortened_url.ttl_seconds:
        del MASTER_URL_SHORTEN_DATA[alias]
        return HTTPException(status_code=404, detail="Alias has expired")
    del MASTER_URL_SHORTEN_DATA[alias]
    return Response("Successfully deleted.", status_code=status.HTTP_200_OK)


@app.get("/{alias}")
async def redirect_url(alias: str):
    shortened_url = MASTER_URL_SHORTEN_DATA.get(alias, None)
    if not shortened_url:
        return HTTPException(status_code=404, detail="Alias does not exist")
    elif (
        datetime.now() - shortened_url.created_at
    ).total_seconds() > shortened_url.ttl_seconds:
        del MASTER_URL_SHORTEN_DATA[alias]
        return HTTPException(status_code=404, detail="Alias has expired")
    shortened_url.access_count += 1
    shortened_url.access_times.append(datetime.now())
    return RedirectResponse(shortened_url.long_url, status_code=status.HTTP_302_FOUND)
