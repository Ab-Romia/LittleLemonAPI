from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from .views import *

urlpatterns = [
    path('menu-items/', MenuItemView.as_view(), name='menu_items'),
    path('menu-items/<int:pk>/', MenuItemDetailView.as_view(), name='single_item'),
    path('category-items/', CategoryView.as_view(), name='category_items'),
    path('category-items/<int:pk>/', CategoryItemView.as_view(), name='single_category'),
    path('cart/menu-items/', CartItemsView.as_view(), name='cart_items'),
    path('cart/menu-items/<int:pk>/', CartItemDetailView.as_view(), name='single_cart_item'),
    path('groups/managers/users/', ManagerUsersView.as_view(), name='manager_users'),
    path('groups/managers/users/<int:pk>/', ManagerUserDetailView.as_view(), name='single_manager_user'),
    path('groups/delivery-crew/users/', DeliveryCrewUsersView.as_view(), name='delivery_crew_users'),
    path('groups/delivery-crew/users/<int:pk>/', DeliveryCrewUserDetailView.as_view(),
         name='single_delivery_crew_user'),
    path('order/',OrderView.as_view(), name='order'),
    path('order/<int:pk>/', OrderItemDetailView.as_view(), name='single_order'),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('users/', include('djoser.urls')),

]
