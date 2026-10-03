"""
NexaOps Dashboard — Test Suite
Tests for the Flask application endpoints and business logic.
"""

import pytest
import json
import sys
import os

# Add the dashboard directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.main import app, get_services, get_deployments


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestHealthEndpoint:
    """Tests for the /health endpoint."""

    def test_health_returns_200(self, client):
        response = client.get('/health')
        assert response.status_code == 200

    def test_health_returns_json(self, client):
        response = client.get('/health')
        data = json.loads(response.data)
        assert isinstance(data, dict)

    def test_health_has_required_fields(self, client):
        response = client.get('/health')
        data = json.loads(response.data)
        assert 'status' in data
        assert 'version' in data
        assert 'checks' in data

    def test_health_status_is_healthy(self, client):
        response = client.get('/health')
        data = json.loads(response.data)
        assert data['status'] == 'healthy'


class TestServicesEndpoint:
    """Tests for the /api/services endpoint."""

    def test_services_returns_200(self, client):
        response = client.get('/api/services')
        assert response.status_code == 200

    def test_services_returns_list(self, client):
        response = client.get('/api/services')
        data = json.loads(response.data)
        assert isinstance(data, list)

    def test_services_not_empty(self, client):
        response = client.get('/api/services')
        data = json.loads(response.data)
        assert len(data) > 0

    def test_services_have_required_fields(self, client):
        response = client.get('/api/services')
        data = json.loads(response.data)
        for service in data:
            assert 'name' in service
            assert 'status' in service
            assert 'uptime' in service

    def test_services_status_values_are_valid(self, client):
        response = client.get('/api/services')
        data = json.loads(response.data)
        valid_statuses = {'operational', 'degraded', 'outage'}
        for service in data:
            assert service['status'] in valid_statuses


class TestDeploymentsEndpoint:
    """Tests for the /api/deployments endpoint."""

    def test_deployments_returns_200(self, client):
        response = client.get('/api/deployments')
        assert response.status_code == 200

    def test_deployments_returns_list(self, client):
        response = client.get('/api/deployments')
        data = json.loads(response.data)
        assert isinstance(data, list)

    def test_deployments_have_required_fields(self, client):
        response = client.get('/api/deployments')
        data = json.loads(response.data)
        for deployment in data:
            assert 'service' in deployment
            assert 'version' in deployment
            assert 'status' in deployment
            assert 'deployed_by' in deployment


class TestIndexEndpoint:
    """Tests for the main dashboard page."""

    def test_index_returns_200(self, client):
        response = client.get('/')
        assert response.status_code == 200

    def test_index_returns_html(self, client):
        response = client.get('/')
        assert b'NexaOps' in response.data

    def test_index_contains_services(self, client):
        response = client.get('/')
        assert b'Service Status' in response.data


class TestBusinessLogic:
    """Tests for core business logic functions."""

    def test_get_services_returns_list(self):
        services = get_services()
        assert isinstance(services, list)
        assert len(services) >= 1

    def test_get_deployments_returns_list(self):
        deployments = get_deployments()
        assert isinstance(deployments, list)
        assert len(deployments) >= 1
