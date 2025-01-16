import base64

from rest_framework import serializers
from django.contrib.auth import get_user_model
from api.models import Recipe
from djoser.serializers import UserSerializer, UserCreateSerializer
from django.core.files.base import ContentFile
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    '''Кастомное поле для обработки изображений в формате base64.'''

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('id', 'email', 'username',
                  'first_name', 'last_name', 'password')

    def validate(self, attrs):
        user = User(**attrs)
        password = attrs.get("password")
        validate_password(password, user)
        return attrs


class UserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'avatar'
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return user.follower.filter(following=obj).exists()
        return False


class SubscriptionRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source='recipes.count', read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count', 'avatar'
        )

    def get_recipes(self, obj):
        recipes_limit = self.context.get('recipes_limit')
        if recipes_limit:
            try:
                recipes_limit = int(recipes_limit)
            except ValueError:
                raise serializers.ValidationError(
                    'recipes_limit должен быть числом.'
                )
        recipes = obj.recipes.all()[
            :recipes_limit] if recipes_limit else obj.recipes.all()
        return SubscriptionRecipeSerializer(recipes, many=True,
                                            context=self.context).data

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return user.follower.filter(following=obj).exists()
        return False
