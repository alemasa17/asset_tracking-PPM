from django.urls import path

from . import views

urlpatterns = [
    path("beni/", views.asset_list, name="asset_list"),
    path("beni/nuovo/", views.asset_create, name="asset_create"),
    path("beni/<int:pk>/", views.asset_detail, name="asset_detail"),
    path("beni/<int:pk>/modifica/", views.asset_update, name="asset_update"),
    path("beni/<int:pk>/dismetti/", views.asset_retire, name="asset_retire"),
    path("beni/<int:pk>/prendi/", views.asset_checkout, name="asset_checkout"),
    path("beni/<int:pk>/restituisci/", views.asset_return, name="asset_return"),
    path("beni/<int:pk>/sposta/", views.asset_move, name="asset_move"),
]