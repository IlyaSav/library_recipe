from django.core.management.base import BaseCommand
from accounts.models import Category

class Command(BaseCommand):
    help = 'Create initial recipe categories'

    def handle(self, *args, **options):
        categories = [
            'Завтраки',
            'Основные блюда',
            'Супы',
            'Салаты',
            'Закуски',
            'Десерты',
            'Напитки',
            'Выпечка',
            'Соусы',
            'Заготовки',
            'Вегетарианские',
            'Веганские',
            'Безглютеновые',
            'Безлактозные',
            'Кето',
            'Простые',
            'Средней сложности',
            'Сложные',
            'Мясные',
            'Рыбные',
            'Овощные',
            'Фруктовые',
            'Бобовые',
            'Молочные продукты',
            'Весна',
            'Лето',
            'Осень',
            'Зима',
            'Запекание',
            'Жарка',
            'Варка',
            'Паста и тесто',
            'Гриль',
            'Новогодние блюда',
            'Постные блюда',
            'Детские рецепты',
            'Праздничные угощения',
        ]
        for cat_name in categories:
            category, created = Category.objects.get_or_create(name=cat_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Category "{cat_name}" created.'))
            else:
                self.stdout.write(f'Category "{cat_name}" already exists.')
