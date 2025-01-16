from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinValueValidator

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(max_length=256, verbose_name='Название',
                            help_text='Введите название ингредиента')
    measurement_unit = models.CharField(
        max_length=256, verbose_name='Единица измерения',
        help_text='Введите единицу измерения ингредиента'
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'

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
            MinValueValidator(
                1, 'Время приготовление должно быть не менее минуты'
            )
        ]
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'

    def get_short_link(self, request):
        short_id = format(self.id, 'x')
        host = request.get_host()
        return f'{host}/s/{short_id}'

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
            MinValueValidator(
                1, 'Колличество ингредиента в рецептне не должно быть менее 1.'
            )
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
        related_name='favorited_by',
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
        related_name='shopping_cart',
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='in_shopping_carts',
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
