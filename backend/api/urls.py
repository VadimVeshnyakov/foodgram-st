from rest_framework import routers

from django.urls import include, path


from .views import (RecipeViewSet, IngredientViewSet,
                    RecipeRedirectView, UserViewSet)


router = routers.DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
    path('s/<str:short_id>/', RecipeRedirectView.as_view(),
         name='recipe_redirect'),
]
