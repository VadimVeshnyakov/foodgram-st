import json
from django.core.management.base import BaseCommand
from recipe.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка ингредиентов из JSON-файла'

    def handle(self, *args, **kwargs):
        with open('ingredients.json', encoding='utf-8') as file:
            data = json.load(file)
        existing_ingredients = set(
            Ingredient.objects.values_list('name', flat=True)
        )
        new_ingredients = [
            Ingredient(name=item['name'],
                       measurement_unit=item['measurement_unit'])
            for item in data if item['name'] not in existing_ingredients
        ]
        created_count = len(new_ingredients)
        if new_ingredients:
            Ingredient.objects.bulk_create(new_ingredients)

        self.stdout.write(self.style.SUCCESS(
            f"Данные успешно загружены! Добавлено записей: {created_count}"
        ))
