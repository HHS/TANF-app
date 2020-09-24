# Graph Models ERD

**Description**

In order to produce an ERD of the current database architecture, we have introduced GraphViz and a suite of Python tools to automatically generate one.

This was done using the Django Extension [Graph Models](https://django-extensions.readthedocs.io/en/latest/graph_models.html#graph-models)

In order to generate an ERD, first navigate the root of the backend codebase (from the project root)

```
cd tdrs-backend
```

Next, run the project locally:

```
docker-compose up -d --build
```
Once the project is running, run the following command:
```
docker-compose run web sh -c "python manage.py graph_models --pygraphviz -a -g -o tdp-erd.png"
```

Lastly, open the file

```
open tdp-erd.png
```
