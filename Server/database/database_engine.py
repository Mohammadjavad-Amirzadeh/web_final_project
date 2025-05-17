from sqlalchemy import create_engine, text
from database_model import Base  # Replace with the actual module name where models are defined

db_path = "./../Game_Center.db"  # or use an environment variable if it's configurable

engine = create_engine(f'sqlite:///{db_path}', echo=True)


Base.metadata.create_all(engine)
