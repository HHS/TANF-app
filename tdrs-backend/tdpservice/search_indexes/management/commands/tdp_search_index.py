from django_elasticsearch_dsl.management.commands import search_index
from django_elasticsearch_dsl.registries import registry


class Command(search_index.Command):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    def _populate(self, models, options):
        parallel = options['parallel']
        for doc in registry.get_documents(models):
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
                thread_count=3,
                chunk_size=500,
            )
