import pytest
import os
import stat
from pathlib import Path


class TestOCIUbuntuDeploymentScripts:
    """Test OCI Ubuntu deployment scripts and configuration."""
    
    def test_oci_deployment_directory_exists(self, oci_deployment_path):
        """Test that OCI deployment directory exists."""
        assert oci_deployment_path.exists(), "OCI deployment directory should exist"
    
    def test_docker_deployment_script_exists(self, oci_deployment_path):
        """Test that Docker deployment script exists."""
        deploy_script = oci_deployment_path / "deploy.sh"
        assert deploy_script.exists(), "Docker deployment script should exist"
    
    def test_deployment_script_is_executable(self, oci_deployment_path):
        """Test that deployment script is executable."""
        deploy_script = oci_deployment_path / "deploy.sh"
        if deploy_script.exists():
            mode = deploy_script.stat().st_mode
            assert mode & stat.S_IEXEC, "Deployment script should be executable"
    
    def test_systemd_service_file_exists(self, oci_deployment_path):
        """Test that systemd service file exists."""
        service_file = oci_deployment_path / "jugglefit.service"
        assert service_file.exists(), "Systemd service file should exist"
    
    def test_systemd_service_configuration(self, oci_deployment_path):
        """Test that systemd service is properly configured."""
        service_file = oci_deployment_path / "jugglefit.service"
        content = service_file.read_text()
        
        # Should have required systemd sections
        assert '[Unit]' in content, "Service file should have [Unit] section"
        assert '[Service]' in content, "Service file should have [Service] section"
        assert '[Install]' in content, "Service file should have [Install] section"
        
        # Should use Docker
        assert 'docker' in content.lower(), "Service should use Docker"
        
        # Should have restart policy
        assert 'Restart=' in content, "Service should have restart policy"
    
    def test_nginx_configuration_exists(self, oci_deployment_path):
        """Test that Nginx configuration exists."""
        nginx_config = oci_deployment_path / "nginx.conf"
        assert nginx_config.exists(), "Nginx configuration should exist"
    
    def test_nginx_configuration_valid(self, oci_deployment_path):
        """Test that Nginx configuration is valid."""
        nginx_config = oci_deployment_path / "nginx.conf"
        content = nginx_config.read_text()
        
        # Should have server block
        assert 'server {' in content, "Should have server block"
        
        # Should proxy to application
        assert 'proxy_pass' in content, "Should proxy to application"
        assert '5001' in content, "Should proxy to port 5001"
        
        # Should have basic security headers
        security_headers = ['X-Content-Type-Options', 'X-Frame-Options']
        has_security = any(header in content for header in security_headers)
        assert has_security, "Should include basic security headers"
    
    def test_ssl_certificate_setup_script_exists(self, oci_deployment_path):
        """Test that SSL certificate setup script exists."""
        ssl_script = oci_deployment_path / "setup-ssl.sh"
        assert ssl_script.exists(), "SSL setup script should exist"
    
    def test_environment_configuration_template_exists(self, oci_deployment_path):
        """Test that environment configuration template exists."""
        env_template = oci_deployment_path / ".env.production"
        assert env_template.exists(), "Production environment template should exist"
    
    def test_deployment_documentation_exists(self, oci_deployment_path):
        """Test that deployment documentation exists."""
        readme = oci_deployment_path / "README.md"
        assert readme.exists(), "Deployment README should exist"
    
    def test_deployment_documentation_comprehensive(self, oci_deployment_path):
        """Test that deployment documentation is comprehensive."""
        readme = oci_deployment_path / "README.md"
        content = readme.read_text().lower()
        
        # Should cover key deployment topics
        topics = ['prerequisites', 'installation', 'configuration', 'ssl', 'firewall']
        for topic in topics:
            assert topic in content, f"Documentation should cover {topic}"


class TestOCIDeploymentScriptContent:
    """Test OCI deployment script content and functionality."""
    
    def test_deployment_script_updates_system(self, oci_deployment_path):
        """Test that deployment script updates system packages."""
        deploy_script = oci_deployment_path / "deploy.sh"
        content = deploy_script.read_text()
        
        # Should update system
        assert 'apt update' in content or 'apt-get update' in content, "Should update package lists"
    
    def test_deployment_script_installs_docker(self, oci_deployment_path):
        """Test that deployment script installs Docker."""
        deploy_script = oci_deployment_path / "deploy.sh"
        content = deploy_script.read_text()
        
        # Should install Docker
        assert 'docker' in content.lower(), "Should install or configure Docker"
        assert 'install' in content.lower(), "Should install required packages"
    
    def test_deployment_script_configures_firewall(self, oci_deployment_path):
        """Test that deployment script configures firewall."""
        deploy_script = oci_deployment_path / "deploy.sh"
        content = deploy_script.read_text()
        
        # Should configure firewall
        firewall_tools = ['ufw', 'iptables', 'firewall']
        has_firewall = any(tool in content.lower() for tool in firewall_tools)
        assert has_firewall, "Should configure firewall"
    
    def test_deployment_script_sets_up_logging(self, oci_deployment_path):
        """Test that deployment script sets up logging."""
        deploy_script = oci_deployment_path / "deploy.sh"
        content = deploy_script.read_text()
        
        # Should set up logging
        logging_tools = ['journalctl', 'syslog', 'log']
        has_logging = any(tool in content.lower() for tool in logging_tools)
        assert has_logging, "Should configure logging"
    
    def test_deployment_script_handles_errors(self, oci_deployment_path):
        """Test that deployment script has error handling."""
        deploy_script = oci_deployment_path / "deploy.sh"
        content = deploy_script.read_text()
        
        # Should have error handling
        error_handling = ['set -e', 'trap', 'exit 1']
        has_error_handling = any(handler in content for handler in error_handling)
        assert has_error_handling, "Should have error handling"
    
    def test_deployment_script_is_idempotent(self, oci_deployment_path):
        """Test that deployment script can be run multiple times safely."""
        deploy_script = oci_deployment_path / "deploy.sh"
        content = deploy_script.read_text()
        
        # Should check for existing installations
        checks = ['which', 'command -v', 'if [', '[ -f']
        has_checks = any(check in content for check in checks)
        assert has_checks, "Should check for existing installations (idempotent)"


class TestOCIProductionConfiguration:
    """Test OCI production-specific configuration."""
    
    def test_production_environment_variables(self, oci_deployment_path):
        """Test that production environment variables are properly configured."""
        env_prod = oci_deployment_path / ".env.production"
        content = env_prod.read_text()
        
        # Should set production environment
        assert 'FLASK_ENV=production' in content, "Should set FLASK_ENV=production"
        
        # Should not have debug mode
        assert 'DEBUG=False' in content or 'DEBUG=0' in content, "Should disable debug mode"
    
    def test_systemd_service_security(self, oci_deployment_path):
        """Test that systemd service has security configurations."""
        service_file = oci_deployment_path / "jugglefit.service"
        content = service_file.read_text()
        
        # Should not run as root
        assert 'User=' in content and 'User=root' not in content, "Should not run as root user"
        
        # Should have security settings
        security_settings = ['NoNewPrivileges=true', 'PrivateTmp=true', 'ProtectSystem=strict']
        has_security = any(setting in content for setting in security_settings)
        assert has_security, "Should have systemd security settings"
    
    def test_nginx_ssl_configuration(self, oci_deployment_path):
        """Test that Nginx is configured for SSL."""
        nginx_config = oci_deployment_path / "nginx.conf"
        content = nginx_config.read_text()
        
        # Should support SSL
        ssl_config = ['ssl_certificate', 'listen 443', 'ssl on']
        has_ssl = any(config in content for config in ssl_config)
        assert has_ssl, "Should be configured for SSL"
    
    def test_backup_script_exists(self, oci_deployment_path):
        """Test that backup script exists."""
        backup_script = oci_deployment_path / "backup.sh"
        assert backup_script.exists(), "Backup script should exist"
    
    def test_monitoring_configuration_exists(self, oci_deployment_path):
        """Test that monitoring configuration exists."""
        # Could be prometheus, grafana, or basic monitoring
        monitoring_files = ['monitoring.yml', 'prometheus.yml', 'health-check.sh']
        has_monitoring = any((oci_deployment_path / f).exists() for f in monitoring_files)
        assert has_monitoring, "Should have monitoring configuration"


class TestOCIDeploymentValidation:
    """Test OCI deployment validation and prerequisites."""
    
    def test_minimum_system_requirements_documented(self, oci_deployment_path):
        """Test that minimum system requirements are documented."""
        readme = oci_deployment_path / "README.md"
        content = readme.read_text().lower()
        
        # Should specify minimum requirements
        requirements = ['memory', 'disk', 'cpu', 'ubuntu']
        for req in requirements:
            assert req in content, f"Should document {req} requirements"
    
    def test_port_configuration_documented(self, oci_deployment_path):
        """Test that required ports are documented."""
        readme = oci_deployment_path / "README.md"
        content = readme.read_text()
        
        # Should document required ports
        ports = ['80', '443', '5001']
        for port in ports:
            assert port in content, f"Should document port {port}"
    
    def test_security_checklist_exists(self, oci_deployment_path):
        """Test that security checklist exists."""
        security_files = ['SECURITY.md', 'security-checklist.md']
        has_security_docs = any((oci_deployment_path / f).exists() for f in security_files)
        
        if not has_security_docs:
            # Check if security is covered in main README
            readme = oci_deployment_path / "README.md"
            content = readme.read_text().lower()
            assert 'security' in content, "Should have security documentation"
    
    def test_troubleshooting_guide_exists(self, oci_deployment_path):
        """Test that troubleshooting guide exists."""
        readme = oci_deployment_path / "README.md"
        content = readme.read_text().lower()
        
        # Should have troubleshooting section
        troubleshooting_keywords = ['troubleshoot', 'problem', 'issue', 'debug']
        has_troubleshooting = any(keyword in content for keyword in troubleshooting_keywords)
        assert has_troubleshooting, "Should have troubleshooting guide"