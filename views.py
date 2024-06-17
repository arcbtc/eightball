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
        "eightball/index.html", {"request": request, "user": user.dict()}
    )


# Frontend shareable page


@eightballl_ext.get("/{eightballl_id}")
async def eightball(request: Request, eightballl_id):
    eightball = await get_eightballl(eightballl_id, request)
    if not eightball:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="EightBall does not exist."
        )
    return eightballl_renderer().TemplateResponse(
        "eightball/eightball.html",
        {
            "request": request,
            "eightballl_id": eightballl_id,
            "lnurlpay": eightball.lnurlpay,
            "web_manifest": f"/eightball/manifest/{eightballl_id}.webmanifest",
        },
    )


# Manifest for public page, customise or remove manifest completely


@eightballl_ext.get("/manifest/{eightballl_id}.webmanifest")
async def manifest(eightballl_id: str):
    eightball = await get_eightballl(eightballl_id)
    if not eightball:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="EightBall does not exist."
        )

    return {
        "short_name": settings.lnbits_site_title,
        "name": eightball.name + " - " + settings.lnbits_site_title,
        "icons": [
            {
                "src": settings.lnbits_custom_logo
                if settings.lnbits_custom_logo
                else "https://cdn.jsdelivr.net/gh/lnbits/lnbits@0.3.0/docs/logos/lnbits.png",
                "type": "image/png",
                "sizes": "900x900",
            }
        ],
        "start_url": "/eightball/" + eightballl_id,
        "background_color": "#1F2234",
        "description": "Minimal extension to build on",
        "display": "standalone",
        "scope": "/eightball/" + eightballl_id,
        "theme_color": "#1F2234",
        "shortcuts": [
            {
                "name": eightball.name + " - " + settings.lnbits_site_title,
                "short_name": eightball.name,
                "description": eightball.name + " - " + settings.lnbits_site_title,
                "url": "/eightball/" + eightballl_id,
            }
        ],
    }
