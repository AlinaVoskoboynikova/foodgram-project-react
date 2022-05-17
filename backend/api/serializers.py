from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingСart, Subscribe, Tag, TagRecipe)
from users.models import User


class UserSerializer(UserCreateSerializer):
    """Создание сериализатора модели пользователя."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name',
                  'last_name', 'is_subscribed', 'password')
        write_only_fields = ('password',)
        read_only_fields = ('id',)

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        if Subscribe.objects.filter(
                user=request.user, following__id=obj.id).exists():
            return True
        else:
            return False


class IngredientSerializer(serializers.ModelSerializer):
    """Создание сериализатора модели продуктов."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Создание сериализатора продуктов в рецепте для чтения."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientAmountRecipeSerializer(serializers.ModelSerializer):
    """Создание сериализатора ингредиентов с количеством продуктов."""
    id = serializers.IntegerField(source='ingredient.id')

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class TagSerializer(serializers.ModelSerializer):
    """Создание сериализатора модели тегов."""
    class Meta:
        model = Tag
        fields = '__all__'


class FavoriteSerializer(serializers.Serializer):
    """Создание сериализатора избранных рецептов."""
    id = serializers.IntegerField()
    name = serializers.CharField()
    cooking_time = serializers.IntegerField()
    image = Base64ImageField(max_length=None, use_url=False,)


class ShoppingСartSerializer(serializers.Serializer):
    """Создание сериализатора корзины."""
    id = serializers.IntegerField()
    name = serializers.CharField()
    cooking_time = serializers.IntegerField()
    image = Base64ImageField(max_length=None, use_url=False,)


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра рецептов."""
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(
        source='ingredientrecipes',
        many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'name', 'image', 'text',
                  'ingredients', 'tags', 'cooking_time',
                  'is_in_shopping_cart', 'is_favorited')

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        if Favorite.objects.filter(user=request.user,
                                   recipe__id=obj.id).exists():
            return True
        else:
            return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        if ShoppingСart.objects.filter(
            user=request.user,
            recipe__id=obj.id
        ).exists():
            return True
        else:
            return False


class RecipeSerializerPost(serializers.ModelSerializer):
    """Сериализатор для создания и изменения рецептов."""
    author = UserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True)
    ingredients = IngredientAmountRecipeSerializer(
        source='ingredientrecipes', many=True)
    image = Base64ImageField(max_length=None, use_url=False,)

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'name', 'image', 'text',
                  'ingredients', 'tags', 'cooking_time',
                  'is_in_shopping_cart', 'is_favorited')

    def add_tags_and_ingredients(self, tags, ingredients, recipe):
        for tag_data in tags:
            recipe.tags.add(tag_data)
            recipe.save()
        for ingredient in ingredients:
            if not IngredientRecipe.objects.filter(
                    ingredient_id=ingredient['ingredient']['id'],
                    recipe=recipe).exists():
                ingredientrecipe = IngredientRecipe.objects.create(
                    ingredient_id=ingredient['ingredient']['id'],
                    recipe=recipe)
                ingredientrecipe.amount = ingredient['amount']
                ingredientrecipe.save()
            else:
                IngredientRecipe.objects.filter(
                    recipe=recipe).delete()
                recipe.delete()
                raise serializers.ValidationError(
                    'Данные продукты повторяются в рецепте!')
        return recipe

    def create(self, validated_data):
        author = validated_data.get('author')
        tags_data = validated_data.pop('tags')
        name = validated_data.get('name')
        image = validated_data.get('image')
        text = validated_data.get('text')
        cooking_time = validated_data.get('cooking_time')
        ingredients = validated_data.pop('ingredientrecipes')
        recipe = Recipe.objects.create(
            author=author,
            name=name,
            image=image,
            text=text,
            cooking_time=cooking_time,
        )
        recipe = self.add_tags_and_ingredients(tags_data, ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredientrecipes')
        TagRecipe.objects.filter(recipe=instance).delete()
        IngredientRecipe.objects.filter(recipe=instance).delete()
        instance = self.add_tags_and_ingredients(
            tags, ingredients, instance)
        super().update(instance, validated_data)
        instance.save()
        return instance


class RecipeSimpleSerializer(serializers.ModelSerializer):
    """Сериализатор для упрощенного отображения рецептов в подписках."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'cooking_time')


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для списка подписок."""
    recipes = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes(self, obj):
        request = self.context.get('request')
        if request.GET.get('recipes_limit'):
            recipes_limit = int(request.GET.get('recipes_limit'))
            queryset = Recipe.objects.filter(author__id=obj.id).order_by('id')[
                :recipes_limit]
        else:
            queryset = Recipe.objects.filter(author__id=obj.id).order_by('id')
        return RecipeSimpleSerializer(queryset, many=True).data

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        if Subscribe.objects.filter(
                user=request.user, following__id=obj.id).exists():
            return True
        else:
            return False

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author__id=obj.id).count()
