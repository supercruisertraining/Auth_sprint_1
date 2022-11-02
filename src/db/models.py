import uuid

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Role(Base):
    __tablename__ = "roles"
    __table_args__ = {"schema": "auth"}
    role_name = Column(String, primary_key=True)


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "auth"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    first_name = Column(String, nullable=True, default=None)
    last_name = Column(String, nullable=True, default=None)
    role = Column(String, ForeignKey(Role.role_name, ondelete="SET NULL"), nullable=True)

    def __repr__(self):
        return f"<User {self.username}>"


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
