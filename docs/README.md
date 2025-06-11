# FabricPy Documentation

This directory contains the Sphinx documentation for FabricPy, with automatic generation from Google-style docstrings.

## Building Documentation

### Quick Start
```bash
# Build HTML documentation
make html

# View the documentation
open _build/html/index.html  # macOS
# or
xdg-open _build/html/index.html  # Linux
```

### Available Commands

| Command | Description |
|---------|-------------|
| `make html` | Build HTML documentation |
| `make apidoc` | Regenerate API docs from source code |
| `make clean` | Clean build directory |
| `make latexpdf` | Build PDF documentation |
| `make linkcheck` | Check all external links |

### Automated Script
```bash
# Interactive documentation generation
python generate_docs.py
```

## Common Issues

### "Builder name 'build' not registered"
❌ **Wrong:** `make build`  
✅ **Correct:** `make html`

The Sphinx Makefile uses specific builder names like `html`, `latex`, `pdf`, etc. There is no generic `build` target.

### Missing Dependencies
If you get import errors, install the required packages:
```bash
pip install sphinx sphinx-rtd-theme
```

## File Structure

- `conf.py` - Sphinx configuration with Google docstring support
- `index.rst` - Main documentation index
- `api.rst` - Auto-generated API reference
- `quickstart.rst` - Getting started guide
- `_build/html/` - Generated HTML output (after running `make html`)

## Configuration Features

- ✅ Google-style docstring parsing (Napoleon extension)
- ✅ Automatic API documentation generation
- ✅ Cross-references and type hints
- ✅ Code syntax highlighting
- ✅ Search functionality
- ✅ Mobile-responsive theme

## Updating Documentation

When you add new modules or update docstrings:

1. Regenerate API docs: `make apidoc`
2. Build HTML: `make html`
3. Or use the automated script: `python generate_docs.py`
