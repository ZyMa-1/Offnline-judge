import click
from flask.cli import with_appcontext

from data.db_models import db_session

from data.db_models import __all_models


@click.command(name='create_tables')
@with_appcontext
def create_tables():
    db_session.global_init(
        "postgres://rrsdyfbspzkpst:8e22731087e1b644a198fc360e3263c98ff8d22126c850799f7e9d700510895f@ec2-52-202-22-140.compute-1.amazonaws.com:5432/datnhrra0kdml8")
