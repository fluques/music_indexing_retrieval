from django.core.management.base import BaseCommand
from django.urls import get_resolver, URLPattern, URLResolver
from django.conf import settings

class Command(BaseCommand):
    help = 'Lists all URL patterns in the project'

    def handle(self, *args, **kwargs):
        self.stdout.write("URL Pattern | View Name | Name")
        self.stdout.write("-" * 50)
        resolver = get_resolver(settings.ROOT_URLCONF)
        self.list_urls_recursive(resolver.url_patterns)

    def list_urls_recursive(self, url_patterns, prefix=''):
        for pattern in url_patterns:
            if isinstance(pattern, URLPattern):
                self.stdout.write(f"{prefix}{pattern.pattern} | {pattern.callback.__name__} | {pattern.name or ''}")
            elif isinstance(pattern, URLResolver):
                new_prefix = prefix + str(pattern.pattern)
                self.list_urls_recursive(pattern.url_patterns, new_prefix)