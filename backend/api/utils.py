from django.utils.timezone import now


def render_shopping_cart(ingredients):
    """Рендерит текстовый отчет для списка покупок."""
    today = now().strftime("%d.%m.%Y")
    header = f'Список покупок\nДата: {today}\n'
    product_list = ['Ингредиенты:\n']
    recipe_set = set()

    for i, ingredient in enumerate(ingredients, 1):
        name = ingredient['name'].capitalize()
        amount = ingredient['amount']
        unit = ingredient['measurement_unit']
        recipe_name = ingredient['recipe_name']
        product_list.append(f'{i}. {name} — {amount} {unit}')
        recipe_set.add(recipe_name)

    recipe_list = ['Рецепты:', *sorted(recipe_set)]

    return '\n'.join([
        header,
        *product_list,
        "",
        *recipe_list
    ])
