from django.urls import path
from . import views

urlpatterns = [
    path('api/vendors/', views.vendor_list_create),
    path('api/vendors/<int:vendor_id>/', views.vendor_detail),
    path('api/purchase_orders/', views.purchase_order_list_create),
    path('api/purchase_orders/<int:po_id>/', views.purchase_order_detail),
]
