import pytest
import requests
import time
import subprocess
from pathlib import Path


class TestProductionServerConfiguration:
    """Test production server configuration and requirements."""
    
    def test_gunicorn_in_requirements(self, project_root):
        """Test that Gunicorn is included in requirements.txt."""
        requirements_path = project_root / "requirements.txt"
        assert requirements_path.exists(), "requirements.txt should exist"
        
        content = requirements_path.read_text()
        assert "gunicorn" in content.lower(), "Gunicorn should be in requirements.txt"
    
    def test_wsgi_module_exists(self, project_root):
        """Test that WSGI module exists for production deployment."""
        wsgi_path = project_root / "wsgi.py"
        assert wsgi_path.exists(), "wsgi.py should exist for WSGI deployment"
        
        content = wsgi_path.read_text()
        assert "app" in content, "wsgi.py should import and expose the Flask app"
    
    def test_production_environment_configuration(self, project_root):
        """Test that app.py has production environment configuration."""
        app_path = project_root / "app.py"
        content = app_path.read_text()
        
        # Should not run in debug mode in production
        assert "debug=True" not in content or "os.environ.get" in content, "Should handle debug mode via environment"
    
    def test_env_example_exists(self, env_example_path):
        """Test that .env.example exists with required variables."""
        assert env_example_path.exists(), ".env.example should exist"
        
        content = env_example_path.read_text()
        # Should contain common environment variables
        expected_vars = ["FLASK_ENV", "FLASK_APP"]
        for var in expected_vars:
            assert var in content, f"{var} should be in .env.example"


class TestHealthCheckEndpoints:
    """Test health check endpoint functionality."""
    
    def test_health_check_endpoint_exists(self, project_root):
        """Test that health check endpoint is defined in the app."""
        app_path = project_root / "app.py"
        content = app_path.read_text()
        
        # Should have a health check route
        assert "/health" in content or "/healthz" in content, "Should have health check endpoint"
    
    def test_readiness_probe_endpoint_exists(self, project_root):
        """Test that readiness probe endpoint exists."""
        app_path = project_root / "app.py"
        content = app_path.read_text()
        
        # Should have readiness probe endpoint
        assert "/ready" in content or "/healthz" in content, "Should have readiness probe endpoint"


class TestProductionDeployment:
    """Test production deployment functionality."""
    
    def test_gunicorn_starts_successfully(self, project_root):
        """Test that Gunicorn can start the application."""
        import subprocess
        import os
        import signal
        import time
        
        # Change to project directory
        original_cwd = os.getcwd()
        os.chdir(project_root)
        
        try:
            # Start Gunicorn
            process = subprocess.Popen(
                ['gunicorn', '--bind', '127.0.0.1:5002', '--timeout', '30', 'wsgi:app'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for startup
            time.sleep(3)
            
            # Check if process is running
            assert process.poll() is None, "Gunicorn process should be running"
            
            # Try to make a request
            try:
                response = requests.get('http://127.0.0.1:5002/', timeout=5)
                assert response.status_code == 200, f"Health check should return 200, got {response.status_code}"
            except requests.exceptions.ConnectionError:
                pytest.fail("Could not connect to Gunicorn server")
            
        finally:
            # Cleanup
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=5)
            os.chdir(original_cwd)
    
    def test_application_serves_static_files(self, project_root):
        """Test that application serves static files correctly in production."""
        import subprocess
        import os
        import time
        
        original_cwd = os.getcwd()
        os.chdir(project_root)
        
        try:
            # Start Gunicorn
            process = subprocess.Popen(
                ['gunicorn', '--bind', '127.0.0.1:5003', 'wsgi:app'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            time.sleep(3)
            assert process.poll() is None, "Gunicorn should be running"
            
            # Test static file serving
            try:
                response = requests.get('http://127.0.0.1:5003/static/css/styles.css', timeout=5)
                assert response.status_code == 200, "Should serve static CSS files"
                assert 'text/css' in response.headers.get('content-type', ''), "Should serve CSS with correct content type"
            except requests.exceptions.ConnectionError:
                pytest.fail("Could not access static files")
            
        finally:
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=5)
            os.chdir(original_cwd)
    
    def test_production_logging_configuration(self, project_root):
        """Test that production logging is properly configured."""
        # This test ensures that the app has proper logging setup
        app_path = project_root / "app.py"
        content = app_path.read_text()
        
        # Should have logging configuration or use Flask's default logging
        # At minimum, should not print debug statements to stdout in production
        assert "app.logger" in content or "logging" in content or "print(" not in content, "Should use proper logging instead of print statements"


class TestContainerProductionReadiness:
    """Test that containers are production-ready."""
    
    def test_container_health_check_responds(self, docker_client, project_root):
        """Test that container health check endpoint responds correctly."""
        # Build image
        image, _ = docker_client.images.build(
            path=str(project_root),
            tag="jugglefit-prod-test:latest",
            rm=True,
            forcerm=True
        )
        
        # Start container with production settings
        container = docker_client.containers.run(
            "jugglefit-prod-test:latest",
            detach=True,
            ports={'5001/tcp': 5004},
            environment={
                'FLASK_ENV': 'production'
            }
        )
        
        try:
            # Wait for service to be ready
            from tests.docker.conftest import wait_for_service_ready
            is_ready = wait_for_service_ready('http://localhost:5004/health', timeout=30)
            assert is_ready, "Health check endpoint should respond within 30 seconds"
            
            # Test health check response
            response = requests.get('http://localhost:5004/health', timeout=5)
            assert response.status_code == 200, "Health check should return 200"
            
        finally:
            container.stop()
            container.remove()
    
    def test_container_handles_graceful_shutdown(self, docker_client, project_root):
        """Test that container handles graceful shutdown properly."""
        image, _ = docker_client.images.build(
            path=str(project_root),
            tag="jugglefit-shutdown-test:latest",
            rm=True,
            forcerm=True
        )
        
        container = docker_client.containers.run(
            "jugglefit-shutdown-test:latest",
            detach=True,
            ports={'5001/tcp': None}
        )
        
        try:
            # Wait for container to be running
            time.sleep(3)
            container.reload()
            assert container.status == 'running', "Container should be running"
            
            # Send graceful stop signal
            container.stop(timeout=10)
            
            # Container should stop gracefully within timeout
            container.reload()
            assert container.status in ['exited'], "Container should stop gracefully"
            
        finally:
            container.remove()
    
    def test_container_resource_limits(self, docker_client, project_root):
        """Test that container runs within reasonable resource limits."""
        image, _ = docker_client.images.build(
            path=str(project_root),
            tag="jugglefit-resource-test:latest",
            rm=True,
            forcerm=True
        )
        
        # Run container with resource limits
        container = docker_client.containers.run(
            "jugglefit-resource-test:latest",
            detach=True,
            mem_limit='256m',  # 256MB RAM limit
            ports={'5001/tcp': None}
        )
        
        try:
            # Wait for startup
            time.sleep(5)
            
            container.reload()
            assert container.status == 'running', "Container should run within 256MB RAM limit"
            
            # Check memory usage
            stats = container.stats(stream=False)
            memory_usage = stats['memory_stats']['usage']
            memory_limit = stats['memory_stats']['limit']
            
            usage_mb = memory_usage / (1024 * 1024)
            assert usage_mb < 200, f"Memory usage {usage_mb:.1f}MB should be reasonable"
            
        finally:
            container.stop()
            container.remove()