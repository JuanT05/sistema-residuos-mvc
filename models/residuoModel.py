from datetime import date

from sqlmodel import (
    SQLModel,
    Field
)


class Residuo(SQLModel, table=True):

    id: int = Field(primary_key=True)

    tipo_residuo: str

    peso: float

    bonificacion_kilo: float

    total_bonificacion: float

    fecha: date
  