from django.core.management.base import BaseCommand
from accounts.models import Recipe

class Command(BaseCommand):
    help = 'Автоматически заполняет slug для всех рецептов, у которых он пустой.'

    def handle(self, *args, **options):
        updated = 0
        for recipe in Recipe.objects.filter(slug__isnull=True) | Recipe.objects.filter(slug=''):
            recipe.save()  # save() сгенерирует slug
            updated += 1
        self.stdout.write(self.style.SUCCESS(f'Обновлено рецептов: {updated}')) 