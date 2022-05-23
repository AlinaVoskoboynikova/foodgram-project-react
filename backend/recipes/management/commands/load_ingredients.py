import json

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    """Класс для загрузки ингредиентов в БД."""
    def handle(self, *args, **options):
        data_file = open('data/ingredients.json', encoding='utf-8').read()
        ingredients_data = json.load(data_file)
        for ingredient in ingredients_data:
            name = ingredient['name']
            measurement_unit = ingredient['measurement_unit']
            Ingredient.objects.create(
                name=name,
                measurement_unit=measurement_unit
            )
