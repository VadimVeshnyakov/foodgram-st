from django.utils.timezone import now


def render_shopping_cart(ingredients):
    """Рендерит текстовый отчет для списка покупок."""
    today = now().strftime("%d.%m.%Y")
    header = f'Список покупок\nДата: {today}\n'
    product_list = [(
        f'{i}. {ingredient["name"].capitalize()} — {ingredient["amount"]}'
        f'{ingredient["measurement_unit"]}')
        for i, ingredient in enumerate(ingredients, 1)
    ]
    recipe_set = {ingredient['recipe_name'] for ingredient in ingredients}

    recipe_list = ['Рецепты:'] + list(recipe_set)

    return '\n'.join([
        header,
        "Ингредиенты:",
        *product_list,
        "",
        *recipe_list
    ])
