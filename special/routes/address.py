import requests
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status, Response

from db import get_db


from ..models.address import Address
from ..models.schema import Address as address_schema

address_router = APIRouter(
    tags=["Address"],
    prefix='/address'
)

# 6dyDBz1Eaf2Mtb2RbuBSM7pgxhqVvFLk


def get_coordinates(user_address, city, state):
    _url = (
        u'http://www.mapquestapi.com/geocoding/v1/'
        u'address?key={api_key}&location={user_address},{city},{state}'
    ).format(
        api_key="6dyDBz1Eaf2Mtb2RbuBSM7pgxhqVvFLk",  # Need to store key in Env
        user_address=user_address,
        city=city,
        state=state
    )
    _response = requests.get(_url)
    location_coordinates = _response.json().get(
        "results", [])[0].get("locations", [])[0]
    return location_coordinates


@address_router.post("/createAddress", status_code=status.HTTP_201_CREATED)
def create_address(req: address_schema, res: Response, db: Session = Depends(get_db)):
    try:
        user_address = req.user_address.strip()
        user_name = req.user_name
        city = req.city.strip()
        state = req.state.strip()
        postal_code = req.postal_code
        if not any([user_address, user_name, city, state]):
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Missing Keys!"
            )

        location_coordinates = get_coordinates(user_address, city, state)

        instance = Address(
            user_address=user_address,
            user_name=user_name,
            city=city,
            state=state,
            country=location_coordinates.get("adminArea1"),
            postal_code=postal_code,
            longitude=location_coordinates.get("latLng", {}).get("lng", ""),
            latitude=location_coordinates.get("latLng", {}).get("lat", ""),
            mapUrl=location_coordinates.get("mapUrl", "")
        )

        db.add(instance)
        db.commit()
        db.refresh(instance)

        return {
            "status": "Created New Address",
            "data": instance
        }

    except Exception as e:
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "status": "failed"
        }
