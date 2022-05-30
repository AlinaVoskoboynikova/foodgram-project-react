from http import HTTPStatus

from api.filters import RecipeFilters
from api.pagination import CustomPagination
from api.serializers import (FavoriteSerializer, IngredientSerializer,
                             RecipeSerializer, RecipeSerializerPost,
                             ShoppingCartSerializer, SubscriptionSerializer,
                             TagSerializer, UserSerializer)
from django.http import HttpResponse
from django.shortcuts import get_list_or_404, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from recipes.models import (Favorite, Ingredient, IngredientRecipe,
                            Recipe, ShoppingCart, Subscribe, Tag)
from rest_framework import filters, permissions, viewsets
from rest_framework.response import Response
from users.models import User
from django.db.models import Sum


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для модели тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели продуктов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny, )
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('name', )


class CreateUserView(UserViewSet):
    """Вьюсет для модели юзера."""
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.all()


class SubscribeViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели подписок."""
    serializer_class = SubscriptionSerializer
    permission_classes = (permissions.IsAuthenticated, )
    pagination_class = CustomPagination

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
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    pagination_class = CustomPagination
    filter_class = RecipeFilters
    filter_backends = (DjangoFilterBackend, )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return RecipeSerializerPost


class ShoppingCartViewSet(viewsets.ModelViewSet):
    """Вьюсет модели корзины."""
    permission_classes = (permissions.IsAuthenticated, )
    pagination_class = CustomPagination
    serializer_class = ShoppingCartSerializer
    queryset = ShoppingCart.objects.all()
    model = ShoppingCart

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

    @staticmethod
    def canvas_method(dictionary):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = (
            'attachment; filename = "shopping_cart.pdf"'
        )
        begin_position_x, begin_position_y = 40, 650
        sheet = canvas.Canvas(response, pagesize=A4)
        pdfmetrics.registerFont(TTFont('FreeSans',
                                       'data/FreeSans.ttf'))
        sheet.setFont('FreeSans', 50)
        sheet.setTitle('Список покупок')
        sheet.drawString(begin_position_x,
                         begin_position_y + 40, 'Список покупок: ')
        sheet.setFont('FreeSans', 24)
        for number, item in enumerate(dictionary, start=1):
            if begin_position_y < 100:
                begin_position_y = 700
                sheet.showPage()
                sheet.setFont('FreeSans', 24)
            sheet.drawString(
                begin_position_x,
                begin_position_y,
                f'{number}.  {item["ingredient__name"]} - '
                f'{item["ingredient_total"]}'
                f' {item["ingredient__measurement_unit"]}'
            )
            begin_position_y -= 30
        sheet.showPage()
        sheet.save()
        return response

    def download_shopping_cart(self, request):
        result = IngredientRecipe.objects.filter(
            recipe__carts__user=request.user).values(
            'ingredient__name', 'ingredient__measurement_unit').order_by(
                'ingredient__name').annotate(ingredient_total=Sum('amount'))
        return self.canvas_method(result)


class FavoriteViewSet(viewsets.ModelViewSet):
    """Вьюсет модели избранных рецептов."""
    permission_classes = (permissions.IsAuthenticated, )
    pagination_class = CustomPagination
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
