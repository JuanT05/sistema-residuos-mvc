from datetime import date

from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from contextlib import asynccontextmanager

from sqlmodel import Field, Session, SQLModel, create_engine, select


# MODELO
class Residuo(SQLModel, table=True):
    id: int = Field(primary_key=True)
    tipo_residuo: str
    peso: float
    bonificacion_kilo: float
    total_bonificacion: float
    fecha: date


# CONEXIÓN POSTGRES
postgres_url = "postgresql://postgres:postgres123@localhost/postgres"

engine = create_engine(postgres_url, echo=True)


# REGLAS DE BONIFICACIÓN
def calcular_bonificacion(peso):

    if peso <= 10:
        return 200

    elif peso <= 20:
        return 300

    else:
        return 400


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


# LISTAR REGISTROS
@app.get("/", response_class=HTMLResponse)
async def read_residuos(request: Request):

    with Session(engine) as session:

        residuos = session.exec(select(Residuo)).all()

        return templates.TemplateResponse(
            "residuos.html",
            {
                "request": request,
                "residuos": residuos
            }
        )


# LISTA JSON
@app.get("/lista")
def leer_residuos():

    with Session(engine) as session:

        residuos = session.exec(select(Residuo)).all()

        return {"residuos": residuos}


# BUSCAR POR ID
@app.get("/residuo/{id}")
def buscar_residuo(id: int):

    with Session(engine) as session:

        residuo = session.get(Residuo, id)

        if not residuo:
            raise HTTPException(
                status_code=404,
                detail="Registro no encontrado"
            )

        return residuo


# AGREGAR
@app.post("/agregar")
async def agregar_residuo(
    id: int = Form(...),
    tipo_residuo: str = Form(...),
    peso: float = Form(...),
    fecha: date = Form(...)
):

    if tipo_residuo not in ["Organico", "Inorganico"]:
        raise HTTPException(
            status_code=400,
            detail="Tipo de residuo inválido"
        )

    bonificacion_kilo = calcular_bonificacion(peso)

    total_bonificacion = peso * bonificacion_kilo

    with Session(engine) as session:

        existe = session.get(Residuo, id)

        if existe:
            raise HTTPException(
                status_code=400,
                detail="Ya existe un registro con ese ID"
            )

        nuevo = Residuo(
            id=id,
            tipo_residuo=tipo_residuo,
            peso=peso,
            bonificacion_kilo=bonificacion_kilo,
            total_bonificacion=total_bonificacion,
            fecha=fecha
        )

        session.add(nuevo)

        session.commit()

    return RedirectResponse(
        url="/",
        status_code=303
    )


# ACTUALIZAR
@app.post("/actualizar/{id}")
async def actualizar_residuo(
    id: int,
    tipo_residuo: str = Form(...),
    peso: float = Form(...),
    fecha: date = Form(...)
):

    if tipo_residuo not in ["Organico", "Inorganico"]:
        raise HTTPException(
            status_code=400,
            detail="Tipo de residuo inválido"
        )

    with Session(engine) as session:

        residuo = session.get(Residuo, id)

        if not residuo:
            raise HTTPException(
                status_code=404,
                detail="Registro no encontrado"
            )

        bonificacion_kilo = calcular_bonificacion(peso)

        residuo.tipo_residuo = tipo_residuo
        residuo.peso = peso
        residuo.bonificacion_kilo = bonificacion_kilo
        residuo.total_bonificacion = peso * bonificacion_kilo
        residuo.fecha = fecha

        session.add(residuo)

        session.commit()

    return RedirectResponse(
        url="/",
        status_code=303
    )


# ELIMINAR
@app.post("/eliminar/{id}")
async def eliminar_residuo(id: int):

    with Session(engine) as session:

        residuo = session.get(Residuo, id)

        if not residuo:
            raise HTTPException(
                status_code=404,
                detail="Registro no encontrado"
            )

        session.delete(residuo)

        session.commit()

    return RedirectResponse(
        url="/",
        status_code=303
    )