from http import HTTPStatus

from fastapi import Depends, Request
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException
from starlette.responses import HTMLResponse

from lnbits.core.models import User
from lnbits.decorators import check_user_exists
from lnbits.settings import settings

from . import eightballl_ext, eightballl_renderer
from .crud import get_eightballl

eightb = Jinja2Templates(directory="eightb")


#######################################
##### ADD YOUR PAGE ENDPOINTS HERE ####
#######################################


# Backend admin page


@eightballl_ext.get("/", response_class=HTMLResponse)
async def index(request: Request, user: User = Depends(check_user_exists)):
    return eightballl_renderer().TemplateResponse(
        "eightballl/index.html", {"request": request, "user": user.dict()}
    )


# Frontend shareable page


@eightballl_ext.get("/{eightballl_id}")
async def eightballl(request: Request, eightballl_id):
    eightballl = await get_eightballl(eightballl_id, request)
    if not eightballl:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="EightBall does not exist."
        )
    return eightballl_renderer().TemplateResponse(
        "eightballl/eightballl.html",
        {
            "request": request,
            "eightballl_id": eightballl_id,
            "lnurlpay": eightballl.lnurlpay,
            "web_manifest": f"/eightballl/manifest/{eightballl_id}.webmanifest",
        },
    )


# Manifest for public page, customise or remove manifest completely


@eightballl_ext.get("/manifest/{eightballl_id}.webmanifest")
async def manifest(eightballl_id: str):
    eightballl = await get_eightballl(eightballl_id)
    if not eightballl:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="EightBall does not exist."
        )

    return {
        "short_name": settings.lnbits_site_title,
        "name": eightballl.name + " - " + settings.lnbits_site_title,
        "icons": [
            {
                "src": settings.lnbits_custom_logo
                if settings.lnbits_custom_logo
                else "https://cdn.jsdelivr.net/gh/lnbits/lnbits@0.3.0/docs/logos/lnbits.png",
                "type": "image/png",
                "sizes": "900x900",
            }
        ],
        "start_url": "/eightballl/" + eightballl_id,
        "background_color": "#1F2234",
        "description": "Minimal extension to build on",
        "display": "standalone",
        "scope": "/eightballl/" + eightballl_id,
        "theme_color": "#1F2234",
        "shortcuts": [
            {
                "name": eightballl.name + " - " + settings.lnbits_site_title,
                "short_name": eightballl.name,
                "description": eightballl.name + " - " + settings.lnbits_site_title,
                "url": "/eightballl/" + eightballl_id,
            }
        ],
    }
