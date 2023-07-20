from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("<int:id>", views.index, name="get id"),
    path("create/", views.create, name="create"),
]
