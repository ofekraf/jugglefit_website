import pytest
import yaml
import os
import subprocess
import shutil
from pathlib import Path


def docker_available():
    """Check if Docker is available and accessible."""
    try:
        result = subprocess.run(['docker', 'info'], capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def docker_compose_available():
    """Check if docker-compose is available."""
    return shutil.which('docker-compose') is not None


class TestDockerComposeDevConfiguration:
    """Test development docker-compose.yml configuration."""
    
    def test_docker_compose_dev_exists(self, docker_compose_dev_path):
        """Test that development docker-compose.yml exists."""
        assert docker_compose_dev_path.exists(), "docker-compose.yml should exist"
    
    def test_docker_compose_dev_valid_yaml(self, docker_compose_dev_path):
        """Test that development docker-compose.yml is valid YAML."""
        try:
            with open(docker_compose_dev_path) as f:
                yaml.safe_load(f)
        except yaml.YAMLError as e:
            pytest.fail(f"docker-compose.yml is not valid YAML: {e}")
    
    def test_docker_compose_dev_has_web_service(self, docker_compose_dev_path):
        """Test that development docker-compose has web service."""
        with open(docker_compose_dev_path) as f:
            config = yaml.safe_load(f)
        
        assert 'services' in config, "docker-compose.yml should have services section"
        assert 'web' in config['services'], "Should have web service"
    
    def test_docker_compose_dev_port_mapping(self, docker_compose_dev_path):
        """Test that development docker-compose maps port correctly."""
        with open(docker_compose_dev_path) as f:
            config = yaml.safe_load(f)
        
        web_service = config['services']['web']
        assert 'ports' in web_service, "Web service should have port mapping"
        
        ports = web_service['ports']
        assert any('5001:5001' in str(port) for port in ports), "Should map port 5001:5001"
    
    def test_docker_compose_dev_environment_variables(self, docker_compose_dev_path):
        """Test that development docker-compose sets environment variables."""
        with open(docker_compose_dev_path) as f:
            config = yaml.safe_load(f)
        
        web_service = config['services']['web']
        assert 'environment' in web_service or 'env_file' in web_service, "Should set environment variables"
    
    def test_docker_compose_dev_volume_mounting(self, docker_compose_dev_path):
        """Test that development docker-compose mounts code for development."""
        with open(docker_compose_dev_path) as f:
            config = yaml.safe_load(f)
        
        web_service = config['services']['web']
        assert 'volumes' in web_service, "Development should mount volumes for hot reload"
    
    def test_docker_compose_dev_restart_policy(self, docker_compose_dev_path):
        """Test that development docker-compose has appropriate restart policy."""
        with open(docker_compose_dev_path) as f:
            config = yaml.safe_load(f)
        
        web_service = config['services']['web']
        if 'restart' in web_service:
            assert web_service['restart'] in ['unless-stopped', 'always', 'on-failure'], "Should have appropriate restart policy"


class TestDockerComposeProdConfiguration:
    """Test production docker-compose.prod.yml configuration."""
    
    def test_docker_compose_prod_exists(self, docker_compose_prod_path):
        """Test that production docker-compose.prod.yml exists."""
        assert docker_compose_prod_path.exists(), "docker-compose.prod.yml should exist"
    
    def test_docker_compose_prod_valid_yaml(self, docker_compose_prod_path):
        """Test that production docker-compose.prod.yml is valid YAML."""
        try:
            with open(docker_compose_prod_path) as f:
                yaml.safe_load(f)
        except yaml.YAMLError as e:
            pytest.fail(f"docker-compose.prod.yml is not valid YAML: {e}")
    
    def test_docker_compose_prod_has_web_service(self, docker_compose_prod_path):
        """Test that production docker-compose has web service."""
        with open(docker_compose_prod_path) as f:
            config = yaml.safe_load(f)
        
        assert 'services' in config, "docker-compose.prod.yml should have services section"
        assert 'web' in config['services'], "Should have web service"
    
    def test_docker_compose_prod_no_volume_mounting(self, docker_compose_prod_path):
        """Test that production docker-compose doesn't mount code volumes."""
        with open(docker_compose_prod_path) as f:
            config = yaml.safe_load(f)
        
        web_service = config['services']['web']
        if 'volumes' in web_service:
            # Should not mount source code in production
            volumes = web_service['volumes']
            code_mounts = [v for v in volumes if '.:/app' in str(v) or './:/app' in str(v)]
            assert len(code_mounts) == 0, "Production should not mount source code volumes"
    
    def test_docker_compose_prod_uses_gunicorn(self, docker_compose_prod_path):
        """Test that production docker-compose uses Gunicorn."""
        with open(docker_compose_prod_path) as f:
            config = yaml.safe_load(f)
        
        web_service = config['services']['web']
        if 'command' in web_service:
            command = str(web_service['command'])
            assert 'gunicorn' in command.lower(), "Production should use Gunicorn server"
    
    def test_docker_compose_prod_environment_production(self, docker_compose_prod_path):
        """Test that production docker-compose sets production environment."""
        with open(docker_compose_prod_path) as f:
            config = yaml.safe_load(f)
        
        web_service = config['services']['web']
        if 'environment' in web_service:
            env_vars = web_service['environment']
            # Should set production environment
            flask_env_set = any('FLASK_ENV=production' in str(env) or 'FLASK_ENV: production' in str(env) for env in env_vars)
            assert flask_env_set, "Should set FLASK_ENV=production"
    
    def test_docker_compose_prod_restart_policy(self, docker_compose_prod_path):
        """Test that production docker-compose has restart policy."""
        with open(docker_compose_prod_path) as f:
            config = yaml.safe_load(f)
        
        web_service = config['services']['web']
        assert 'restart' in web_service, "Production should have restart policy"
        assert web_service['restart'] in ['unless-stopped', 'always'], "Should have appropriate restart policy for production"


class TestDockerComposeIntegration:
    """Test docker-compose integration and functionality."""
    
    @pytest.mark.skipif(not docker_available() or not docker_compose_available(), 
                       reason="Docker or docker-compose not available")
    def test_docker_compose_dev_builds_and_runs(self, project_root, docker_compose_dev_path):
        """Test that development docker-compose builds and runs successfully."""
        import subprocess
        import os
        
        # Change to project directory
        original_cwd = os.getcwd()
        os.chdir(project_root)
        
        try:
            # Build services
            result = subprocess.run(
                ['docker-compose', 'build'],
                capture_output=True,
                text=True,
                timeout=300
            )
            assert result.returncode == 0, f"docker-compose build failed: {result.stderr}"
            
            # Start services
            result = subprocess.run(
                ['docker-compose', 'up', '-d'],
                capture_output=True,
                text=True,
                timeout=60
            )
            assert result.returncode == 0, f"docker-compose up failed: {result.stderr}"
            
            # Check if service is running
            result = subprocess.run(
                ['docker-compose', 'ps'],
                capture_output=True,
                text=True
            )
            assert 'web' in result.stdout, "Web service should be running"
            
        finally:
            # Cleanup
            subprocess.run(['docker-compose', 'down'], capture_output=True)
            os.chdir(original_cwd)
    
    @pytest.mark.skipif(not docker_available() or not docker_compose_available(), 
                       reason="Docker or docker-compose not available")
    def test_docker_compose_prod_builds_and_runs(self, project_root, docker_compose_prod_path):
        """Test that production docker-compose builds and runs successfully."""
        import subprocess
        import os
        
        # Change to project directory
        original_cwd = os.getcwd()
        os.chdir(project_root)
        
        try:
            # Build services
            result = subprocess.run(
                ['docker-compose', '-f', 'docker-compose.prod.yml', 'build'],
                capture_output=True,
                text=True,
                timeout=300
            )
            assert result.returncode == 0, f"docker-compose prod build failed: {result.stderr}"
            
            # Start services
            result = subprocess.run(
                ['docker-compose', '-f', 'docker-compose.prod.yml', 'up', '-d'],
                capture_output=True,
                text=True,
                timeout=60
            )
            assert result.returncode == 0, f"docker-compose prod up failed: {result.stderr}"
            
        finally:
            # Cleanup
            subprocess.run(['docker-compose', '-f', 'docker-compose.prod.yml', 'down'], capture_output=True)
            os.chdir(original_cwd)