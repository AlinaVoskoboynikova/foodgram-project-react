from colorfield.fields import ColorField
from django.db import models

from users.models import User


class Tag(models.Model):
    """Модель для тегов к рецепту."""
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Тег',
        help_text='Укажите тег для рецепта'
    )
    color = ColorField(
        unique=True,
        verbose_name='Цвет тега',
        help_text='Укажите цвет тега'
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name='Уникальный идентификатор',
        help_text='Укажите уникальный идентификатор тега'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиентов для рецепта."""
    name = models.CharField(
        max_length=200,
        verbose_name='Ингредиент',
        help_text='Укажите ингредиент для рецепта'
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения',
        help_text='Введите единицу измерения'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
        help_text='Выберете автора рецепта'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта',
        help_text='Укажите название рецепта'
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipes/image/',
        help_text='Выберите фото рецепта'
    )
    text = models.TextField(
        verbose_name='Текст рецепта',
        help_text='Введите текст рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        related_name='recipes',
        verbose_name='Ингредиенты',
        help_text='Выберите ингредиенты для рецепта'
    )
    tags = models.ManyToManyField(
        Tag,
        through='TagRecipe',
        verbose_name='Тег',
        help_text='Выберите тег для рецепта'
    )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления',
        help_text='Введите время приготовления'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    class Meta:
        ordering = ('-pub_date', )
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    """Модель ингредиентов в рецепте."""
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredientrecipes',
        verbose_name='Ингредиеты в рецепте',
        help_text='Добавьте ингредиенты'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredientrecipes',
        verbose_name='Рецепт',
        help_text='Выберите рецепт'
    )
    amount = models.IntegerField(
        default=1,
        verbose_name='Количество ингредиентов',
        help_text='Введите количество ингредиентов'
    )

    class Meta:
        verbose_name = 'Ингредиенты в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'

    def __str__(self):
        return f'{self.ingredient} {self.recipe}'


class TagRecipe(models.Model):
    """Модель тегов в рецепте."""
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='tagrecipes',
        verbose_name='Теги в рецепте',
        help_text='Добавьте теги'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='tagrecipes',
        verbose_name='Рецепт',
        help_text='Выберите рецепт')

    class Meta:
        verbose_name = 'Теги рецепта'
        verbose_name_plural = 'Теги рецепта'

    def __str__(self):
        return f'{self.tag} {self.recipe}'


class ShoppingСart(models.Model):
    """Модель корзины пользователя."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь',
        help_text='Выберите пользователя'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='carts',
        verbose_name='Рецепты',
        help_text='Выберите рецепты для добавления в корзины'
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

    def __str__(self):
        return f'{self.user} {self.recipe}'


class Favorite(models.Model):
    """Модель избранных рецептов пользователя."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        help_text='Выберите пользователя'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
        help_text='Выберите рецепт'
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return f'{self.recipe} {self.user}'


class Subscribe(models.Model):
    """Модель подписок."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
        help_text='Выберите пользователя-подписчика'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
        help_text='Выберите автора'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(fields=['user', 'following'],
                                    name='unique_subscribe')
        ]

    def __str__(self):
        return f'{self.user} {self.following}'
