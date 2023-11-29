#!/usr/bin/env python

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import BaseCommand

User = get_user_model()

email = "dev@test.com"
pswd = "pass"
first = "Jon"
last = "Tester"

class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            user = User.objects.get(username=email)
            print(f"Found {vars(user)}")
        except User.DoesNotExist:
            group = Group.objects.get(name="Developer")
            user = User.objects.create(username=email,
                                       email=email,
                                       password=pswd,
                                       first_name=first,
                                       last_name=last,
                                       account_approval_status="Approved")
            user.groups.add(group)
            print(f"Created {vars(user)}")
    
