from django.core.management.base import BaseCommand
from accounts.models import Recipe
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Автоматически заполняет пустые slug у рецептов на основе title (уникально)'

    def handle(self, *args, **options):
        updated = 0
        for recipe in Recipe.objects.all():
            if not recipe.slug:
                base_slug = slugify(recipe.title)
                slug = base_slug
                i = 1
                while Recipe.objects.filter(slug=slug).exclude(id=recipe.id).exists():
                    slug = f"{base_slug}-{i}"
                    i += 1
                recipe.slug = slug
                recipe.save()
                updated += 1
                self.stdout.write(self.style.SUCCESS(f'Обновлён рецепт {recipe.id}: {slug}'))
        if updated == 0:
            self.stdout.write(self.style.WARNING('Нет рецептов с пустым slug.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Готово! Обновлено {updated} рецептов.')) 