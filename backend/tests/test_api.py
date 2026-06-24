"""Tests for API endpoints."""
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

client = TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_root_endpoint(self):
        """Test root endpoint returns API info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert data["version"] == "3.3.0"
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestTaxEndpoints:
    """Test tax calculation endpoints."""
    
    def test_list_taxes(self):
        """Test listing available taxes."""
        response = client.get("/api/v1/taxes")
        assert response.status_code == 200
        data = response.json()
        assert "taxes" in data
        assert len(data["taxes"]) > 0
    
    def test_calculate_commercial_tax(self):
        """Test commercial tax calculation."""
        payload = {
            "amount": 100000,
            "tax_type": "commercial"
        }
        response = client.post("/api/v1/tax/calculate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["original_amount"] == 100000
        assert data["tax_rate"] == 0.02
        assert data["tax_amount"] == 2000
        assert data["total_amount"] == 102000
    
    def test_calculate_income_tax(self):
        """Test individual income tax calculation."""
        payload = {
            "amount": 500000,
            "tax_type": "income_individual"
        }
        response = client.post("/api/v1/tax/calculate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["tax_rate"] == 0.05
        assert data["tax_amount"] == 25000
    
    def test_invalid_tax_type(self):
        """Test error handling for invalid tax type."""
        payload = {
            "amount": 100000,
            "tax_type": "invalid_tax"
        }
        response = client.post("/api/v1/tax/calculate", json=payload)
        assert response.status_code == 400


class TestTownshipEndpoints:
    """Test township endpoints."""
    
    def test_list_all_townships(self):
        """Test listing all townships."""
        response = client.get("/api/v1/townships")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_get_township_by_name(self):
        """Test getting specific township."""
        response = client.get("/api/v1/townships/Yangon")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Yangon"
        assert "state_region" in data
    
    def test_township_not_found(self):
        """Test 404 for non-existent township."""
        response = client.get("/api/v1/townships/NonExistent")
        assert response.status_code == 404
    
    def test_search_townships(self):
        """Test searching townships."""
        response = client.get("/api/v1/townships?search=man")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        # Should find Mandalay
        names = [t["name"].lower() for t in data]
        assert any("man" in name for name in names)


class TestDeliveryEndpoints:
    """Test delivery calculation endpoints."""
    
    def test_calculate_delivery_same_region(self):
        """Test delivery within same region."""
        payload = {
            "from_township": "Yangon",
            "to_township": "Mandalay",
            "weight_kg": 5.0
        }
        response = client.post("/api/v1/delivery/calculate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["from_township"] == "Yangon"
        assert data["to_township"] == "Mandalay"
        assert data["total_cost"] > 0
        assert data["estimated_days"] >= 1
    
    def test_delivery_invalid_origin(self):
        """Test error for invalid origin township."""
        payload = {
            "from_township": "InvalidTown",
            "to_township": "Yangon",
            "weight_kg": 2.0
        }
        response = client.post("/api/v1/delivery/calculate", json=payload)
        assert response.status_code == 404
    
    def test_delivery_invalid_destination(self):
        """Test error for invalid destination township."""
        payload = {
            "from_township": "Yangon",
            "to_township": "InvalidTown",
            "weight_kg": 2.0
        }
        response = client.post("/api/v1/delivery/calculate", json=payload)
        assert response.status_code == 404
