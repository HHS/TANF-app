"""Management command to process OWASP scan results from CircleCI."""

import logging
import requests
import os

from django.core.management import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Command to process OWASP scan results."""

    help = 'Download, process and store OWASP ZAP scan results.'

    def add_arguments(self, parser):
        """Accepted argument(s) for this command."""
        parser.add_argument('build_num', type=int)
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
        results = [artifact['url'] for artifact in response.json()['items']]
        print(results)
