import uuid

from sqlalchemy import Column, UniqueConstraint, String, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Role(Base):
    __tablename__ = "roles"
    __table_args__ = {"schema": "auth"}
    role_name = Column(String, primary_key=True)
    description = Column(String, nullable=True)
    position = Column(Integer, unique=True, nullable=False)


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "auth"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    first_name = Column(String, nullable=True, default=None)
    last_name = Column(String, nullable=True, default=None)
    email = Column(String, nullable=True, default=None)
    role = Column(String, ForeignKey(Role.role_name, ondelete="SET NULL"), nullable=True)

    def __repr__(self):
        return f"<User {self.username}>"


class Password(Base):
    __tablename__ = "password"
    __table_args__ = {"schema": "auth"}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey(User.id, ondelete="CASCADE"),  unique=True)
    password = Column(String, nullable=False)


class SocialUserId(Base):
    __tablename__ = "social_user_id"
    __table_args__ = {"schema": "auth"}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey(User.id, ondelete="CASCADE"))
    social_id = Column(String, unique=True, nullable=False)
    UniqueConstraint("user_id", "social_id", name='user_id_social_id_uniq')


class UserAdmin(Base):
    __tablename__ = "admin_users"
    __table_args__ = {"schema": "auth"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    first_name = Column(String, nullable=True, default=None)
    last_name = Column(String, nullable=True, default=None)

    def __repr__(self):
        return f"<SuperUser {self.username}>"


class LoginStat(Base):
    __tablename__ = "login_stat"
    __table_args__ = {"schema": "auth"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey(User.id, ondelete="CASCADE"))
    ip = Column(String, default=None, nullable=True)
    os = Column(String, default=None, nullable=True)
    browser = Column(String, default=None, nullable=True)
    device = Column(String, default=None, nullable=True)
    created_at_utc = Column(DateTime, nullable=False)
