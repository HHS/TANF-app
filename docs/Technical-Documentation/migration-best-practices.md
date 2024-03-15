# Project migrations and database best practices

## Indexing

- If some column is going to be queried repeatedly then, create the database indexes on that column.
- Django migration has built-in support for creating indexes in database.
- If multiple columns are going to be queried together then index_together can be used to create composite indexes.
- Tools such as pgbadger can be used to analyse the query pattern on the production.
- PostgreSQL has support for different kind of indexes which can outperform the performance in various conditions and workloads. Research about it for other databases and apply the best one for the application.

## Naming

Migrations have to be named as follows:

{migration number}_{model_name}_{change being applied}

E.g:

```shell
0002_datafilesumary_change_pk_to_uuid.py
```


## Data migration

It is possible to create/add data in the migration. This is called data migration and is a feature available in Django, however, it has it's own shortcomings and should be avoided.

## Version control

All migrations shall be version controlled. Each PR should only include one migration. This ensures better control over the model changes and gives a better option to revert changes back to previous version.

However, in cloud.gov the database has limited disk space. Since alter/add transactions in one migration need to cache the status in disk and then apply the changes, it is strongly suggested to limit the number of transactions and changes in one migration. 

Considering notes above, we conclude that there is a tradeoff between the number of migrations and the number of changes in one migration. One should be careful with this tradeoff specifically in apps that have larger database tables such as search_indexes.

## Back up before migration

Before applying any new migration into production, take a full backup from the DB.

## Check before migration

Check django [migration transactions](https://docs.djangoproject.com/en/3.2/topics/migrations/#transactions) details for database and assess the behavior on what will happen in case of server network lost between the server running the migration and db, server went out of memory, server freeze etc behaviors.

## Useful commands

### List the existing migrations

```python
from django.db.migrations.recorder import MigrationRecorder

existing_migration = MigrationRecorder.Migration.objects.all()
for migration in existing_migration:
    print(migration)
```

will output lines similar to:

```
.
..
Migration 0007_ssp_m1_ssp_m2_ssp_m3 for search_indexes                       
Migration 0038_user_access_requested_date for users
Migration 0008_auto_20230522_1850 for search_indexes
Migration 0002_alter_parsererror_error_type for parsers
Migration 0003_auto_20230518_1339 for parsers
Migration 0004_parsererror_object_uuid for parsers
Migration 0005_auto_20230601_1510 for parsers
Migration 0006_alter_parsererror_item_number for parsers
Migration 0009_auto_20230525_1959 for search_indexes
Migration 0010_add_tmp_uuid for search_indexes
Migration 0039_alter_user_options for users
Migration 0011_gen_uuid for search_indexes
Migration 0012_set_uuid_pk for search_indexes
Migration 0013_rename_uuid for search_indexes
Migration 0014_auto_20230707_1952 for search_indexes
Migration 0006_auto_20230726_1448 for parsers
Migration 0015_auto_20230724_1830 for search_indexes
Migration 0016_auto_20230803_1721 for search_indexes
Migration 0006_auto_20230810_1500 for parsers
```
