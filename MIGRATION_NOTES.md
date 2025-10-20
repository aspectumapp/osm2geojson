# Migration Notes

This document tracks changes from the old workflow to the new modernized workflow.

## Removed Files

### `lint.sh` (Removed)

**Old usage:**
```bash
./lint.sh
```

**New replacement:**
```bash
make lint          # Run linter (Ruff - much faster!)
make format        # Auto-format code
make all           # Run all checks
```

**Why removed:**
- Used old `flake8` (slow)
- Ruff is 10-100x faster
- Make commands are more intuitive
- Pre-commit hooks run automatically

---

### `release.sh` (Removed)

**Old usage:**
```bash
./release.sh       # Manual release
```

**New replacement:**
```bash
# Automated via GitHub Actions
git tag v0.2.10
git push origin v0.2.10
# Create GitHub Release → Automatically publishes to PyPI
```

**Or use Make (if you need to test release build):**
```bash
make test-build    # Test the build
# See RELEASE_GUIDE.md for complete process
```

**Why removed:**
- Manual, error-prone process
- GitHub Actions automates everything
- Trusted Publishers = no passwords needed
- Built-in testing and verification

---

## Old → New Command Reference

| Old Command | New Command | Notes |
|-------------|-------------|-------|
| `./lint.sh` | `make lint` | Uses Ruff (much faster) |
| `python setup.py develop` | `pip install -e ".[dev]"` | Modern editable install |
| `python setup.py sdist` | `python -m build` | PEP 517 compliant |
| `flake8 .` | `ruff check .` | 10-100x faster |
| Manual release | GitHub Release | Fully automated |
| `python -m unittest` | `pytest` | Modern testing (unittest still works) |

---

## Setup Comparison

### Old Setup
```bash
git clone https://github.com/aspectumapp/osm2geojson.git
cd osm2geojson
python setup.py develop
./lint.sh          # Check code
python -m unittest  # Run tests
./release.sh       # Release (manual)
```

### New Setup
```bash
git clone --recurse-submodules https://github.com/aspectumapp/osm2geojson.git
cd osm2geojson
make setup         # One command!
make all           # Check everything
# Release via GitHub Release (automatic)
```

---

## Configuration Files

### Old (REMOVED)
- ❌ `setup.py` - Project metadata
- ❌ `setup.cfg` - Additional config
- ❌ `requirements.txt` - Dependencies
- ❌ `requirements-dev.txt` - Dev dependencies
- ❌ `MANIFEST.in` - Package data
- ❌ `lint.sh` - Linting script
- ❌ `release.sh` - Manual release script

### New
- ✅ `pyproject.toml` - **Everything in one file!**
- ✅ `Makefile` - Common tasks
- ✅ `.pre-commit-config.yaml` - Automated checks

---

## Benefits of New Approach

### Speed
- **Ruff is 10-100x faster** than flake8
- **Make commands** are instant shortcuts
- **Pre-commit** catches issues before CI

### Automation
- **No manual steps** for releasing
- **GitHub Actions** handle testing and publishing
- **Trusted Publishers** = no passwords

### Standards
- **PEP 621** compliant (pyproject.toml)
- **Modern tooling** (Ruff, pytest, mypy)
- **Industry best practices**

### Developer Experience
- **One command setup**: `make setup`
- **Clear documentation**: CONTRIBUTING.md
- **Helpful tools**: Make, pre-commit

---

## Troubleshooting

### "I was using lint.sh"
Use `make lint` or `ruff check .`

### "I was using release.sh"
See `RELEASE_GUIDE.md` - now it's automated via GitHub Releases

### "Where's setup.py / requirements.txt?"
**Removed**. Modern Python uses `pyproject.toml` exclusively (PEP 621). All metadata, dependencies, and tool config are now in one file.

### "I want the old way back"
The old scripts are in git history if you need them:
```bash
git show HEAD~1:lint.sh > lint.sh.old
git show HEAD~1:release.sh > release.sh.old
```

But we recommend using the new tools - they're much better! 😊

---

## Questions?

- See `CONTRIBUTING.md` for development workflow
- See `RELEASE_GUIDE.md` for release process
- See `MODERNIZATION.md` for what changed and why
- Open an issue if you need help migrating
