"""
Overrides the `search_index` management command provided by django_elasticsearch_dsl.

Adds in the configurable `thread_count` and `chunk_size` that can be set
as environment variables.
"""

import time
from django_elasticsearch_dsl.management.commands import search_index
from django_elasticsearch_dsl.registries import registry
from django.conf import settings


class Command(search_index.Command):
    """Override django_elasticsearch_dsl `search_index` command to add configurable options."""

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    def _populate(self, models, options):
        parallel = options['parallel']
        for doc in registry.get_documents(models):
            self.stdout.write('setting log thresholds')

            self.es_conn.indices.put_settings(
                {
                    "index.search.slowlog.threshold.query.warn": settings.ELASTICSEARCH_LOG_SEARCH_SLOW_THRESHOLD_WARN,
                    "index.search.slowlog.threshold.query.info": settings.ELASTICSEARCH_LOG_SEARCH_SLOW_THRESHOLD_INFO,
                    "index.search.slowlog.threshold.query.trace":
                        settings.ELASTICSEARCH_LOG_SEARCH_SLOW_THRESHOLD_TRACE,
                    "index.search.slowlog.level": settings.ELASTICSEARCH_LOG_SEARCH_SLOW_LEVEL,

                    "index.indexing.slowlog.threshold.index.warn": settings.ELASTICSEARCH_LOG_INDEX_SLOW_THRESHOLD_WARN,
                    "index.indexing.slowlog.threshold.index.info": settings.ELASTICSEARCH_LOG_INDEX_SLOW_THRESHOLD_INFO,
                    "index.indexing.slowlog.threshold.index.trace":
                        settings.ELASTICSEARCH_LOG_INDEX_SLOW_THRESHOLD_TRACE,
                    "index.indexing.slowlog.level": settings.ELASTICSEARCH_LOG_INDEX_SLOW_LEVEL,
                },
                doc.Index.name
            )

            self.stdout.write("Indexing {} '{}' objects {}".format(
                doc().get_queryset().count() if options['count'] else "all",
                doc.django.model.__name__,
                "(parallel)" if parallel else "")
            )
            qs = doc().get_indexing_queryset()
            doc().update(
                qs,
                parallel=parallel,
                refresh=options['refresh'],
                thread_count=settings.ELASTICSEARCH_REINDEX_THREAD_COUNT,
                chunk_size=settings.ELASTICSEARCH_REINDEX_CHUNK_SIZE,
                request_timeout=settings.ELASTICSEARCH_REINDEX_REQUEST_TIMEOUT,
            )
            time.sleep(10)
