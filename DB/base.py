import pwd
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path

engine = create_engine(f'sqlite:///{Path(__file__).parent.resolve()}/settings.db')
Session = sessionmaker(bind=engine)
Base = declarative_base()
