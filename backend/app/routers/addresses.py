import os
import re

import httpx
from fastapi import APIRouter, HTTPException, Query

from app.schemas import UK_POSTCODE, AddressSuggestion

router = APIRouter(prefix="/addresses", tags=["Address lookup"])

GEOAPIFY_URL = "https://api.geoapify.com/v1/geocode/autocomplete"
PHOTON_URL = "https://photon.komoot.io/api/"
UK_BBOX = "-8.7,49.8,1.9,60.9"  # minLon,minLat,maxLon,maxLat
HEADERS = {"User-Agent": "client-onboarding-portal/1.0 (assessment project)"}


def _valid_postcode(value):
    if value and re.match(UK_POSTCODE, value.strip()):
        return value.strip().upper()
    return None


def _build(line1, city, county, postcode, country="United Kingdom"):
    label = ", ".join(p for p in (line1, city, county, postcode, country) if p)
    return AddressSuggestion(
        label=label,
        address_line1=line1 or None,
        address_line2=None,
        city=city or None,
        county=county or None,
        postcode=postcode,
        country=country or "United Kingdom",
    )


def _search_geoapify(q: str, api_key: str) -> list[AddressSuggestion]:
    response = httpx.get(
        GEOAPIFY_URL,
        params={
            "text": q,
            "filter": "countrycode:gb",
            "format": "json",
            "limit": 6,
            "lang": "en",
            "apiKey": api_key,
        },
        headers=HEADERS,
        timeout=8.0,
    )
    response.raise_for_status()
    results = []
    for r in response.json().get("results", []):
        line1 = " ".join(filter(None, [r.get("housenumber"), r.get("street")])).strip()
        results.append(
            _build(
                line1 or r.get("address_line1"),
                r.get("city") or r.get("town") or r.get("village") or r.get("suburb"),
                r.get("county") or r.get("state"),
                _valid_postcode(r.get("postcode")),
                r.get("country") or "United Kingdom",
            )
        )
    return results


def _search_photon(q: str) -> list[AddressSuggestion]:
    response = httpx.get(
        PHOTON_URL,
        params={"q": q, "limit": 10, "lang": "en", "bbox": UK_BBOX},
        headers=HEADERS,
        timeout=8.0,
    )
    response.raise_for_status()
    results, seen = [], set()
    for feature in response.json().get("features", []):
        p = feature.get("properties", {})
        if (p.get("countrycode") or "").upper() != "GB":
            continue
        street = p.get("street")
        if street:
            line1 = " ".join(filter(None, [p.get("housenumber"), street])).strip()
        else:
            line1 = p.get("name")
        item = _build(
            line1,
            p.get("city") or p.get("district") or p.get("locality"),
            p.get("county") or p.get("state"),
            _valid_postcode(p.get("postcode")),
            p.get("country") or "United Kingdom",
        )
        if item.label and item.label not in seen:
            seen.add(item.label)
            results.append(item)
    return results[:6]


@router.get("/search", response_model=list[AddressSuggestion])
def search_addresses(q: str = Query(min_length=3, max_length=200)):
    api_key = os.getenv("GEOAPIFY_API_KEY")
    try:
        if api_key:
            return _search_geoapify(q.strip(), api_key)
        return _search_photon(q.strip())
    except httpx.HTTPStatusError:
        raise HTTPException(status_code=502, detail="Address service rejected the request")
    except httpx.HTTPError:
        raise HTTPException(status_code=502, detail="Address service is unavailable")