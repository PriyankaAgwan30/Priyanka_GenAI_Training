# Day 12 – CI/CD, Docker and Deployment

## Objective
To automate code quality checks, testing, Docker image building, and deployment preparation for the UGCRuleBook project.

## 1. GitHub Actions – Continuous Integration (CI)
Configured GitHub Actions to automatically execute checks whenever code is pushed to `main` or a Pull Request is created.

**Workflow file:** `.github/workflows/ci.yml`

Tasks completed:
- Configured GitHub Actions workflow.
- Set up Python 3.12 environment.
- Installed project dependencies.
- Automated Ruff linting.
- Automated Pytest execution.
- Automated Docker image build verification.

## 2. Code Quality – Ruff
Integrated Ruff for Python code quality checking.

Command:
```bash
python -m ruff check .
```

Purpose:
- Identify coding errors.
- Detect undefined variables.
- Maintain consistent code quality.
- Detect common Python issues.

## 3. Automated Testing – Pytest
Configured automated testing using Pytest.

Command:
```bash
python -m pytest -v
```

Tests verify the functionality of different components of the UGCRuleBook backend.

## 4. Docker Containerization
Created a Dockerfile to containerize the UGCRuleBook application.

Implemented:
- Python 3.12 base image.
- Installation of system dependencies.
- Installation of Python requirements.
- Application source code copying.
- API server startup using Uvicorn.
- Port configuration.

## 5. Backend Startup Optimization
Implemented lazy loading in backend modules to reduce unnecessary loading of AI components during API startup.

Updated files:
- `backend/main.py`
- `backend/embed.py`

This optimization helps reduce initial memory usage by loading certain AI components only when required.

## 6. Deployment – Render
Attempted to deploy the FastAPI backend on Render using Docker.

Deployment configuration:
- Runtime: Docker
- Backend framework: FastAPI
- Deployment platform: Render
- Health check endpoint: `/health`

The deployment was attempted successfully, but the service encountered a memory limitation on the free instance (512 MB RAM) while running the application.

Further memory optimization or a higher-memory deployment environment is required.

## 7. Tools and Technologies
- Python
- FastAPI
- Git and GitHub
- GitHub Actions
- Ruff
- Pytest
- Docker
- Render

## 8. Outcome
- Implemented a CI workflow for automated validation.
- Integrated linting and testing.
- Added Docker containerization support.
- Optimized backend startup using lazy loading.
- Attempted cloud deployment.
- Identified deployment memory requirements.

## Status
CI pipeline and Docker build verification are implemented. Cloud deployment was attempted, and memory optimization remains a pending task.
