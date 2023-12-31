from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, include

from .views import (
    ProjectsListView,
    ProjectsDetailsView,
    CustomLoginView,
    EquipmentDetailsView,
    CreatePositionView,
    DestroyPositionView,
    CreateLocationView,
    CreateNodeView,
    CreateEquipmentView,
    RemoveEquipmentView,
    ManufacturesListView,
    ManufactureDetailsView,
    ManufactureCreateView,
    DestroyProjectView,
    DestroyManufactureView,
    UpdateLocationView,
    EquipmentList,
    EquipmentUpdateView,
    RawSqlView,
    RawSqlQuery,

)

urlpatterns = [
    path('raw-sql/', RawSqlView.as_view(), name='raw_sql'),
    path('raw-sql-query/', RawSqlQuery.as_view(), name='raw_sql-query'),
    path('create-position/', CreatePositionView.as_view(), name='create_position'),
    path('equipment/', EquipmentList.as_view(), name='equipment_list'),
    path('destroy-project/<int:pk>/', DestroyProjectView.as_view(), name='destroy_project'),
    path('destroy-manufacture/<int:pk>/', DestroyManufactureView.as_view(), name='destroy_manufacture'),
    path('manufacture-create/', ManufactureCreateView.as_view(), name='manufacture_create'),
    path('manufacture/', ManufacturesListView.as_view(), name='manufactures'),
    path('manufacture/<int:pk>/', ManufactureDetailsView.as_view(), name='manufacture_details'),
    path('remove-position/<int:pk>/', DestroyPositionView.as_view(), name='destroy_position'),
    path('remove-equipment/<int:pk>/', RemoveEquipmentView.as_view(), name='remove_equipment'),
    path('create-location/', CreateLocationView.as_view(), name='create_location'),
    path('update-location/<int:pk>/', UpdateLocationView.as_view(), name='update_location'),
    path('create-node/', CreateNodeView.as_view(), name='create_node'),
    path('create-equipment/<int:pk>/', CreateEquipmentView.as_view(), name='create_equipment'),
    path('', ProjectsListView.as_view(), name='projects_list'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('<str:slug>/', ProjectsDetailsView.as_view(), name='project_details'),
    path('position/<str:slug>/', EquipmentDetailsView.as_view(), name='equipment_details'),
    path('position-update/<str:slug>/', EquipmentUpdateView.as_view(), name='equipment_update'),


]
