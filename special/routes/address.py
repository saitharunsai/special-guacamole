import requests
from typing import Union
from sqlalchemy.orm import Session
from geopy.distance import geodesic
from fastapi import APIRouter, Depends, HTTPException, status, Response

from db import get_db
from ..models.address import Address
from ..models.schema import Address as address_schema

address_router = APIRouter(
    tags=["Address"],
    prefix='/address'
)


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


@address_router.get("/all", status_code=status.HTTP_200_OK)
def get_all_address(res: Response, db: Session = Depends(get_db)):
    try:
        return {
            "address": db.query(Address).all()
        }
    except:
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "msg": "Failed To Fetch Address !!"
        }


@address_router.post("/create", status_code=status.HTTP_201_CREATED)
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
            latitude=location_coordinates.get("latLng", {}).get("lat", "")
        )

        db.add(instance)
        db.commit()
        db.refresh(instance)

        return {
            "status": "Created New Address",
            "instance": instance
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@address_router.get("/find", status_code=status.HTTP_200_OK)
def get_nearest_address(res: Response, user_address: str, city: str, state: str, db: Session = Depends(get_db)):
    '''
        :params str user_address
        :params str city
        :params str state

        Api to Fetch the Near by Address for the given user
    '''
    try:
        location_coordinates = get_coordinates(user_address, city, state)
        query_coordinates = location_coordinates.get("latLng")

        first_coordinates = (query_coordinates.get(
            "lat"), query_coordinates.get("lng"))

        _all_address = db.query(Address).all()
        reqAddress = [
            address if geodesic(
                first_coordinates, (address.latitude, address.longitude)).km <= 100 else []
            for address in _all_address
        ]
        return {
            "instance": reqAddress
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@address_router.put("/update/{pk}", status_code=status.HTTP_202_ACCEPTED)
def update_address(pk: Union[int, str], req: address_schema, res: Response, db: Session = Depends(get_db)):
    '''
        :params int pk refers to Id in the Address Table
        Api to Update The address
    '''
    try:

        if not pk:
            raise Exception("Id is Missing")

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

        new_address = {
            "user_address": user_address,
            "user_name": user_name,
            "city": city,
            "state": state,
            "country": location_coordinates.get("adminArea1", ""),
            "postal_code": postal_code,
            "longitude":  location_coordinates.get("latLng", {}).get("lng", ""),
            "latitude":  location_coordinates.get("latLng", {}).get("lat", "")
        }

        _update_instance = db.query(Address).filter(
            Address.id == pk).update(new_address)

        if not _update_instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Address id {pk} not found"
            )
        db.commit()

        return {
            "instance": _update_instance
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@address_router.delete("/delete/{pk}", status_code=status.HTTP_202_ACCEPTED)
def delete_address(pk: Union[int, str], res: Response, db: Session = Depends(get_db)):
    '''
        :params int pk refers to Id in the Address Table
        Api to Delete The address
    '''
    try:
        if not pk:
            raise Exception("Id is Missing")

        _removed_address = db.query(Address).filter(
            Address.id == pk).delete(synchronize_session=False)

        if not _removed_address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Address id {pk} not found"
            )

        db.commit()
        return {
            "instance": _removed_address
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
