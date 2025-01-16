import base64

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated, AllowAny,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotAuthenticated
from djoser.serializers import SetPasswordSerializer
from django.core.files.base import ContentFile


from .serializers import (UserSerializer, SubscriptionSerializer,
                          CustomUserCreateSerializer)
from django.contrib.auth import get_user_model, update_session_auth_hash

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomUserCreateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticatedOrReadOnly()]

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def me(self, request):
        if not request.user.is_authenticated:
            raise NotAuthenticated('Пользователь не аутентифицирован')
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['post'],
            permission_classes=[IsAuthenticated])
    def set_password(self, request, *args, **kwargs):
        serializer = SetPasswordSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        self.request.user.set_password(serializer.data['new_password'])
        self.request.user.save()

        update_session_auth_hash(self.request, self.request.user)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, pk=None):
        user = request.user
        target_user = self.get_object()

        if request.method == 'POST':
            if user == target_user:
                return Response(
                    {'error': 'Нельзя подписаться на самого себя.'},
                    status=status.HTTP_400_BAD_REQUEST)
            if user.follower.filter(following=target_user).exists():
                return Response(
                    {'error': 'Вы уже подписаны на этого пользователя.'},
                    status=status.HTTP_400_BAD_REQUEST)

            user.follower.get_or_create(following=target_user)
            recipes_limit = request.query_params.get('recipes_limit')
            serializer = SubscriptionSerializer(
                target_user, context={'request': request,
                                      'recipes_limit': recipes_limit})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if not user.follower.filter(following=target_user).exists():
            return Response(
                {'error': 'Вы не подписаны на этого пользователя.'},
                status=status.HTTP_400_BAD_REQUEST)
        user.follower.filter(following=target_user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        queryset = User.objects.filter(following__user=request.user)
        recipes_limit = request.query_params.get('recipes_limit')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SubscriptionSerializer(
                page, many=True, context={'request': request,
                                          'recipes_limit': recipes_limit}
            )
            return self.get_paginated_response(serializer.data)
        serializer = SubscriptionSerializer(
            queryset, many=True, context={'request': request,
                                          'recipes_limit': recipes_limit})
        return Response(serializer.data)

    @action(detail=False, methods=['put', 'delete'], url_path='me/avatar',
            permission_classes=[IsAuthenticated])
    def avatar(self, request):
        user = request.user
        if request.method == 'PUT':
            avatar_data = request.data.get('avatar')
            if not avatar_data:
                raise ValidationError('Требуются данные для аватара.')
            try:
                format, imgstr = avatar_data.split(';base64,')
            except ValueError:
                raise ValidationError(
                    'Недопустимый формат аватара. Ожидаемое - base64.')

            format, imgstr = avatar_data.split(';base64,')
            ext = format.split('/')[-1]
            avatar_file = ContentFile(base64.b64decode(imgstr),
                                      name=f'avatar.{ext}')
            user.avatar = avatar_file
            user.save()
            return Response({'avatar': user.avatar.url})
        user.avatar = None
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
