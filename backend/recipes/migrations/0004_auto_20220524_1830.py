# Generated by Django 2.2.19 on 2022-05-24 15:30

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_auto_20220518_2011'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredientrecipe',
            name='amount',
            field=models.IntegerField(default=1, help_text='Введите количество ингредиентов', validators=[django.core.validators.MinValueValidator(1)], verbose_name='Количество ингредиентов'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.IntegerField(help_text='Введите время приготовления', validators=[django.core.validators.MinValueValidator(1)], verbose_name='Время приготовления'),
        ),
        migrations.AddConstraint(
            model_name='favorite',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='unique_favorite'),
        ),
        migrations.AddConstraint(
            model_name='shoppingcart',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='unique_shoppingcart'),
        ),
    ]