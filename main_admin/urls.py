from django.urls import path
from main_admin.views import UserListViewAPI, UserDetailViewAPI, InventoryView, InventoryDetailView, OrganizationView, \
    OrganizationDetailView

urlpatterns = [
    path('v1/admin/user/list',UserListViewAPI.as_view(),name='user-list'),
    path('v1/admin/user/detail/<uuid:pk>',UserDetailViewAPI.as_view(),name='user-list'),
    path('v1/admin/category',InventoryView.as_view(),name='inventory-list'),
    path('v1/admin/inventory/detail/<uuid:pk>',InventoryDetailView.as_view(),name='inventory-detail'),
    path('v1/admin/organization',OrganizationView.as_view(),name='organization-list'),
    path('v1/admin/organization/<uuid:pk>',OrganizationDetailView.as_view(),name='organization-detail'),
]