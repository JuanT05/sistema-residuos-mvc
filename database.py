from sqlmodel import SQLModel, create_engine

postgres_url = "postgresql://postgres:postgres123@localhost/postgres"

engine = create_engine(
    postgres_url,
    echo=True
)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)