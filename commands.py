import click
from flask.cli import with_appcontext

from data.db_models import db_session

from data.db_models.submissions import *
from data.db_models.problems import *
from data.db_models.users import *


@click.command(name='create_tables')
@with_appcontext
def create_tables():
    db_session.global_init("data/db/main.sqlite")
