# Project migrations best practices

## Indexing

- If some column is going to be queried repeatedly then, create the database indexes on that column.
- Django migration has built-in support for creating indexes in database.
- If multiple columns are going to be queries together then index_together can be used to create composite indexes.
- Different database supports different kind of indexes with various characteristics. Research on it and apply the best suitable index on the database tables.
- Tools such as pgbadger can be used to analyse the query pattern on the production.
- PostgreSQL has support for different kind of indexes which can outperform the performance in various conditions and workloads. Research about it for other databases and apply the best one for the application.

## Check before migration

Check django [migration transactions](https://docs.djangoproject.com/en/3.2/topics/migrations/#transactions) details for database and access the behavior on what will happen in case of server network lost between the server running the migration and db, server went out of memory, server freeze etc behaviors.