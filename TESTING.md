# Testing

Run pytest functions with a full coverage report:

```sh
coverage run --source=picoproject -m pytest -v tests && coverage report -m
```

To generate a HTML report use:

```sh
coverage html
```

A detailed report will be created @ `picoproject/htmlcov/index.html`.
