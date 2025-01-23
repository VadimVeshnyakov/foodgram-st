from django.contrib import admin
from django.utils.safestring import mark_safe
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import (Ingredient, Recipe, RecipeIngredient,
                     Favorite, ShoppingCart, User, Subscription)


@admin.register(User)
class UsersAdmin(BaseUserAdmin):
    """Возможность редактировать и удалять все данные о пользователях.
    Поиск по адресу электронной почты и имени пользователя."""

    list_display = (
        'id',
        'username',
        'email',
        'full_name',
        'display_avatar',
        'recipe_count',
        'is_staff'
    )
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_active')

    @admin.display(description='ФИО')
    def full_name(self, obj):
        return f'{obj.first_name} {obj.last_name}'.strip()

    @mark_safe
    @admin.display(description='Аватар')
    def display_avatar(self, obj):
        if obj.avatar:
            return (f'<img src="{obj.avatar.url}" style="height: '
                    '50px;width: 50px; border-radius: 50%;">')
        return "—"

    @admin.display(description='Число рецептов')
    def recipe_count(self, obj):
        return obj.recipes.count()


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Настройки отображения данных о подписках."""

    list_display = ('user', 'author')


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    min_num = 1
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Настройка отображения рецептов."""

    inlines = (RecipeIngredientInline,)
    list_display = (
        'id', 'name', 'cooking_time', 'author_username',
        'get_favorite_count', 'display_ingredients', 'display_image',
    )
    list_filter = ('name', 'author__username',)
    search_fields = ('name', 'author__username',)

    def author_username(self, recipe):
        return recipe.author.username

    def get_favorite_count(self, recipe):
        return recipe.favorites.count()
    get_favorite_count.short_description = 'В избранном'

    @mark_safe
    @admin.display(description='Ингредиенты')
    def display_ingredients(self, recipe):
        ingredients = recipe.recipe_ingredients.select_related('ingredient')
        return '<br>'.join(
            (f'{ri.ingredient.name} — {ri.amount} '
               f'{ri.ingredient.measurement_unit}')
            for ri in ingredients
        )

    @mark_safe
    @admin.display(description='Изображение')
    def display_image(self, recipe):
        """Отображение изображения в виде миниатюры."""
        if recipe.image:
            return f'<img src="{recipe.image.url}" style="height: 100px;" />'
        return 'Нет изображения'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Настройка отображения ингредиентов."""

    list_display = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)
    search_fields = ('name', 'measurement_unit')


@admin.register(Favorite, ShoppingCart)
class FavoriteShoppingCartAdmin(admin.ModelAdmin):
    """Настройки отображения избранных у пользователей и списка покупок."""

    list_display = ('user', 'recipe')
