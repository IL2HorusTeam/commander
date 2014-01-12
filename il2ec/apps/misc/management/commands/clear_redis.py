# -*- coding: utf-8 -*-
"""
Implement 'clear_redis' Django management command.
"""
from __future__ import unicode_literals

import redis

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    A management command which clears all Redis databases.
    """
    help = "Clear all Redis databases"

    def handle(self, *args, **kwargs):
        r = redis.Redis(host=settings.REDIS_HOST,
                        port=settings.REDIS_PORT,
                        password=settings.REDIS_PASSWORD)
        r.flushall()
