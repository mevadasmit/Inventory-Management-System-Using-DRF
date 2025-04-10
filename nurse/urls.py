from django.urls import path
from nurse.views import RequestedListView, RequestDetailView, CreateRequestView, RequestActionView, ReturnableItemView, \
        ReturnInventoryView, ReturnStatusView

urlpatterns = [
        path('v1/requests/all',RequestedListView.as_view(),name='request-list'),
        path('v1/requests/<uuid:pk>',RequestDetailView.as_view(),name='request-detail'),
        path('v1/requests/action/<uuid:pk>',RequestActionView.as_view(),name='request-action'),
        path('v1/request/create',CreateRequestView.as_view(),name='request-create'),
        path('v1/request/returnable/inventory/<uuid:request_id>',ReturnableItemView.as_view(),name='request-inventory-inventory'),
        path('v1/request/return',ReturnInventoryView.as_view(),name='request-return'),
        path('v1/request/return/status/<uuid:request_id>',ReturnStatusView.as_view(),name='request-return-status'),
]