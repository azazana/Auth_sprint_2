import click
from flask.cli import FlaskGroup
from werkzeug.security import generate_password_hash
from api import app, db, redis
from api.v1.auth import auth as auth_blueprint
from api.v1.roles import role as role_blueprint
from api.v1.oauth import oauth as oauth_blueprint
from models import User, Role
from utils.partition_user_sign_in import create_partition_year
from utils.ratelimiter import over_limit_multi_lua
from flask import abort

app.register_blueprint(auth_blueprint, url_prefix="/auth/v1")
app.register_blueprint(oauth_blueprint, url_prefix="/auth/v1")
app.register_blueprint(role_blueprint, url_prefix="/auth/v1")
cli = FlaskGroup(app)


@cli.command("create_db")
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()


@cli.command("create_partition_year")
@click.argument('year')
def create_db(year):
    with db.engine.connect() as con:
        create_partition_year(connection=con, year=year)
        con.close()


@cli.command("create_superuser")
def create_superuser():

    role = Role(
        name="admin"
    )
    db.session.add(role)
    db.session.commit()
    user = User(
        name="admin",
        email="admin@admin.ru",
        password=generate_password_hash("admin")
    )
    user.roles = [role]
    db.session.add(user)
    db.session.commit()



# @app.before_request
# def rate_limiter():
#     if over_limit_multi_lua(redis):
#         abort(429, description="Too many requests")


if __name__ == '__main__':
    cli()
