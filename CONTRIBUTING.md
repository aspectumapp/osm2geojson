# Contributing to osm2geojson

Thank you for your interest in contributing to osm2geojson! This document provides guidelines and instructions for contributing to the project.

> **💡 Quick Start:** For a quick reference guide with common commands, see [DEVELOPMENT_QUICKSTART.md](DEVELOPMENT_QUICKSTART.md)

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git

### Getting Started

1. **Clone the repository with submodules:**

   ```bash
   git clone --recurse-submodules https://github.com/aspectumapp/osm2geojson.git
   cd osm2geojson
   ```

2. **Create a virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install the package in development mode with dev dependencies:**

   ```bash
   pip install -e ".[dev]"
   ```

4. **Install pre-commit hooks:**

   ```bash
   pre-commit install
   ```

   This will automatically run linters and formatters before each commit.

## Code Quality Standards

This project follows modern Python best practices and uses several tools to maintain code quality:

### Formatting

We use **Ruff** for both linting and formatting (replacing Black, isort, and flake8):

```bash
# Format code
ruff format .

# Check formatting without making changes
ruff format --check .
```

### Linting

```bash
# Run linter
ruff check .

# Auto-fix issues where possible
ruff check --fix .
```

### Type Checking

We use **mypy** for static type checking:

```bash
mypy osm2geojson
```

### Running All Quality Checks

```bash
# Run all checks before committing
ruff format --check .
ruff check .
mypy osm2geojson
```

## Testing

### Running Tests

We support both `unittest` (legacy) and `pytest` (modern):

```bash
# Using unittest (legacy)
python -m unittest discover

# Using pytest (recommended)
pytest

# Run with coverage
pytest --cov=osm2geojson --cov-report=html
```

### Running Specific Tests

```bash
# Single test file
pytest tests/main.py

# Single test class
pytest tests/main.py::TestOsm2GeoJsonMethods

# Single test method
pytest tests/main.py::TestOsm2GeoJsonMethods::test_barrier_wall
```

### Writing Tests

- Place test files in the `tests/` directory
- Name test files with `test_*.py` prefix
- Use descriptive test names that explain what is being tested
- Include docstrings for complex test cases
- Add test data files to `tests/data/` directory

Example test structure:

```python
def test_feature_description():
    """Test that feature X behaves correctly under condition Y."""
    # Arrange
    input_data = ...

    # Act
    result = function_under_test(input_data)

    # Assert
    assert result == expected_output
```

## Making Changes

### Branching Strategy

1. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bugfix-name
   ```

2. Make your changes, following the code quality standards above

3. Write or update tests as needed

4. Run the test suite to ensure all tests pass

5. Commit your changes with clear, descriptive commit messages

### Commit Messages

Follow these guidelines for commit messages:

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests when relevant

Examples:
```
Add support for custom polygon features

Fix issue #123: Handle empty geometry collections

Update documentation for xml2geojson parameters
```

## Pull Request Process

1. **Update documentation** if you've made changes to the API or functionality

2. **Ensure all tests pass** and add new tests for new features

3. **Update the README.md** if needed with details of changes to the interface

4. **Run all quality checks**:
   ```bash
   ruff format --check .
   ruff check .
   mypy osm2geojson
   pytest
   ```

5. **Submit your pull request** with:
   - A clear title describing the change
   - A detailed description of what changed and why
   - References to any related issues
   - Screenshots or examples if applicable

6. **Respond to feedback** from maintainers and update your PR as needed

## Code Style Guidelines

- **Line length**: Maximum 100 characters (enforced by Ruff)
- **Imports**: Organized automatically by Ruff (similar to isort)
- **Type hints**: Add type hints to new functions and gradually add to existing code
- **Docstrings**: Use Google-style docstrings for functions and classes
- **Naming conventions**:
  - Functions and variables: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_SNAKE_CASE`

## Adding Dependencies

When adding new dependencies:

1. Add them to the appropriate section in `pyproject.toml`:
   - Runtime dependencies: `dependencies` array
   - Development dependencies: `[project.optional-dependencies]` under `dev`

2. Specify minimum versions when possible

3. Document why the dependency is needed in your PR

## Updating OSM Polygon Features

To update the OSM polygon features to the latest version:

```bash
./update-osm-polygon-features.sh
```

## Questions or Need Help?

- Check existing [issues](https://github.com/aspectumapp/osm2geojson/issues)
- Open a new issue for bugs or feature requests
- Join discussions in pull requests

## License

By contributing, you agree that your contributions will be licensed under the same MIT License that covers the project.

## Recognition

All contributors will be recognized in the project. Thank you for helping make osm2geojson better!
