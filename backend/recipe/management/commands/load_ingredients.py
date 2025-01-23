import json
from django.core.management.base import BaseCommand
from recipe.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка ингредиентов из JSON-файла'

    def handle(self, *args, **kwargs):
        with open('ingredients.json', encoding='utf-8') as file:
            new_ingredients = [
                Ingredient(**item)
                for item in json.load(file)
            ]
        created_ingredients = Ingredient.objects.bulk_create(
            new_ingredients, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS(
            'Данные успешно загружены! '
            f'Добавлено записей: {len(created_ingredients)}'
        ))
