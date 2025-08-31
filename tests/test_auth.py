"""
认证模块测试
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from src.database import get_db, Base
from src.models import User
from src.auth import get_password_hash


# 创建测试数据库
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """覆盖数据库依赖"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    """测试客户端"""
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user():
    """测试用户"""
    db = TestingSessionLocal()
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=get_password_hash("testpass"),
        role="user"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user


def test_register_user(client):
    """测试用户注册"""
    response = client.post("/api/v1/auth/register", json={
        "username": "newuser",
        "email": "new@example.com",
        "password": "newpass123"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["access_token"] is not None
    assert data["user"]["username"] == "newuser"


def test_login_user(client, test_user):
    """测试用户登录"""
    response = client.post("/api/v1/auth/login", json={
        "username": "testuser",
        "password": "testpass"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["access_token"] is not None
    assert data["user"]["username"] == "testuser"


def test_login_invalid_credentials(client):
    """测试无效凭据登录"""
    response = client.post("/api/v1/auth/login", json={
        "username": "wronguser",
        "password": "wrongpass"
    })
    
    assert response.status_code == 401


def test_get_current_user(client, test_user):
    """测试获取当前用户信息"""
    # 先登录获取token
    login_response = client.post("/api/v1/auth/login", json={
        "username": "testuser",
        "password": "testpass"
    })
    token = login_response.json()["access_token"]
    
    # 使用token获取用户信息
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
