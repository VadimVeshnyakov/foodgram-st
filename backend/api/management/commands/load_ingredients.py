import json
from django.core.management.base import BaseCommand
from api.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка ингредиентов из JSON-файла'

    def handle(self, *args, **kwargs):
        with open('ingredients.json', encoding='utf-8') as file:
            data = json.load(file)

        for item in data:
            Ingredient.objects.get_or_create(
                name=item['name'],
                measurement_unit=item['measurement_unit']
            )

        self.stdout.write(self.style.SUCCESS("Данные успешно загружены!"))
