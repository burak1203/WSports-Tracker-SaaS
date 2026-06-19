import pytest
from fastapi.testclient import TestClient

# "app.main" yerine doğrudan "main" dosyasından import ediyoruz
from main import app 
from app.api.dependencies import get_current_active_user
from app.models.models import User

# Gerçek veritabanı yerine geçecek boş bir obje
class MockUser(User):
    def __init__(self, id, role, company_id=1, target_revenue=0):
        self.id = id
        self.role = role
        self.company_id = company_id
        self.target_revenue = target_revenue
        self.full_name = "Test Kullanicisi"

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_user_override(client):
    def _override_user(role="admin"):
        # FastAPI'nin token doğrulayan fonksiyonunu eziyoruz
        app.dependency_overrides[get_current_active_user] = lambda: MockUser(id=99, role=role)
    
    yield _override_user
    
    # Test bitince override'ı temizle
    app.dependency_overrides.clear()