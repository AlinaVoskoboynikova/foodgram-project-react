from http import HTTPStatus

from django.http import HttpResponse
from django.shortcuts import get_list_or_404, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import filters, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.filters import RecipeFilters
from api.pagination import CustomPagination
from api.serializers import (FavoriteSerializer, IngredientSerializer,
                             RecipeSerializer, RecipeSerializerPost,
                             ShoppingСartSerializer, SubscriptionSerializer,
                             TagSerializer, UserSerializer)
from recipes.models import (Favorite, Ingredient, Recipe, ShoppingСart,
                            Subscribe, Tag)
from users.models import User


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для модели тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели продуктов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ['name', ]


class CreateUserView(UserViewSet):
    """Вьюсет для модели юзера."""
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.all()


class SubscribeViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели подписок."""
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return get_list_or_404(User, following__user=self.request.user)

    def create(self, request, *args, **kwargs):
        user_id = self.kwargs.get('users_id')
        user = get_object_or_404(User, id=user_id)
        Subscribe.objects.create(
            user=request.user, following=user)
        return Response(HTTPStatus.CREATED)

    def delete(self, request, *args, **kwargs):
        author_id = self.kwargs['users_id']
        user_id = request.user.id
        subscribe = get_object_or_404(
            Subscribe, user__id=user_id, following__id=author_id)
        subscribe.delete()
        return Response(HTTPStatus.NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели рецептов."""
    queryset = Recipe.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = CustomPagination
    filter_class = RecipeFilters
    filter_backends = [DjangoFilterBackend, ]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        else:
            return RecipeSerializerPost


class ShoppingСartViewSet(viewsets.ModelViewSet):
    """Вьюсет модели корзины."""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ShoppingСartSerializer
    queryset = ShoppingСart.objects.all()
    model = ShoppingСart

    def create(self, request, *args, **kwargs):
        recipe_id = int(self.kwargs['recipes_id'])
        recipe = get_object_or_404(Recipe, id=recipe_id)
        self.model.objects.create(
            user=request.user, recipe=recipe)
        return Response(HTTPStatus.CREATED)

    def delete(self, request, *args, **kwargs):
        recipe_id = self.kwargs['recipes_id']
        user_id = request.user.id
        object = get_object_or_404(
            self.model, user__id=user_id, recipe__id=recipe_id)
        object.delete()
        return Response(HTTPStatus.NO_CONTENT)

    @action(detail=False)
    def download_shopping_cart(self, request):
        ingredients = request.user.shopping_cart.all().values_list(
            'recipe__ingredients__name',
            'recipe__ingredients__ingredientrecipes__amount',
            'recipe__ingredients__measurement_unit')
        shopping_list = {}
        for ingredient in ingredients:
            name = ingredient[0]
            amount = ingredient[1]
            measurement_unit = ingredient[2]
            if name not in shopping_list:
                shopping_list[name] = {
                    'measurement_unit': measurement_unit,
                    'amount': amount
                }
            else:
                shopping_list[name]['amount'] += amount
        buy = []
        for item in shopping_list:
            buy.append(f'{item} - {shopping_list[item]["amount"]} '
                       f'{shopping_list[item]["measurement_unit"]} \n')
        response = HttpResponse(buy, 'Content-Type: text/plain')
        response['Content-Disposition'] = (
            'attachment; filename=shopping_cart.txt'
        )
        return response


class FavoriteViewSet(viewsets.ModelViewSet):
    """Вьюсет модели избранных рецептов."""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FavoriteSerializer
    queryset = Favorite.objects.all()
    model = Favorite

    def create(self, request, *args, **kwargs):
        recipe_id = int(self.kwargs['recipes_id'])
        recipe = get_object_or_404(Recipe, id=recipe_id)
        self.model.objects.create(
            user=request.user, recipe=recipe)
        return Response(HTTPStatus.CREATED)

    def delete(self, request, *args, **kwargs):
        recipe_id = self.kwargs['recipes_id']
        user_id = request.user.id
        object = get_object_or_404(
            self.model, user__id=user_id, recipe__id=recipe_id)
        object.delete()
        return Response(HTTPStatus.NO_CONTENT)
