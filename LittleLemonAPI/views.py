from django.contrib.auth.models import User
from django.shortcuts import render
from rest_framework import generics
from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView, ListCreateAPIView, get_object_or_404
from django.http import JsonResponse
from rest_framework.status import HTTP_200_OK

from .models import MenuItem, Category, Cart, OrderItem, Order
from .serializers import MenuItemSerializer, CategorySerializer, CartSerializer, AddItemToCartSerializer, \
    UserSerializer, ManagerSerializer, RemoveItemFromCartSerializer, OrderSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import permission_classes, api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from .permissions import ManagerPermission, DeliveryCrewPermission


class MenuItemView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    ordering_fields = ['category', 'price']
    search_fields = ['title', 'category__title']

    def get_permissions(self):
        permission_classes = []
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]


class MenuItemDetailView(generics.RetrieveUpdateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permission(self):
        permission_classes = [IsAuthenticated]
        if self.request.method in ['PATCH', 'DELETE']:
            permission_classes = [IsAuthenticated, IsAdminUser | ManagerPermission]

        return [permission() for permission in permission_classes]


class CategoryView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        permission_classes = []
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]


class CategoryItemView(generics.RetrieveUpdateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permission(self):
        permission_classes = [IsAuthenticated]
        if self.request.method in ['PATCH', 'DELETE']:
            permission_classes = [IsAuthenticated, IsAdminUser | ManagerPermission]

        return [permission() for permission in permission_classes]


class CartItemsView(ListCreateAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def post(self, request, *args, **kwargs):
        serialized_item = AddItemToCartSerializer(data=request.data)
        if serialized_item.is_valid():
            menuitem = MenuItem.objects.get(pk=serialized_item.data['menuitem'])
            quantity = serialized_item.data['quantity']
            cart_item = Cart.objects.filter(user=request.user, menuitem=menuitem).first()
            if cart_item:
                cart_item.quantity += quantity
                cart_item.price = cart_item.quantity * cart_item.unit_price
                cart_item.save()
                return JsonResponse({'message': 'Item added to cart'}, status=HTTP_200_OK)
            else:
                cart_item = Cart.objects.create(user=request.user, menuitem=menuitem, quantity=quantity,
                                                unit_price=menuitem.price, price=menuitem.price * quantity)
                return JsonResponse({'message': 'Item added to cart'}, status=HTTP_200_OK)
        else:
            return JsonResponse(serialized_item.errors, status=400)

    def delete(self, request, *args, **kwargs):
        serialized_item = RemoveItemFromCartSerializer(data=request.data)
        if serialized_item.is_valid():
            menuitem = MenuItem.objects.get(pk=serialized_item.data['menuitem'])
            cart_item = Cart.objects.filter(user=request.user, menuitem=menuitem).first()
            if cart_item:
                cart_item.delete()
                return JsonResponse({'message': 'Item removed from cart'}, status=HTTP_200_OK)
            else:
                return JsonResponse({'message': 'Item not found in cart'}, status=404)
        else:
            return JsonResponse(serialized_item.errors, status=400)


class CartItemDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return get_object_or_404(Cart, user=self.request.user, pk=self.kwargs['pk'])


class ManagerUsersView(ListCreateAPIView):
    queryset = User.objects.filter(groups__name='Manager')
    serializer_class = ManagerSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        return User.objects.filter(groups__name='Manager')


class ManagerUserDetailView(RetrieveUpdateDestroyAPIView):
    queryset = User.objects.filter(groups__name='Manager')
    serializer_class = ManagerSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        return User.objects.filter(groups__name='Manager')


class DeliveryCrewUsersView(ListCreateAPIView):
    queryset = User.objects.filter(groups__name='Delivery Crew')
    serializer_class = ManagerSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        return User.objects.filter(groups__name='Delivery Crew')


class DeliveryCrewUserDetailView(RetrieveUpdateDestroyAPIView):
    queryset = User.objects.filter(groups__name='Delivery Crew')
    serializer_class = ManagerSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        return User.objects.filter(groups__name='Delivery Crew')


class OrderView(ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_permissions(self):
        permission_classes = []
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            permission_classes = [IsAuthenticated, IsAdminUser | ManagerPermission]
        return [permission() for permission in permission_classes]

    def post(self, request, *args, **kwargs):
        serialized_order = OrderSerializer(data=request.data)
        if serialized_order.is_valid():
            order = Order.objects.create(user=request.user, delivery_crew=None, status=False, total=0,
                                         date=serialized_order.data['date'])
            cart_items = Cart.objects.filter(user=request.user)
            total = 0
            for item in cart_items:
                total += item.price
                OrderItem.objects.create(order=order, menuitem=item.menuitem, quantity=item.quantity,
                                         unit_price=item.unit_price, price=item.price)
                item.delete()
            order.total = total
            order.save()
            return JsonResponse({'message': 'Order placed successfully'}, status=HTTP_200_OK)
        else:
            return JsonResponse(serialized_order.errors, status=400)


class OrderItemDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return get_object_or_404(Order, user=self.request.user, pk=self.kwargs['pk'])

    def put(self, request, *args, **kwargs):
        order = self.get_object()
        serialized_order = OrderSerializer(order, data=request.data)
        if serialized_order.is_valid():
            if order.status:
                return JsonResponse({'message': 'Order already admitted'}, status=400)
            else:
                order.delivery_crew = serialized_order.data['delivery_crew']
                order.status = serialized_order.data['status']
                order.save()
                return JsonResponse({'message': 'Order updated successfully'}, status=HTTP_200_OK)
        else:
            return JsonResponse(serialized_order.errors, status=400)

    def patch(self, request, *args, **kwargs):
        order = self.get_object()
        serialized_order = OrderSerializer(order, data=request.data, partial=True)
        if serialized_order.is_valid():
            if order.status:
                return JsonResponse({'message': 'Order already admitted'}, status=400)
            else:
                order.delivery_crew = serialized_order.data['delivery_crew']
                order.status = serialized_order.data['status']
                order.save()
                return JsonResponse({'message': 'Order updated successfully'}, status=HTTP_200_OK)
        else:
            return JsonResponse(serialized_order.errors, status=400)

    def delete(self, request, *args, **kwargs):
        order = self.get_object()
        if order.status:
            return JsonResponse({'message': 'Order already admitted'}, status=400)
        else:
            order.delete()
            return JsonResponse({'message': 'Order deleted successfully'}, status=HTTP_200_OK)
