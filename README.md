```
python -m build
python -m twine upload --repository testpypi dist/*
python -m pip install --index-url https://test.pypi.org/simple/ --no-deps fragscrape
```

#### TODO
- Use Click to finish CLI setup for Fragrantica code


#### Future improvements
- Make Parfumo work with headless driver
- Make fragrantica work with headless driver