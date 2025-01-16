from rest_framework import serializers
from collections import Counter
from users.serializers import UserSerializer, Base64ImageField

from .models import (Ingredient, Recipe, RecipeIngredient,
                     Favorite, ShoppingCart)


class IngredientSerializer(serializers.ModelSerializer):
    '''Сериализатор для модели ингредиентов.'''

    class Meta:
        fields = '__all__'
        model = Ingredient


class RecipeIngredientSerializer(serializers.ModelSerializer):
    '''Сериализатор для отображения ингредиентов рецепта.'''

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
    )
    name = serializers.CharField(
        source='ingredient.name',
        read_only=True
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    '''Сериализатор для рецептов.'''

    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(source='recipe_ingredients',
                                             many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(allow_null=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def validate_ingredients(self, ingredients):
        '''Проверка ингредиентов на дубликаты.'''
        if not ingredients:
            raise serializers.ValidationError(
                'Необходимо добавить хотя бы один ингредиент.')
        ingredient_ids = [ingredient['id'] for ingredient in ingredients]
        ingredient_counts = Counter(ingredient_ids)
        duplicate_ingredients = [
            ingredient_id for ingredient_id,
            count in ingredient_counts.items() if count > 1
        ]

        if duplicate_ingredients:
            raise serializers.ValidationError(
                'Ингредиенты с id ',
                f'{", ".join(map(str, duplicate_ingredients))} повторяются.')

        return ingredients

    def validate_image(self, image):
        '''Проверка картинки.'''
        if not image:
            raise serializers.ValidationError(
                'Необходимо добавить фото.')
        return image

    @staticmethod
    def save_ingredients(recipe, ingredients_data):
        '''Создание связей ингредиентов с рецептом.'''
        ingredients_list = []
        for ingredient in ingredients_data:
            current_ingredient = ingredient['id']
            current_amount = ingredient.get('amount')
            ingredients_list.append(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=current_ingredient,
                    amount=current_amount
                )
            )
        RecipeIngredient.objects.bulk_create(ingredients_list)

    def create(self, validated_data):
        '''Создание рецепта.'''
        user = self.context['request'].user
        ingredients_data = validated_data.pop('recipe_ingredients')
        recipe = Recipe.objects.create(author=user, **validated_data)
        self.save_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        '''Обновление рецепта.'''
        ingredients_data = validated_data.pop('recipe_ingredients', None)
        if ingredients_data is None or not ingredients_data:
            raise serializers.ValidationError(
                'Ингредиенты обязательны при обновлении рецепта.'
            )
        instance.ingredients.clear()
        self.save_ingredients(instance, ingredients_data)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return Favorite.objects.filter(user=user, recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return ShoppingCart.objects.filter(user=user, recipe=obj).exists()
        return False


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
