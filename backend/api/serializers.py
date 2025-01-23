from rest_framework import serializers
from collections import Counter
from recipe.models import (Ingredient, Recipe, RecipeIngredient,
                           Favorite, ShoppingCart)
from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer, UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class UsersSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'avatar'
        )

    def get_is_subscribed(self, author):
        user = self.context['request'].user
        if user.is_authenticated:
            return user.followers.filter(following=author).exists()
        return False


class UsersCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('id', 'email', 'username',
                  'first_name', 'last_name', 'password')

    def validate(self, attrs):
        user = User(**attrs)
        password = attrs.get("password")
        validate_password(password, user)
        return attrs


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ингредиентов."""

    class Meta:
        fields = '__all__'
        model = Ingredient


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения ингредиентов рецепта."""

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

    def validate_amount(self, value):
        """Валидация поля amount."""
        if value < 1:
            raise serializers.ValidationError(
                'Колличество ингредиента в рецептне не должно быть менее 1.'
            )
        return value


class SubscriptionRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов."""

    author = UsersSerializer(read_only=True)
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

    def validate_cooking_time(self, value):
        """Валидация поля cooking_time."""
        if value < 1:
            raise serializers.ValidationError(
                'Время приготовление должно быть не менее минуты'
            )
        return value

    def validate_ingredients(self, ingredients):
        """Проверка ингредиентов на дубликаты."""
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
                f'Ингредиенты с id {duplicate_ingredients} повторяются.')

        return ingredients

    def validate_image(self, image):
        """Проверка картинки."""
        if not image:
            raise serializers.ValidationError(
                'Необходимо добавить фото.')
        return image

    @ staticmethod
    def save_ingredients(recipe, ingredients_data):
        """Создание связей ингредиентов с рецептом."""
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient.get('amount')
            )
            for ingredient in ingredients_data
        ])

    def create(self, validated_data):
        """Создание рецепта."""
        ingredients_data = validated_data.pop('recipe_ingredients')
        recipe = super().create(validated_data)
        self.save_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        """Обновление рецепта."""
        ingredients_data = validated_data.pop('recipe_ingredients', None)
        validated_ingredients = self.validate_ingredients(ingredients_data)
        instance.recipe_ingredients.all().delete()
        self.save_ingredients(instance, validated_ingredients)
        return super().update(instance, validated_data)

    def get_is_favorited(self, recipe):
        user = self.context['request'].user
        return user.is_authenticated and Favorite.objects.filter(
            user=user, recipe=recipe).exists()

    def get_is_in_shopping_cart(self, recipe):
        user = self.context['request'].user
        return user.is_authenticated and ShoppingCart.objects.filter(
            user=user, recipe=recipe).exists()


class SubscriptionSerializer(UsersSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source='recipes.count', read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count', 'avatar'
        )

    def get_recipes(self, obj):
        recipes_limit = self.context.get('recipes_limit', None)
        if recipes_limit is None:
            recipes_limit = 10**10
        try:
            recipes_limit = int(recipes_limit)
        except ValueError:
            raise serializers.ValidationError(
                'recipes_limit должен быть числом.'
            )
        recipes = obj.recipes.all()[:recipes_limit]
        return SubscriptionRecipeSerializer(recipes, many=True,
                                            context=self.context).data
