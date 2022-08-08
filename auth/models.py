from flask_authorize import RestrictionsMixin
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
import uuid
from api import db
from utils.partition_user_sign_in import create_partition


UserGroup = db.Table(
    "user_group",
    db.Model.metadata,
    db.Column("user_id", db.Integer, db.ForeignKey("users.id")),
    db.Column("group_id", db.Integer, db.ForeignKey("groups.id")),
)

UserRole = db.Table(
    "user_role",
    db.Model.metadata,
    db.Column("user_id", db.Integer, db.ForeignKey("users.id")),
    db.Column("role_id", db.Integer, db.ForeignKey("roles.id")),
)


class Group(db.Model, RestrictionsMixin):
    __tablename__ = "groups"
    __table_args__ = {"extend_existing": True}
    __restrictions__ = "*"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)


class Role(db.Model, RestrictionsMixin):
    __tablename__ = "roles"
    __table_args__ = {"extend_existing": True}
    __restrictions__ = "*"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)

    def serialize(self):
        return {
            "name": self.name,
            "id": self.id,
        }


class User(db.Model):
    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(103), nullable=False)
    name = db.Column(db.String(1000))
    roles = db.relationship("Role", secondary=UserRole)
    groups = db.relationship("Group", secondary=UserGroup)

    def __repr__(self):
        return f"<User {self.email}>"

    def serialize(self):
        return {
            "name": self.name,
            "id": self.id,
            "groups": self.groups,
        }


class UserLoginHistory(db.Model):
    __tablename__ = "users_sign_in"
    __table_args__ = (
        UniqueConstraint("id", "datestamp"),
        {
            "postgresql_partition_by": "RANGE (datestamp)",
            "listeners": [("after_create", create_partition)],
        },
    )
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    datestamp = db.Column(db.Date, primary_key=True, server_default=db.func.now())
    user_id = db.Column(db.Integer)
    user_agent = db.Column(db.Text)
