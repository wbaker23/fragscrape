```
python -m build
python -m twine upload --repository testpypi dist/*
python -m pip install --index-url https://test.pypi.org/simple/ --no-deps fragscrape
```


## Notes
- Use Click for command line setup
- Write algorithm to find threshold similarity score for Parfumo graph
- Automate cookie rejection on Parfumo
- Make Parfumo work with headless driver
- Make fragrantica work with headless driver