import pytest
import yaml
from pathlib import Path


class TestGitHubActionsWorkflow:
    """Test GitHub Actions CI/CD workflow configuration."""
    
    def test_github_workflow_exists(self, github_workflow_path):
        """Test that GitHub Actions workflow file exists."""
        assert github_workflow_path.parent.exists(), ".github/workflows directory should exist"
        assert github_workflow_path.exists(), "GitHub Actions workflow should exist"
    
    def test_github_workflow_valid_yaml(self, github_workflow_path):
        """Test that GitHub Actions workflow is valid YAML."""
        try:
            with open(github_workflow_path) as f:
                yaml.safe_load(f)
        except yaml.YAMLError as e:
            pytest.fail(f"GitHub Actions workflow is not valid YAML: {e}")
    
    def test_workflow_has_required_triggers(self, github_workflow_path):
        """Test that workflow has appropriate triggers."""
        with open(github_workflow_path) as f:
            workflow = yaml.safe_load(f)
        
        assert 'on' in workflow, "Workflow should have trigger configuration"
        
        triggers = workflow['on']
        # Should trigger on push and pull requests
        assert 'push' in triggers or 'pull_request' in triggers, "Should trigger on push or PR"
    
    def test_workflow_has_test_job(self, github_workflow_path):
        """Test that workflow includes test job."""
        with open(github_workflow_path) as f:
            workflow = yaml.safe_load(f)
        
        assert 'jobs' in workflow, "Workflow should have jobs"
        
        jobs = workflow['jobs']
        test_job_exists = any('test' in job_name.lower() for job_name in jobs.keys())
        assert test_job_exists, "Should have a test job"
    
    def test_workflow_has_build_job(self, github_workflow_path):
        """Test that workflow includes Docker build job."""
        with open(github_workflow_path) as f:
            workflow = yaml.safe_load(f)
        
        jobs = workflow['jobs']
        build_job_exists = any('build' in job_name.lower() or 'docker' in job_name.lower() for job_name in jobs.keys())
        assert build_job_exists, "Should have a Docker build job"
    
    def test_workflow_uses_docker_actions(self, github_workflow_path):
        """Test that workflow uses Docker-related actions."""
        with open(github_workflow_path) as f:
            content = f.read()
        
        # Should use Docker build/push actions
        docker_actions = ['docker/build-push-action', 'docker/setup-buildx-action', 'docker/login-action']
        uses_docker_action = any(action in content for action in docker_actions)
        assert uses_docker_action, "Should use Docker GitHub Actions"
    
    def test_workflow_runs_tests_before_build(self, github_workflow_path):
        """Test that workflow runs tests before building/deploying."""
        with open(github_workflow_path) as f:
            workflow = yaml.safe_load(f)
        
        jobs = workflow['jobs']
        
        # Check for job dependencies or proper ordering
        has_test_before_build = False
        for job_name, job_config in jobs.items():
            if 'build' in job_name.lower() or 'deploy' in job_name.lower():
                if 'needs' in job_config:
                    needs = job_config['needs']
                    if isinstance(needs, str):
                        needs = [needs]
                    test_dependency = any('test' in need.lower() for need in needs)
                    if test_dependency:
                        has_test_before_build = True
                        break
        
        assert has_test_before_build, "Build/deploy jobs should depend on test jobs"
    
    def test_workflow_has_security_scanning(self, github_workflow_path):
        """Test that workflow includes security scanning."""
        with open(github_workflow_path) as f:
            content = f.read()
        
        # Should include security scanning (Trivy, Snyk, or similar)
        security_tools = ['trivy', 'snyk', 'security', 'vulnerability']
        has_security_scan = any(tool in content.lower() for tool in security_tools)
        assert has_security_scan, "Should include security scanning in CI/CD pipeline"
    
    def test_workflow_builds_for_multiple_platforms(self, github_workflow_path):
        """Test that workflow builds for multiple platforms if using buildx."""
        with open(github_workflow_path) as f:
            content = f.read()
        
        if 'buildx' in content.lower():
            # If using buildx, should build for multiple platforms
            platforms = ['linux/amd64', 'linux/arm64']
            has_multiplatform = any(platform in content for platform in platforms)
            assert has_multiplatform, "Should build for multiple platforms when using buildx"
    
    def test_workflow_uses_github_container_registry(self, github_workflow_path):
        """Test that workflow uses GitHub Container Registry."""
        with open(github_workflow_path) as f:
            content = f.read()
        
        # Should use GHCR
        assert 'ghcr.io' in content, "Should use GitHub Container Registry (ghcr.io)"
    
    def test_workflow_has_environment_specific_deployments(self, github_workflow_path):
        """Test that workflow has different environments (staging/production)."""
        with open(github_workflow_path) as f:
            workflow = yaml.safe_load(f)
        
        # Should have different deployment stages or environments
        content_str = str(workflow).lower()
        environments = ['production', 'staging', 'prod', 'stage']
        has_environments = any(env in content_str for env in environments)
        assert has_environments, "Should have different deployment environments"


class TestCIPipelineIntegration:
    """Test CI pipeline integration and functionality."""
    
    def test_dockerfile_linting_in_pipeline(self, project_root):
        """Test that Dockerfile can be linted (hadolint compatibility)."""
        dockerfile_path = project_root / "Dockerfile"
        content = dockerfile_path.read_text()
        
        # Basic linting checks that would be caught by hadolint
        lines = content.split('\n')
        
        # Should not have sudo
        assert not any('sudo' in line for line in lines), "Dockerfile should not use sudo"
        
        # Should use COPY instead of ADD when possible
        add_lines = [line for line in lines if line.strip().startswith('ADD')]
        for line in add_lines:
            # ADD should only be used for URLs or tar extraction
            assert 'http' in line or '.tar' in line, f"Should use COPY instead of ADD: {line}"
    
    def test_requirements_txt_security_scanning(self, project_root):
        """Test that requirements.txt can be scanned for vulnerabilities."""
        requirements_path = project_root / "requirements.txt"
        assert requirements_path.exists(), "requirements.txt should exist for security scanning"
        
        content = requirements_path.read_text()
        lines = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('#')]
        
        # Should have pinned versions for security
        unpinned_packages = [line for line in lines if '==' not in line and '>=' not in line and '~=' not in line]
        assert len(unpinned_packages) < len(lines) * 0.5, "Should have most packages pinned for security"
    
    def test_git_repository_structure_for_ci(self, project_root):
        """Test that repository structure supports CI/CD."""
        # Should have necessary files for CI/CD
        required_files = [
            'requirements.txt',
            'Dockerfile',
            'docker-compose.yml',
            '.gitignore'
        ]
        
        for file_name in required_files:
            file_path = project_root / file_name
            assert file_path.exists(), f"{file_name} should exist for CI/CD"
    
    def test_environment_variables_security(self, project_root):
        """Test that sensitive environment variables are not hardcoded."""
        # Check common files for hardcoded secrets
        files_to_check = ['app.py', 'wsgi.py']
        
        sensitive_patterns = [
            'password=',
            'secret=',
            'api_key=',
            'token=',
            'key='
        ]
        
        for file_name in files_to_check:
            file_path = project_root / file_name
            if file_path.exists():
                content = file_path.read_text().lower()
                for pattern in sensitive_patterns:
                    if pattern in content:
                        # Should use environment variables, not hardcoded values
                        line_with_pattern = [line for line in content.split('\n') if pattern in line][0]
                        assert 'os.environ' in line_with_pattern or 'getenv' in line_with_pattern, f"Should use environment variables for sensitive data: {line_with_pattern}"
    
    def test_docker_image_vulnerability_scanning_ready(self, project_root):
        """Test that Docker image is ready for vulnerability scanning."""
        dockerfile_path = project_root / "Dockerfile"
        content = dockerfile_path.read_text()
        
        # Should use official base images for better security scanning
        assert 'FROM python:' in content, "Should use official Python image for better security scanning"
        
        # Should not install unnecessary packages that increase attack surface
        dangerous_packages = ['sudo', 'ssh', 'telnet']
        for package in dangerous_packages:
            assert package not in content.lower(), f"Should not install {package} in production image"