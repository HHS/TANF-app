"""Elasticsearch base document mappings."""

from django_elasticsearch_dsl import fields
from tdpservice.data_files.models import DataFile

class DocumentBase:
    """Elastic search model mapping for a parsed SSP M1 data file."""

    datafile = fields.ObjectField(properties={
                      'pk': fields.IntegerField(),
                      'created_at': fields.DateField(),
                      'version': fields.IntegerField(),
                      'quarter': fields.TextField()
                  })

    def get_instances_from_related(self, related_instance):
        """Return correct instance."""
        if isinstance(related_instance, DataFile):
            return related_instance
