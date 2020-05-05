import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec

SqlAlchemyBase = dec.declarative_base()

__factory = None


def global_init(db_file):
    global __factory

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("Bad db file name")

    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'
    print(f"Connecting to {conn_str}...")

    engine = sa.create_engine(conn_str, echo=False)  # (echo True == debug)
    __factory = orm.sessionmaker(bind=engine)

    from . import __all_models

    SqlAlchemyBase.metadata.create_all(engine)


def remote_global_init(db_path):
    global __factory

    if __factory:
        return

    conn_str = f'{db_path}?check_same_thread=False'
    print(f"Connecting to {db_path}...")

    engine = sa.create_engine(db_path, echo=False)  # (echo True == debug)
    __factory = orm.sessionmaker(bind=engine)

    from . import __all_models

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()
