from django.contrib.auth.models import User
from rest_framework import serializers
from .models import MenuItem, Category, Cart, Order


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'slug', 'title']


class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category', 'category_id']


class MenuItemForCart(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price']


class CartSerializer(serializers.ModelSerializer):
    menuitem = MenuItemForCart()

    class Meta:
        model = Cart
        fields = ['menuitem', 'quantity', 'price']


class AddItemToCartSerializer(serializers.Serializer):
    class Meta:
        model = Cart
        fields = ['menuitem', 'quantity']
        extra_kwargs = {
            'menuitem': {'required': True},
            'quantity': {'required': True, 'min_value': 1},
        }


class RemoveItemFromCartSerializer(serializers.Serializer):
    class Meta:
        model = Cart
        fields = ['menuitem']
        extra_kwargs = {
            'menuitem': {'required': True},
        }


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'date']


class AdmitOrderSerializer(serializers.Serializer):
    class Meta:
        model = Order
        fields = ['id', 'delivery_crew', 'status']
        extra_kwargs = {
            'delivery_crew': {'required': True},
            'status': {'required': True},
        }


class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
