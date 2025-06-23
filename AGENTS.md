# Repository Guidelines

This repository provides a small Python utility for visualizing variable video bitrate using `ffprobe` and `matplotlib`.

## Coding Style
- Target Python 3.10+ and use type annotations.
- Keep line length under 88 characters.
- Format changes with `black`.

## Testing
Run a basic syntax check after making changes:

```bash
python -m py_compile main.py
```

## Usage
Install dependencies and run the script:

```bash
pip install -r requirements.txt
python main.py VIDEO
```
