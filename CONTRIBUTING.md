# Contributing to Real-Time Manufacturing Sensor Streaming

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Pull Request Process](#pull-request-process)
- [Testing Guidelines](#testing-guidelines)

## Code of Conduct

### Our Pledge
We are committed to providing a welcoming and inclusive environment for all contributors.

### Our Standards
- Be respectful and inclusive
- Accept constructive criticism gracefully
- Focus on what's best for the community
- Show empathy towards others

## Getting Started

### Prerequisites
1. Fork the repository
2. Clone your fork locally
3. Set up development environment (see README.md)
4. Create a new branch for your changes

```bash
git clone https://github.com/YOUR_USERNAME/real-time-manufacturing-sensor-streaming-kinesis-flink-timestream.git
cd real-time-manufacturing-sensor-streaming-kinesis-flink-timestream
bash scripts/setup/setup_dev_environment.sh
git checkout -b feature/your-feature-name
```

## Development Workflow

### 1. Create an Issue
Before starting work:
- Check if an issue already exists
- Create a new issue describing your proposed changes
- Wait for feedback from maintainers

### 2. Develop Your Changes
- Keep changes focused and atomic
- Write clear, descriptive commit messages
- Add tests for new functionality
- Update documentation as needed

### 3. Test Locally
```bash
# Run Python tests
cd python
source venv/bin/activate
pytest tests/

# Validate Terraform
cd terraform/modules/MODULE_NAME
terraform validate
terraform fmt -check
```

### 4. Submit Pull Request
- Push your branch to your fork
- Create a pull request
- Fill out the PR template completely
- Link related issues

## Coding Standards

### Python Code
- Follow PEP 8 style guide
- Use type hints where appropriate
- Write docstrings for all functions and classes
- Maximum line length: 100 characters

**Example:**
```python
def process_sensor_data(
    readings: List[Dict],
    threshold: float = 50.0,
) -> List[Dict]:
    """
    Process sensor readings and filter by threshold.
    
    Args:
        readings: List of sensor reading dictionaries
        threshold: Minimum value threshold
        
    Returns:
        Filtered list of readings
    """
    return [r for r in readings if r.get("value", 0) > threshold]
```

### Terraform Code
- Use consistent naming conventions
- Add descriptions to all variables
- Include outputs for important resources
- Use modules for reusable components

**Example:**
```hcl
variable "stream_name" {
  description = "Name of the Kinesis Data Stream"
  type        = string
  
  validation {
    condition     = length(var.stream_name) > 0
    error_message = "Stream name cannot be empty"
  }
}
```

### Documentation
- Use clear, concise language
- Include code examples
- Update README.md if adding features
- Add inline comments for complex logic

## Pull Request Process

### PR Checklist
- [ ] Code follows project style guidelines
- [ ] Tests added/updated and passing
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] Branch is up-to-date with main
- [ ] PR description is complete

### PR Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing
Describe testing performed

## Related Issues
Fixes #issue_number
```

### Review Process
1. Automated checks must pass
2. At least one maintainer approval required
3. Address review comments
4. Maintainer will merge when ready

## Testing Guidelines

### Python Tests
```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# Coverage report
pytest --cov=python/src tests/
```

### Terraform Tests
```bash
# Format check
terraform fmt -check -recursive

# Validation
terraform validate

# Plan (no apply)
terraform plan
```

### Writing Tests
- Test one thing per test
- Use descriptive test names
- Include positive and negative cases
- Mock external dependencies

**Example:**
```python
def test_data_generator_creates_readings():
    """Test that DataGenerator creates valid sensor readings."""
    generator = DataGenerator(num_machines=1, sensors_per_machine=1)
    readings = generator.generate_batch(5)
    
    assert len(readings) == 5
    assert all(isinstance(r, SensorReading) for r in readings)
    assert all(r.value > 0 for r in readings)
```

## Documentation Contributions

### Adding Tutorial Steps
1. Follow the existing numbering scheme
2. Use the same format as existing docs
3. Include code examples
4. Add to TUTORIAL_MASTER.md index

### Updating README
- Keep it concise
- Update table of contents
- Test all code examples
- Update badges if needed

## Types of Contributions

### Bug Fixes
- Include reproduction steps in issue
- Add test that demonstrates the bug
- Fix the bug
- Verify test now passes

### New Features
- Discuss in issue first
- Follow existing patterns
- Add comprehensive tests
- Update documentation

### Documentation
- Fix typos and errors
- Improve clarity
- Add examples
- Update outdated information

### Infrastructure
- Terraform module improvements
- CI/CD enhancements
- Build/deployment scripts
- Development tools

## Getting Help

- **Documentation**: Check [docs/](docs/) first
- **Issues**: Search existing issues
- **Discussions**: Use GitHub Discussions
- **Questions**: Tag with `question` label

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Acknowledged in documentation

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to make this project better! 🎉
