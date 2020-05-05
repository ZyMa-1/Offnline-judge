import click
from flask.cli import with_appcontext
from data.db_models import db_session

from data.db_models.problems import *


@click.command(name='create_tables')
@with_appcontext
def create_tables():
    db_session.global_init("data/db/main.sqlite")
    session = db_session.create_session()
    problem1 = Problem(
        id=1,
        title="A+B",
        time_limit=1.0,
        memory_limit=64,
        theme="basic_programming"
    )
    problem2 = Problem(
        id=3,
        title="Factorization",
        time_limit=1.0,
        memory_limit=64,
        theme="basic_programming"
    )
    problem3 = Problem(
        id=2,
        title="A+B",
        time_limit=1.0,
        memory_limit=64,
        theme="data_structures"
    )
    session.add(problem1)
    session.add(problem2)
    session.add(problem3)
    session.commit()
