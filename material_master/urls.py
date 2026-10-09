from django.urls import path
from . import views
app_name = "material_master"

urlpatterns = [
    path("", views.material_master_view, name="view"),
    path("add/", views.material_master_add_view, name="add"),
    path("edit", views.material_master_edit_view, name="edit"),
    path("delete", views.material_master_delete_view, name="delete"),
]