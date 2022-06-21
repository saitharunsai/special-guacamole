from pydantic import BaseModel


class Address(BaseModel):
    '''
       pydantic allows us to allow custom dataTypes 
    '''
    user_address: str
    user_name: str
    city: str
    state: str
    postal_code: int
