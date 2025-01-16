from django.contrib import admin

from .models import (Ingredient, Recipe, RecipeIngredient,
                     Favorite, ShoppingCart)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    min_num = 1
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    '''Настройка отображения рецептов.'''

    inlines = (RecipeIngredientInline,)
    list_display = (
        'name', 'author_username', 'get_favorite_count',
    )
    list_filter = ('name', 'author__username',)
    search_fields = ('name', 'author__username',)

    def author_username(self, obj):
        return obj.author.username

    def get_favorite_count(self, obj):
        return obj.favorited_by.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    '''Настройка отображения ингредиентов.'''

    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    '''Настройки отображения избранных у пользователей.'''

    list_display = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    '''Настройки отображения списка покупок.'''

    list_display = ('user', 'recipe')
