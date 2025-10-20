# Development Quick Start

Quick reference for common development tasks in osm2geojson.

## ⚡ One-Time Setup

```bash
# Clone with submodules
git clone --recurse-submodules https://github.com/aspectumapp/osm2geojson.git
cd osm2geojson

# Complete setup (installs deps + pre-commit hooks)
make setup

# Or manually:
pip install -e ".[dev]"
pre-commit install
```

## 🔨 Daily Development

### Before Starting Work
```bash
git checkout -b feature/my-feature
```

### Code Quality (Auto-runs on commit via pre-commit)
```bash
make format      # Format code with ruff
make lint        # Check code with ruff
make type-check  # Type check with mypy
```

### Testing
```bash
make test                # Run all tests
make test-coverage       # Run tests with coverage report
pytest tests/main.py     # Run specific test file
pytest -k test_name      # Run specific test
pytest -v                # Verbose output
```

### Before Committing
```bash
# Pre-commit hooks will run automatically, but you can run manually:
make all                 # Run format, lint, type-check, and test
```

## 📝 Common Workflows

### Adding a New Feature

1. **Create branch**: `git checkout -b feature/my-feature`
2. **Write code**: Add your feature
3. **Add tests**: Write tests in `tests/`
4. **Check quality**: `make all`
5. **Commit**: `git commit -m "Add: my feature"`
6. **Push**: `git push origin feature/my-feature`
7. **Create PR**: Use the PR template

### Fixing a Bug

1. **Create branch**: `git checkout -b fix/bug-description`
2. **Write test**: Add failing test that reproduces bug
3. **Fix bug**: Make the test pass
4. **Check quality**: `make all`
5. **Commit**: `git commit -m "Fix: bug description"`
6. **Push and PR**

### Updating Dependencies

We use some configuration files which are supported by the community. These files don't update often, but in case of update we should synchronise our local configs using this

```bash
./update-osm-polygon-features.sh
```

## 🐛 Debugging

### Run Tests with Debug Output
```bash
pytest -v --tb=long           # Verbose with long tracebacks
pytest --pdb                  # Drop into debugger on failure
pytest -k test_name -s        # Show print statements
```

### Check Coverage for Specific Files
```bash
pytest --cov=osm2geojson.main --cov-report=term-missing
```

### Type Check Specific File
```bash
mypy osm2geojson/main.py
```

## 🚀 Release Process (Maintainers)

1. **Update version** in `pyproject.toml`
2. **Update CHANGELOG** (if exists)
3. **Commit**: `git commit -m "Release v0.2.10"`
4. **Tag**: `git tag -a v0.2.10 -m "Release v0.2.10"`
5. **Push**: `git push && git push --tags`
6. **Create GitHub Release**: This triggers PyPI publish

## 🔧 Tool Reference

| Tool | Purpose | Command |
|------|---------|---------|
| **ruff** | Lint + Format | `ruff check .` / `ruff format .` |
| **mypy** | Type checking | `mypy osm2geojson` |
| **pytest** | Testing | `pytest` |
| **pre-commit** | Git hooks | `pre-commit run --all-files` |

## 📚 Documentation

- **Full Guide**: See `CONTRIBUTING.md`
- **Modernization**: See `MODERNIZATION.md`
- **Project README**: See `README.md`

## ⚙️ Configuration Files

- `pyproject.toml` - Project metadata, dependencies, tool config
- `.pre-commit-config.yaml` - Pre-commit hooks
- `.github/workflows/` - CI/CD pipelines
- `Makefile` - Common tasks

## 💡 Pro Tips

1. **Use Make**: `make <tab>` to see all available commands
2. **Pre-commit**: Install hooks once, forget about formatting
3. **Coverage HTML**: `make test-coverage` creates `htmlcov/index.html`
4. **Type Hints**: Add them as you go, don't need 100% coverage
5. **Tests**: Prefer pytest fixtures over unittest setUp methods

## ❓ Getting Help

- **Issues**: https://github.com/aspectumapp/osm2geojson/issues
- **Discussions**: GitHub Discussions
- **Contributing**: See `CONTRIBUTING.md`

---

**Quick Links:**
- 📖 [Contributing Guide](CONTRIBUTING.md)
- 🔄 [Modernization Summary](MODERNIZATION.md)
- 📋 [Issue Templates](.github/ISSUE_TEMPLATE/)
- 🔀 [PR Template](.github/PULL_REQUEST_TEMPLATE.md)
