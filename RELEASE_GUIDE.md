# Release Guide

This guide explains how to release a new version of osm2geojson to PyPI.

## Prerequisites

### One-Time PyPI Setup (Trusted Publishers)

Before you can publish, configure Trusted Publishers on PyPI (most secure method, no API tokens!):

1. **Log in to PyPI**: https://pypi.org/
2. **Go to project settings**: https://pypi.org/manage/project/osm2geojson/settings/publishing/
3. **Add Trusted Publisher** with these values:
   ```
   PyPI Project Name: osm2geojson
   Owner: aspectumapp
   Repository: osm2geojson
   Workflow name: pythonpublish.yml
   Environment name: (leave blank)
   ```
4. **Save** - That's it! No passwords or tokens needed.

## Release Process

### 1. Prepare the Release

```bash
# Make sure you're on main/master branch
git checkout master
git pull origin master

# Ensure everything is clean
make clean
make all  # Run all tests and checks
```

### 2. Update Version

Edit `pyproject.toml`:
```toml
[project]
version = "0.2.10"  # Update this
```

### 3. Test the Build

```bash
# Test that package builds correctly
make test-build

# Or manually:
python -m build
pip install dist/osm2geojson-*.whl  # Test installation
```

### 4. Update Documentation (Optional)

- Update `README.md` if there are notable changes
- Update `CHANGELOG.md` (if exists) with release notes
- Document any breaking changes

### 5. Commit and Tag

```bash
# Commit version bump
git add pyproject.toml
git commit -m "Release v0.2.10"

# Create git tag
git tag -a v0.2.10 -m "Release version 0.2.10"

# Push everything
git push origin master
git push origin v0.2.10
```

### 6. Create GitHub Release

1. **Go to GitHub**: https://github.com/aspectumapp/osm2geojson/releases/new
2. **Select tag**: Choose `v0.2.10`
3. **Release title**: `v0.2.10` or `Release 0.2.10`
4. **Description**: Add release notes (see template below)
5. **Click "Publish release"**

**This automatically triggers the PyPI publish workflow!** 🎉

### 7. Verify Publication

After ~2-5 minutes:

1. Check workflow: https://github.com/aspectumapp/osm2geojson/actions
2. Verify on PyPI: https://pypi.org/project/osm2geojson/
3. Test installation:
   ```bash
   pip install --upgrade osm2geojson
   python -c "import osm2geojson; print(osm2geojson.__version__)"
   ```

## Release Notes Template

```markdown
## What's New in v0.2.10

### ✨ New Features
- Added support for X
- Improved Y performance

### 🐛 Bug Fixes
- Fixed issue with Z (#123)
- Resolved problem where...

### 📚 Documentation
- Updated contributor guide
- Added examples for...

### 🔧 Internal Changes
- Migrated to pyproject.toml
- Added type hints
- Improved test coverage

### 🙏 Contributors
Thanks to @username1, @username2 for their contributions!

**Full Changelog**: https://github.com/aspectumapp/osm2geojson/compare/v0.2.9...v0.2.10
```

## Troubleshooting

### Build Fails Locally

```bash
# Clean everything and try again
make clean
pip install --upgrade build
python -m build
```

### GitHub Action Fails

**"Trusted publishing exchange failure"**
- Make sure Trusted Publisher is configured on PyPI
- Verify repository name, workflow name match exactly

**"Version already exists"**
- You forgot to update version in pyproject.toml
- Or someone already published this version

**"Missing files in package"**
- Check `pyproject.toml` [tool.setuptools.package-data]
- Verify submodules are checked out (should be automatic now)

### Wrong Version Published

If you accidentally publish the wrong version:

1. **Don't panic!** You can't delete PyPI releases (by design)
2. **Release a patch version**: v0.2.11 with fixes
3. **Mark old version as yanked** (doesn't delete, just discourages use):
   ```bash
   # Requires pypi credentials (one-time setup)
   pip install twine
   twine upload --repository pypi --skip-existing dist/*
   ```

## Emergency Rollback

If a bad release goes out:

1. **Yank the version on PyPI** (in project settings)
2. **Release a fixed version immediately**
3. **Update documentation** to warn users
4. **Announce** in issues/discussions

## Testing Pre-Release

To test before releasing to production PyPI:

1. **Use TestPyPI**: https://test.pypi.org/
2. **Modify workflow** temporarily to use TestPyPI
3. **Test installation** from TestPyPI
4. **Switch back** to production PyPI

## Version Numbering

We use [Semantic Versioning](https://semver.org/):

- **Major** (1.0.0): Breaking changes
- **Minor** (0.1.0): New features, backward compatible
- **Patch** (0.0.1): Bug fixes, backward compatible

Examples:
- `0.2.9` → `0.2.10`: Bug fixes
- `0.2.9` → `0.3.0`: New features
- `0.2.9` → `1.0.0`: Breaking changes

## Checklist

Before releasing, verify:

- [ ] All tests pass (`make test`)
- [ ] Code is formatted (`make format`)
- [ ] No linter errors (`make lint`)
- [ ] Type checking passes (`make type-check`)
- [ ] Version updated in `pyproject.toml`
- [ ] Documentation updated
- [ ] Build test passes (`make test-build`)
- [ ] Changelog updated (if exists)
- [ ] Git tag created
- [ ] Release notes prepared

## Quick Reference

```bash
# Complete release in one go
make clean
make all                           # Test everything
vim pyproject.toml                # Update version
make test-build                   # Test build
git add pyproject.toml
git commit -m "Release v0.2.10"
git tag -a v0.2.10 -m "Release version 0.2.10"
git push origin master --tags
# Then create GitHub Release (triggers PyPI publish)
```

## Help

- **PyPI Issues**: https://pypi.org/help/
- **Trusted Publishers**: https://docs.pypi.org/trusted-publishers/
- **GitHub Releases**: https://docs.github.com/en/repositories/releasing-projects-on-github

---

**Pro Tip**: Test the entire release process (except the final push) before doing it for real!
