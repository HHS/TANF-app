"""Management command to process OWASP scan results from CircleCI."""

from tempfile import TemporaryFile
import logging
import requests

from django.core.files import File
from django.core.management import BaseCommand

from tdpservice.security.models import OwaspZapScan

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Command to process OWASP scan results."""

    help = 'Download, process and store OWASP ZAP scan results.'

    def add_arguments(self, parser):
        """Specify accepted arguments for this command."""
        parser.add_argument('build_num', type=int)
        parser.add_argument(
            '--backend-pass-count',
            default=0,
            type=int
        )
        parser.add_argument(
            '--backend-warn-count',
            default=0,
            type=int
        )
        parser.add_argument(
            '--backend-fail-count',
            default=0,
            type=int
        )
        parser.add_argument(
            '--frontend-pass-count',
            default=0,
            type=int
        )
        parser.add_argument(
            '--frontend-warn-count',
            default=0,
            type=int
        )
        parser.add_argument(
            '--frontend-fail-count',
            default=0,
            type=int
        )
        parser.add_argument(
            '--project-slug',
            default='raft-tech/TANF-app',
            type=str
        )

    def handle(self, *args, **options):
        """Given a build number, retrieve the OWASP Zap scan reports."""
        circle_build_num = options['build_num']
        circle_project_slug = options['project_slug']
        circle_api_url = (
            f'https://circleci.com/api/v2/project/gh/{circle_project_slug}/'
            f'{circle_build_num}/artifacts'
        )
        response = requests.get(circle_api_url)

        if response.status_code == 500:
            raise Exception("CircleCI API returned 500 error. The 'circle_build_num' number may be incorrect.")
        elif response.status_code == 404:
            raise Exception("CircleCI API returned 404 error. The 'circle_project_slug' number may be incorrect.")
        elif response.status_code != 200:
            raise Exception("CircleCI API returned an unexpected error.")

        artifacts = response.json().get('items', [])
        for artifact in artifacts:
            report_path = artifact.get('path')
            report_url = artifact.get('url')

            if not (report_path and report_url):
                raise ValueError(
                    f'Build {circle_build_num} has no valid artifacts for '
                    f'project {circle_project_slug}'
                )

            app_target = report_path.split('/')[0]

            # Determine the matching alert metrics keys
            prefix = app_target.lstrip('tdrs-')
            fail_count, pass_count, warn_count = [
                options.get(key, 0)
                for key in [
                    f'{prefix}_fail_count',
                    f'{prefix}_pass_count',
                    f'{prefix}_warn_count'
                ]
            ]

            # Download the HTML report to a temporary file that will be deleted
            # from the local filesystem after the report has been stored in S3.
            with TemporaryFile() as temp_file:
                report_response = requests.get(report_url, stream=True)
                for chunk in report_response.iter_content(chunk_size=4096):
                    temp_file.write(chunk)
                html_report = File(temp_file)

                # Record the completed scan along with any associated logging
                OwaspZapScan.objects.record_scan(
                    app_target,
                    html_report,
                    fail_count,
                    pass_count,
                    warn_count
                )
