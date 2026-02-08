from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"todos", views.TodoViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("test/", views.test_view, name="test"),
]
