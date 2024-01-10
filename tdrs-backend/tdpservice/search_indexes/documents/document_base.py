"""Elasticsearch base document mappings."""

from django_elasticsearch_dsl import fields, Document
from tdpservice.data_files.models import DataFile


class DocumentBase(Document):
    """Elastic search base document to be overridden."""

    datafile = fields.ObjectField(properties={
                      'id': fields.IntegerField(),
                      'created_at': fields.DateField(),
                      'version': fields.IntegerField(),
                      'quarter': fields.TextField(),
                      'year': fields.IntegerField(),
                      'stt': fields.ObjectField(properties={
                          'name': fields.CharField(max_length=1000),
                          'type': fields.CharField(max_length=200),
                          'stt_code': fields.CharField(max_length=3)
                      })
                  })

    def get_instances_from_related(self, related_instance):
        """Return correct instance."""
        if isinstance(related_instance, DataFile):
            return related_instance
