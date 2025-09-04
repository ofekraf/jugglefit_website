import pytest
import docker
import os
import re
from pathlib import Path


class TestDockerfileStructure:
    """Test Dockerfile structure and best practices."""
    
    def test_dockerfile_exists(self, dockerfile_path):
        """Test that Dockerfile exists."""
        assert dockerfile_path.exists(), "Dockerfile should exist"
    
    def test_dockerfile_single_from_statement(self, dockerfile_path):
        """Test that Dockerfile has only one FROM statement (no duplicate)."""
        content = dockerfile_path.read_text()
        from_statements = re.findall(r'^FROM\s+', content, re.MULTILINE)
        assert len(from_statements) == 1, f"Expected 1 FROM statement, found {len(from_statements)}"
    
    def test_dockerfile_uses_python_slim(self, dockerfile_path):
        """Test that Dockerfile uses Python slim image for size optimization."""
        content = dockerfile_path.read_text()
        assert "python:" in content.lower(), "Dockerfile should use Python base image"
        assert "slim" in content.lower(), "Dockerfile should use slim variant for size optimization"
    
    def test_dockerfile_has_healthcheck(self, dockerfile_path):
        """Test that Dockerfile includes health check."""
        content = dockerfile_path.read_text()
        assert "HEALTHCHECK" in content, "Dockerfile should include HEALTHCHECK instruction"
    
    def test_dockerfile_uses_non_root_user(self, dockerfile_path):
        """Test that Dockerfile creates and uses non-root user for security."""
        content = dockerfile_path.read_text()
        assert "USER" in content and "root" not in content.split("USER")[-1], "Dockerfile should use non-root user"
        assert "RUN adduser" in content or "RUN useradd" in content or "RUN groupadd" in content, "Dockerfile should create non-root user"
    
    def test_dockerfile_optimized_layer_caching(self, dockerfile_path):
        """Test that Dockerfile is optimized for layer caching."""
        content = dockerfile_path.read_text()
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        # Check that requirements.txt is copied before the rest of the app
        copy_requirements_idx = None
        copy_app_idx = None
        
        for i, line in enumerate(lines):
            if "COPY requirements.txt" in line:
                copy_requirements_idx = i
            elif "COPY . ." in line:
                copy_app_idx = i
        
        assert copy_requirements_idx is not None, "Should copy requirements.txt separately"
        assert copy_app_idx is not None, "Should copy app files"
        assert copy_requirements_idx < copy_app_idx, "requirements.txt should be copied before app files for layer caching"
    
    def test_dockerfile_sets_workdir(self, dockerfile_path):
        """Test that Dockerfile sets working directory."""
        content = dockerfile_path.read_text()
        assert "WORKDIR" in content, "Dockerfile should set WORKDIR"
    
    def test_dockerfile_sets_environment_variables(self, dockerfile_path):
        """Test that Dockerfile sets required environment variables."""
        content = dockerfile_path.read_text()
        assert "PYTHONDONTWRITEBYTECODE" in content, "Should set PYTHONDONTWRITEBYTECODE=1"
        assert "PYTHONUNBUFFERED" in content, "Should set PYTHONUNBUFFERED=1"
    
    def test_dockerfile_exposes_port(self, dockerfile_path):
        """Test that Dockerfile exposes the correct port."""
        content = dockerfile_path.read_text()
        assert "EXPOSE" in content, "Dockerfile should expose port"
        assert "5001" in content, "Should expose port 5001"


class TestDockerBuild:
    """Test Docker image building."""
    
    def test_docker_image_builds_successfully(self, docker_client, project_root):
        """Test that Docker image builds without errors."""
        try:
            image, logs = docker_client.images.build(
                path=str(project_root),
                tag="jugglefit-test:latest",
                rm=True,
                forcerm=True
            )
            assert image is not None, "Docker image should build successfully"
        except docker.errors.BuildError as e:
            pytest.fail(f"Docker build failed: {e}")
    
    def test_docker_image_size_optimized(self, docker_client, project_root):
        """Test that Docker image size is reasonable (under 500MB)."""
        image, _ = docker_client.images.build(
            path=str(project_root),
            tag="jugglefit-test:latest",
            rm=True,
            forcerm=True
        )
        
        size_mb = image.attrs['Size'] / (1024 * 1024)
        assert size_mb < 500, f"Image size {size_mb:.1f}MB should be under 500MB"
    
    def test_docker_container_starts_successfully(self, docker_client, project_root):
        """Test that Docker container starts without errors."""
        # Build image first
        image, _ = docker_client.images.build(
            path=str(project_root),
            tag="jugglefit-test:latest",
            rm=True,
            forcerm=True
        )
        
        # Start container
        container = docker_client.containers.run(
            "jugglefit-test:latest",
            detach=True,
            ports={'5001/tcp': None},
            environment={
                'FLASK_ENV': 'production'
            }
        )
        
        try:
            # Wait a bit for startup
            import time
            time.sleep(5)
            
            container.reload()
            assert container.status in ['running'], f"Container should be running, status: {container.status}"
            
            # Check logs for errors
            logs = container.logs().decode('utf-8')
            assert "error" not in logs.lower() or "traceback" not in logs.lower(), f"Container logs should not contain errors: {logs}"
            
        finally:
            container.stop()
            container.remove()
    
    def test_docker_container_health_check_passes(self, docker_client, project_root):
        """Test that Docker container passes health checks."""
        # This test will fail until we implement proper health checks
        image, _ = docker_client.images.build(
            path=str(project_root),
            tag="jugglefit-test:latest",
            rm=True,
            forcerm=True
        )
        
        container = docker_client.containers.run(
            "jugglefit-test:latest",
            detach=True,
            ports={'5001/tcp': None}
        )
        
        try:
            # Wait for health check to pass
            from tests.docker.conftest import wait_for_healthy_container
            is_healthy = wait_for_healthy_container(container, timeout=30)
            assert is_healthy, "Container health check should pass"
            
        finally:
            container.stop()
            container.remove()
    
    def test_docker_container_runs_as_non_root(self, docker_client, project_root):
        """Test that Docker container runs as non-root user."""
        image, _ = docker_client.images.build(
            path=str(project_root),
            tag="jugglefit-test:latest",
            rm=True,
            forcerm=True
        )
        
        container = docker_client.containers.run(
            "jugglefit-test:latest",
            command="whoami",
            remove=True
        )
        
        logs = container.logs().decode('utf-8').strip()
        assert logs != "root", f"Container should not run as root user, running as: {logs}"