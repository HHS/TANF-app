"""Serializers for parsing errors."""

from rest_framework import serializers
from .models import ParserError, DataFileSummary


class ParsingErrorSerializer(serializers.ModelSerializer):
    """Serializer for Parsing Errors."""

    def __init__(self, *args, **kwargs):
        """Override fields argument to control fields to be displayed."""
        super(ParsingErrorSerializer, self).__init__(*args, **kwargs)
        fields = kwargs['context']['request'].query_params.get('fields')
        if fields is not None:
            fields = [x.strip() for x in fields.split(',')]
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    class Meta:
        """Metadata."""

        model = ParserError
        fields = '__all__'


class DataFileSummarySerializer(serializers.ModelSerializer):
    """Serializer for Parsing Errors."""

    class Meta:
        """Metadata."""

        model = DataFileSummary
        fields = ['status', 'case_aggregates', 'datafile']
