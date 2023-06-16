"""Views for the parsers app."""
from tdpservice.users.permissions import IsApprovedPermission
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from .serializers import ParsingErrorSerializer
from .models import ParserError
import logging
import base64
from io import BytesIO
import xlsxwriter

logger = logging.getLogger()


class ParsingErrorViewSet(ModelViewSet):
    """Data file views."""

    queryset = ParserError.objects.all()
    serializer_class = ParsingErrorSerializer
    permission_classes = [IsApprovedPermission]

    def list(self, request, *args, **kwargs):
        """Override list to return xls file."""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(self._get_xls_serialized_file(serializer.data))

    def get_queryset(self):
        """Override get_queryset to filter by request url."""
        queryset = ParserError.objects.all()
        id = self.request.query_params.get('id', None)
        if id is not None:
            queryset = queryset.filter(id=id)
        file = self.request.query_params.get('file', None)
        if file is not None:
            queryset = queryset.filter(file=file)
        return queryset

    def _get_xls_serialized_file(self, data):
        """Return xls file created from the error."""
        row, col = 0, 0
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()

        report_columns = ['case_number',
                          'rpt_month_year',
                          'error_type',
                          'error_message',
                          'item_number',
                          'field_name',
                          'row_number',
                          'column_number']

        # write beta banner
        worksheet.write(row, col,
                        "Error reporting in TDP is still in development." +
                        "We'll be in touch when it's ready to use!" +
                        "For now please refer to the reports you receive via email")
        row, col = 2, 0
        # write csv header
        [worksheet.write(row, col, key) for col, key in enumerate(report_columns)]

        for i in data:
            row += 1
            col = 0
            for key in report_columns:
                worksheet.write(row, col, i[key])  # writes value by looking up data by key
                col += 1
        workbook.close()
        return {"data": data, "xls_report": base64.b64encode(output.getvalue()).decode("utf-8")}
