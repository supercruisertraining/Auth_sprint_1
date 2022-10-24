from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


from core.config import config

engine = create_engine(
    f"postgresql://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}",
    connect_args={"options": f"-csearch_path={config.SCHEMAS_SEARCH_ORDER}"},
    echo=True)

from db import models

session_factory = sessionmaker(bind=engine)
