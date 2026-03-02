# Верстальщик
from backend.models import User, Category, Shop, ProductInfo, Product, ProductParameter, OrderItem, Order, Contact, ProductImage
from rest_framework import serializers
from easy_thumbnails.files import get_thumbnailer

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ('id', 'city', 'street', 'house', 'structure', 'building', 'apartment', 'user', 'phone')
        read_only_fields = ('id',)
        extra_kwargs = {
            'user': {'write_only': True}
        }

# создаем класс для регистрации нового пользователя
class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password', 'company', 'position')

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(
            username=validated_data['email'],
            **validated_data,
        )
        user.set_password(password)
        user.save()
        return user



class UserSerializer(serializers.ModelSerializer):
    contacts = ContactSerializer(read_only=True, many=True)

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'company', 'position', 'contacts')
        read_only_fields = ('id',)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name',)
        read_only_fields = ('id',)


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ('id', 'name', 'state',)
        read_only_fields = ('id',)

class ProductImageSerializer(serializers.ModelSerializer):
    image_small = serializers.SerializerMethodField()
    image_medium = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'image_small', 'image_medium', 'is_main', 'order']

    def get_image_small(self, obj):
        if obj.image:
            thumbnailer = get_thumbnailer(obj.image)
            return thumbnailer['product_small'].url
        return None

    def get_image_medium(self, obj):
        if obj.image:
            thumbnailer = get_thumbnailer(obj.image)
            return thumbnailer['product_medium'].url
        return None

class ProductSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()
    image_small = serializers.SerializerMethodField()
    image_medium = serializers.SerializerMethodField()
    image_large = serializers.SerializerMethodField()
    additional_images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ('name', 'category', 'image', 'image_small',
                 'image_medium', 'image_large', 'additional_images')

        def get_image_small(self, obj):
            if obj.image:
                thumbnailer = get_thumbnailer(obj.image)
                return thumbnailer['product_small'].url
            return None

        def get_image_medium(self, obj):
            if obj.image:
                thumbnailer = get_thumbnailer(obj.image)
                return thumbnailer['product_medium'].url
            return None

        def get_image_large(self, obj):
            if obj.image:
                thumbnailer = get_thumbnailer(obj.image)
                return thumbnailer['product_large'].url
            return None


class ProductParameterSerializer(serializers.ModelSerializer):
    parameter = serializers.StringRelatedField()

    class Meta:
        model = ProductParameter
        fields = ('parameter', 'value',)


class ProductInfoSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_parameters = ProductParameterSerializer(read_only=True, many=True)

    class Meta:
        model = ProductInfo
        fields = ('id', 'model', 'product', 'shop', 'quantity', 'price', 'price_rrc', 'product_parameters',)
        read_only_fields = ('id',)


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('id', 'product_info', 'quantity', 'order',)
        read_only_fields = ('id',)
        extra_kwargs = {
            'order': {'write_only': True}
        }


class OrderItemCreateSerializer(OrderItemSerializer):
    product_info = ProductInfoSerializer(read_only=True)


class OrderSerializer(serializers.ModelSerializer):
    ordered_items = OrderItemCreateSerializer(read_only=True, many=True)

    total_sum = serializers.IntegerField()
    contact = ContactSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'ordered_items', 'state', 'dt', 'total_sum', 'contact')
        read_only_fields = ('id',)


class UserAvatarSerializer(serializers.ModelSerializer):
    avatar_small = serializers.SerializerMethodField()
    avatar_medium = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'avatar',
                  'avatar_small', 'avatar_medium', 'company', 'position']

    def get_avatar_small(self, obj):
        if obj.avatar:
            thumbnailer = get_thumbnailer(obj.avatar)
            return thumbnailer['avatar_small'].url
        return None

    def get_avatar_medium(self, obj):
        if obj.avatar:
            thumbnailer = get_thumbnailer(obj.avatar)
            return thumbnailer['avatar_medium'].url
        return None


