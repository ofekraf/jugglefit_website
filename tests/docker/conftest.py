import pytest
import docker
import requests
import time
import os
import subprocess
import yaml
from pathlib import Path


@pytest.fixture(scope="session")
def docker_client():
    """Docker client fixture for running tests."""
    try:
        return docker.DockerClient.from_env()
    except AttributeError:
        # Fallback for older docker library versions
        return docker.from_env()


@pytest.fixture(scope="session")
def project_root():
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent


@pytest.fixture
def dockerfile_path(project_root):
    """Path to the Dockerfile."""
    return project_root / "Dockerfile"


@pytest.fixture
def docker_compose_dev_path(project_root):
    """Path to development docker-compose.yml."""
    return project_root / "docker-compose.yml"


@pytest.fixture
def docker_compose_prod_path(project_root):
    """Path to production docker-compose.prod.yml."""
    return project_root / "docker-compose.prod.yml"


@pytest.fixture
def env_example_path(project_root):
    """Path to .env.example file."""
    return project_root / ".env.example"


@pytest.fixture
def github_workflow_path(project_root):
    """Path to GitHub Actions workflow."""
    return project_root / ".github" / "workflows" / "deploy.yml"


@pytest.fixture
def oci_deployment_path(project_root):
    """Path to OCI deployment scripts."""
    return project_root / "deploy" / "oci-ubuntu"


def wait_for_healthy_container(container, timeout=60):
    """Wait for container to become healthy."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        container.reload()
        if container.attrs['State']['Health']['Status'] == 'healthy':
            return True
        time.sleep(2)
    return False


def wait_for_service_ready(url, timeout=60):
    """Wait for service to be ready at given URL."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return True
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            pass
        time.sleep(2)
    return False