from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BoardViewSet, PostViewSet, delete_comment, admin_create_news

router = DefaultRouter()
router.register('boards', BoardViewSet, basename='board')
router.register('posts', PostViewSet, basename='post')

urlpatterns = [
    path('', include(router.urls)),
    path('comments/<int:pk>/', delete_comment, name='delete-comment'),
    path('admin/news/', admin_create_news, name='admin-news'),
]
