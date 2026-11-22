import os
import re
from urllib.parse import quote

import httpx
from fastapi import APIRouter, HTTPException, Query

from app.schemas import AddressSuggestion, UK_POSTCODE

router = APIRouter(prefix="/addresses", tags=["Address lookup"])

BASE_URL = "https://api.ideal-postcodes.co.uk/v1/postcodes"


@router.get("/search", response_model=list[AddressSuggestion])
def search_addresses(q: str = Query(min_length=3, max_length=20)):
    api_key = os.getenv("ADDRESS_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="Address lookup is not configured")

    postcode = q.strip().upper()
    if not re.match(UK_POSTCODE, postcode):
        raise HTTPException(status_code=422, detail="Enter a full UK postcode, e.g. SW1A 1AA")

    try:
        response = httpx.get(
            f"{BASE_URL}/{quote(postcode)}",
            params={"api_key": api_key},
            timeout=8.0,
        )
    except httpx.HTTPError:
        raise HTTPException(status_code=502, detail="Address service is unavailable")

    if response.status_code == 404:
        return []
    if response.status_code in (401, 402, 403):
        raise HTTPException(
            status_code=502,
            detail="Address service rejected the API key or the lookup limit was reached",
        )
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="Address service returned an error")

    suggestions = []
    for r in response.json().get("result", []):
        parts = [p for p in (r.get("line_1"), r.get("line_2"), r.get("line_3")) if p]
        town = r.get("post_town")
        code = r.get("postcode") or postcode
        suggestions.append(
            AddressSuggestion(
                label=", ".join(parts + [p for p in (town, code) if p]),
                address_line1=r.get("line_1") or None,
                address_line2=", ".join(p for p in (r.get("line_2"), r.get("line_3")) if p) or None,
                city=town or None,
                county=r.get("county") or None,
                postcode=code,
                country="United Kingdom",
            )
        )
    return suggestions