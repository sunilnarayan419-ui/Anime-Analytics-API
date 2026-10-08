from pydantic import BaseModel


class GroupProportion(BaseModel):
    group: str
    proportion: float
