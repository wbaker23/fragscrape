# Greeting

Hello! This repository is a work in progress, 1.0.0 release is coming soon

## Build Process

```bash
python -m build
python -m twine upload --repository testpypi dist/*
python -m pip install --index-url https://test.pypi.org/simple/ --no-deps fragscrape
```

## TODO

- Use Click to finish CLI setup for Fragrantica code
- Add license
- Add date to Parfumo votes table to prevent excess scraping

## Future improvements

- Make Parfumo work with headless driver
- Make fragrantica work with headless driver
