from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError


def custom_username_validator(value):
    """Кастомная валидация имени пользователя."""
    allowed_characters = r'^[\w.@+-]+$'
    regex_validator = RegexValidator(
        regex=allowed_characters,
        message=('Имя пользователя может содержать только '
                 'буквы, цифры и символы: . @ + - _')
    )
    try:
        regex_validator(value)
    except ValidationError:
        invalid_chars = ''.join(
            set(char for char in value
                if not char.isalnum() and char not in '._-'))
        raise ValidationError(
            f'Имя пользователя содержит недопустимые символы: {invalid_chars}')


class User(AbstractUser):

    username = models.CharField(
        'Имя пользователя',
        max_length=150,
        unique=True,
        validators=[custom_username_validator],
    )
    email = models.EmailField(
        'email',
        max_length=254,
        blank=False,
        unique=True,
    )
    first_name = models.CharField(
        'Имя',
        max_length=150,
        blank=False,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
        blank=False,
    )
    avatar = models.ImageField('Аватар', upload_to='users/images/',
                               null=True, blank=True)

    USERNAME_FIELD = 'email'
    USER_ID_FIELD = 'username'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        related_name='followers',
        on_delete=models.CASCADE,
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        related_name='authors',
        on_delete=models.CASCADE,
        verbose_name='Подписка'
    )

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('-user',)
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_follows',
            ),
        )

    def __str__(self):
        return f'{self.user.username} подписан на {self.author.username}'


class Ingredient(models.Model):
    name = models.CharField(max_length=128, verbose_name='Название',
                            help_text='Введите название ингредиента')
    measurement_unit = models.CharField(
        max_length=64,
        verbose_name='Единица измерения',
        help_text='Введите единицу измерения ингредиента'
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=256, verbose_name='Название',
                            help_text='Введите название рецепта')
    text = models.TextField('Рецепт', help_text='Введите описание рецепта')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes',
        verbose_name='Автор', help_text='Выберите автора рецепта'
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Фото', help_text='Добавьте изображение рецепта'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        help_text='Введите время приготовления в минутах',
        validators=[
            MinValueValidator(1)
        ]
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['name']

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='recipe_ingredients',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE,
        related_name='recipe_ingredients', verbose_name='Ингредиент'
    )
    amount = models.PositiveIntegerField(
        'Количество',
        help_text='Введите количество ингредиента',
        validators=[
            MinValueValidator(1)
        ]
    )

    class Meta:
        verbose_name = 'ингредиенты в рецепт'
        verbose_name_plural = 'Ингредиенты в рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]

    def __str__(self):
        return (
            f'{self.ingredient.name} - {self.amount} '
            f'{self.ingredient.measurement_unit}'
        )


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        related_name='favorites',
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='favorites',
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'избранное'
        verbose_name_plural = 'Избранное'
        ordering = ('-user',)
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite_recipes',
            ),
        )

    def __str__(self) -> str:
        return f'{self.user.username} добавил в избранное {self.recipe.name}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        related_name='shopping_carts',
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='shopping_carts',
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'корзина'
        verbose_name_plural = 'Корзина'
        ordering = ('-user',)
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_shoppingcart_recipes',
            ),
        )

    def __str__(self) -> str:
        return f'{self.user.username} добавил в корзину {self.recipe.name}'
