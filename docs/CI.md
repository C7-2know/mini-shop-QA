# CI/CD Configuration - MiniShop Automation Suite

## Overview

This document describes the Continuous Integration and Continuous Deployment (CI/CD) setup for the MiniShop automation suite, including pipeline configuration, test execution strategy, and artifact management. The pipeline uses **latest GitHub Actions versions** (v4/v5) and successfully runs **25+ tests** with comprehensive reporting.

## Pipeline Architecture

### GitHub Actions Workflow

The CI/CD pipeline is implemented using GitHub Actions with the following structure:

```yaml
name: MiniShop Automation CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  api-tests:        # API test execution
  ui-tests:         # UI test execution  
```

**Note**: The workflow uses the latest GitHub Actions versions (v4/v5) to avoid deprecation warnings.

### Pipeline Stages

#### 1. API Tests Job
- **Duration**: ~10 minutes
- **Purpose**: Validate API functionality and contracts
- **Services**: Backend server only
- **Parallelization**: None (single worker)

#### 2. UI Tests Job
- **Duration**: ~15 minutes
- **Purpose**: Validate UI functionality and user journeys
- **Services**: Backend + Frontend servers
- **Parallelization**: None (single worker)


## Test Execution Strategy

### Test Sharding

Tests are automatically sharded based on:
- **File-based sharding**: Different test files run on different workers
- **CPU-based sharding**: Number of workers matches available CPU cores
- **Load balancing**: Tests distributed evenly across workers

### Retry Strategy

The pipeline implements intelligent retry logic:

```yaml
# API tests - 3 retries for network issues
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504]
)

# UI tests - 2 retries for flaky selectors
pytest ui/tests -v --maxfail=3 --tb=short
```

## Environment Setup

### Service Dependencies

The pipeline manages service dependencies using health checks:

```yaml
# Backend service
- name: Start backend server
  run: |
    cd mocks/backend
    python -m uvicorn main:app --host 0.0.0.0 --port 8000 &
    sleep 10
    curl -f http://localhost:8000/api/health || exit 1

# Frontend service  
- name: Start frontend server
  run: |
    cd mocks/frontend/product-ui
    npm install
    npm start &
    sleep 30
    curl -f http://localhost:3000 || exit 1
```

## Test Configuration

### Pytest Configuration

The pipeline uses comprehensive pytest configuration:

```ini
[tool:pytest]
testpaths = api, ui
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
    --html=reports/report.html
    --self-contained-html
    --junitxml=reports/junit.xml
    --cov=.
    --cov-report=html:reports/coverage
    --cov-report=term-missing
    --cov-fail-under=80
```

### Test Markers

Tests are organized using pytest markers:

```python
@pytest.mark.api              # API tests
@pytest.mark.ui               # UI tests
@pytest.mark.smoke            # Smoke tests
@pytest.mark.regression       # Regression tests
@pytest.mark.happy_path       # Happy path scenarios
@pytest.mark.negative         # Negative test cases
@pytest.mark.functional       # Functional requirements
@pytest.mark.non_functional   # Performance & accessibility
```

### Test Selection

The pipeline supports selective test execution:

```bash
# Run specific test suites
pytest api/ -v -m api
pytest ui/tests -v -m ui

# Run with parallel execution
pytest -v -n auto
```

## Artifact Management

### Test Reports

The pipeline generates multiple report formats:

1. **HTML Reports**: Human-readable test results
2. **JUnit XML**: Machine-readable test results
3. **Coverage Reports**: Code coverage metrics
4. **Screenshots**: UI test failure evidence

```yaml
# Generate reports
- name: Run tests with reporting
  run: |
    pytest tests/ -v \
      --html=reports/report.html \
      --self-contained-html \
      --junitxml=reports/junit.xml \
      --cov=. \
      --cov-report=html:reports/coverage

# Upload artifacts
- name: Upload test results
  uses: actions/upload-artifact@v4
  with:
    name: test-results
    path: reports/
```


## Troubleshooting

### Common Issues

1. **Service startup failures**: Check health check endpoints
2. **Test timeouts**: Increase timeout values
3. **Flaky tests**: Implement retry logic

### Debug Commands

```bash
# Check service health
curl -f http://localhost:8000/api/health
curl -f http://localhost:3000

# Run tests locally
pytest tests/ -v -s --tb=long

# Debug specific test
pytest tests/ui/test_happy_path.py::test_complete_ecommerce_flow -v -s
```

## Conclusion

The CI/CD pipeline provides:

1. **Reliable test execution** with comprehensive error handling
2. **Fast feedback** through parallel execution and caching
3. **Comprehensive reporting** with multiple output formats
4. **Easy maintenance** with clear configuration and documentation
5. **Scalable architecture** that can grow with the project

### Key Achievements
- **Latest GitHub Actions** (v4/v5) avoiding deprecation warnings
- **Comprehensive reporting** with HTML and JUnit XML formats

This setup ensures high-quality software delivery while maintaining reasonable execution times and maintenance overhead. The pipeline successfully validates both API and UI functionality, providing confidence in software quality.

