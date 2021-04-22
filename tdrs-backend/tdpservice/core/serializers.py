# """Serialize core data."""
# import logging
# 
# from rest_framework import serializers
# 
# from ..reports.models import ReportFile
# from ..users.models import User
# 
# logger = logging.getLogger()
# 
# class FileEventSerializer(serializers.Serializer):
#     """Serializer for individual File objects sent as part of Log Events."""
#     report = serializers.PrimaryKeyRelatedField(queryset=ReportFile.objects.all())
#     
#     def create(self, validated_data):
#         logger.info(validated_data)
# 
# 
# class EventLogSerializer(serializers.Serializer):
#     """Serializer for Log Events"""
#     user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
#     type = serializers.CharField()
#     message = serializers.CharField()
#     activity = serializers.CharField()
#     timestamp = serializers.DateTimeField()
#     files = FileEventSerializer(many=True)
# 
# 
#     def create(self, validated_data):
#         logger.info(validated_data)
