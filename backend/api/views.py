from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from .pagination import PageToOffsetPagination
from django.http import HttpResponse
from django.db.models import F, Sum
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from django.views import View
from .models import (Ingredient, Recipe, Favorite,
                     ShoppingCart, RecipeIngredient)
from .serializers import (
    RecipeSerializer, IngredientSerializer,
    ShoppingCartSerializer, FavoriteSerializer,
)
from .permissions import IsAuthorOrReadOnly
from .filters import RecipeFilter


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = PageToOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsAuthorOrReadOnly,)

    class Meta:
        ordering = ['-id']

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        return [IsAuthorOrReadOnly(), IsAuthenticatedOrReadOnly()]

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        cart_item, created = ShoppingCart.objects.get_or_create(
            user=request.user, recipe=recipe)
        if not created:
            return Response({'error': 'Рецепт уже добавлен в корзину.'},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = ShoppingCartSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def remove_from_shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        cart_item = ShoppingCart.objects.filter(
            user=request.user, recipe=recipe)
        if cart_item.exists():
            cart_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        favor, created = Favorite.objects.get_or_create(
            user=request.user, recipe=recipe)
        if not created:
            return Response({'error': 'Рецепт уже добавлен в избранное.'},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = FavoriteSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def remove_from_favorites(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        favorite_item = Favorite.objects.filter(
            user=request.user, recipe=recipe)
        if favorite_item.exists():
            favorite_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        short_link = recipe.get_short_link(request)
        return Response({'short-link': short_link}, status=status.HTTP_200_OK)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = RecipeIngredient.objects.filter(
            recipe__in=user.shopping_cart.values('recipe')).values(
            name=F('ingredient__name'),
            measurement_unit=F('ingredient__measurement_unit')).annotate(
            amount=Sum('amount')
        )
        data = ['Список покупок:\n']
        for ingredient in ingredients:
            data.append(
                f'{ingredient["name"]} - '
                f'{ingredient["amount"]} '
                f'{ingredient["measurement_unit"]}'
            )
        content = '\n'.join(data)
        filename = 'Shopping_cart.txt'
        request = HttpResponse(content, content_type='text/plain')
        request['Content-Disposition'] = f'attachment; filename={filename}'
        return request


class RecipeRedirectView(View):
    def get(self, request, short_id):
        recipe_id = int(short_id, 16)
        return redirect(f'/recipes/{recipe_id}')
