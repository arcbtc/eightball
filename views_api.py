from http import HTTPStatus
import json

import httpx
from fastapi import Depends, Query, Request
from lnurl import decode as decode_lnurl
from loguru import logger
from starlette.exceptions import HTTPException

from lnbits.core.crud import get_user
from lnbits.core.models import Payment
from lnbits.core.services import create_invoice
from lnbits.core.views.api import api_payment
from lnbits.decorators import (
    WalletTypeInfo,
    check_admin,
    get_key_type,
    require_admin_key,
    require_invoice_key,
)

from . import eightballl_ext
from .crud import (
    create_eightballl,
    update_eightballl,
    delete_eightballl,
    get_eightballl,
    get_eightballls,
)
from .models import CreateEightBallData


#######################################
##### ADD YOUR API ENDPOINTS HERE #####
#######################################

## Get all the records belonging to the user


@eightballl_ext.get("/api/v1/eightb", status_code=HTTPStatus.OK)
async def api_eightballls(
    req: Request,
    all_wallets: bool = Query(False),
    wallet: WalletTypeInfo = Depends(get_key_type),
):
    wallet_ids = [wallet.wallet.id]
    if all_wallets:
        user = await get_user(wallet.wallet.user)
        wallet_ids = user.wallet_ids if user else []
    return [
        eightballl.dict() for eightballl in await get_eightballls(wallet_ids, req)
    ]


## Get a single record


@eightballl_ext.get("/api/v1/eightb/{eightballl_id}", status_code=HTTPStatus.OK)
async def api_eightballl(
    req: Request, eightballl_id: str, WalletTypeInfo=Depends(get_key_type)
):
    eightballl = await get_eightballl(eightballl_id, req)
    if not eightballl:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="EightBall does not exist."
        )
    return eightballl.dict()


## update a record


@eightballl_ext.put("/api/v1/eightb/{eightballl_id}")
async def api_eightballl_update(
    req: Request,
    data: CreateEightBallData,
    eightballl_id: str,
    wallet: WalletTypeInfo = Depends(get_key_type),
):
    if not eightballl_id:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="EightBall does not exist."
        )
    eightballl = await get_eightballl(eightballl_id, req)
    assert eightballl, "EightBall couldn't be retrieved"

    if wallet.wallet.id != eightballl.wallet:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="Not your EightBall."
        )
    eightballl = await update_eightballl(
        eightballl_id=eightballl_id, **data.dict(), req=req
    )
    return eightballl.dict()


## Create a new record


@eightballl_ext.post("/api/v1/eightb", status_code=HTTPStatus.CREATED)
async def api_eightballl_create(
    req: Request,
    data: CreateEightBallData,
    wallet: WalletTypeInfo = Depends(require_admin_key),
):
    eightballl = await create_eightballl(
        wallet_id=wallet.wallet.id, data=data, req=req
    )
    return eightballl.dict()


## Delete a record


@eightballl_ext.delete("/api/v1/eightb/{eightballl_id}")
async def api_eightballl_delete(
    eightballl_id: str, wallet: WalletTypeInfo = Depends(require_admin_key)
):
    eightballl = await get_eightballl(eightballl_id)

    if not eightballl:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="EightBall does not exist."
        )

    if eightballl.wallet != wallet.wallet.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="Not your EightBall."
        )

    await delete_eightballl(eightballl_id)
    return "", HTTPStatus.NO_CONTENT