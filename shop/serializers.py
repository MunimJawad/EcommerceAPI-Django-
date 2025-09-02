from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator
from .models import Category,Product,Order,OrderItem,ShippingAddress

User=get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password=serializers.CharField(required=True,write_only=True)
    email=serializers.EmailField(required=True,
                                 validators=[UniqueValidator(queryset=User.objects.all())])
    username=serializers.CharField(required=True,
                                   validators=[UniqueValidator(queryset=User.objects.all())])
    
    class Meta:
        model=User
        fields=['id','username','email','password']

    def create(self,validated_data):
        validated_data['role']=validated_data.get('role','customer')

        user=User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data['role']
        )
        return user
 

class LoginSerializer(serializers.Serializer):
    username=serializers.CharField()
    password=serializers.CharField()

    def validate(self,data):
        from django.contrib.auth import authenticate

        user=authenticate(username=data['username'],password=data['password'])

        if user:
            refresh=RefreshToken.for_user(user)

            return {
                'refresh':str(refresh),
                'access':str(refresh.access_token),
                'username':user.username,
                'role':user.role,
            }
        raise serializers.ValidationError("Invalid email or password")

    

class UserSerializer(serializers.ModelSerializer):
    password=serializers.CharField(required=True,write_only=True)
    email=serializers.EmailField(required=True,
                                 validators=[UniqueValidator(queryset=User.objects.all())])
    username=serializers.CharField(required=True,
                                   validators=[UniqueValidator(queryset=User.objects.all())])

    

    class Meta:
        model=User
        fields=['id','username','email','password','role']

    def update(self,instance,validated_data):

        request_user = self.context['request'].user
        is_admin = request_user.role == 'admin'
        
        new_role=validated_data.get('role',instance.role)

        if is_admin: 
            instance.role=new_role
            if new_role == 'admin':
               instance.is_staff=True
               instance.is_superuser=True
            else:
              instance.is_staff=False
              instance.is_superuser=False

        instance.username=validated_data.get('username',instance.username)
        instance.email=validated_data.get('email',instance.email)
        instance.password=validated_data.get('password',instance.password)
        

        return instance


#Category Serializer

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model=Category
        fields=['id','name','slug']

#Product Serializer
class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        write_only=True,
        source='category'
    )

    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'price', 'stock', 'image', 'slug', 'category', 'category_id']


# Order Item Serializer
class OrderItemSerializer(serializers.ModelSerializer):
    product_title = serializers.ReadOnlyField(source='product.title')
    product_price = serializers.ReadOnlyField(source='product.price')

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_title', 'product_price', 'quantity']


class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
       model=ShippingAddress
       fields=['id','address','city','zip_code','date_added']


class OrderSerializer(serializers.ModelSerializer):
    items=OrderItemSerializer(many=True,read_only=True)
    customer_name=serializers.ReadOnlyField(source='customer.username')
    total_price=serializers.ReadOnlyField(source='get_cart_total')
    total_items=serializers.ReadOnlyField(source='get_total_item')     
    shipping_address=serializers.SerializerMethodField()

    def get_shipping_address(self, obj):
         shipping = ShippingAddress.objects.filter(order=obj).last()  # or `.first()` based on your logic
         if shipping:
             return {
                 "address": shipping.address,
                 "city": shipping.city,
                 "zip_code": shipping.zip_code,
             }
         return None

    class Meta:
        model=Order
        fields=['id','customer','customer_name','created_at','status','payment_method','payment_status','is_checked_out','completed','items','shipping_address','total_price','total_items']
        read_only_fields=['customer','created_at','items']



#Admin Functionality
class AdminOrderSerializer(serializers.ModelSerializer):
    items=OrderItemSerializer(many=True,read_only=True)
    customer_name=serializers.ReadOnlyField(source='customer.username')
    shipping_address=serializers.SerializerMethodField()
    total_price=serializers.ReadOnlyField(source='get_cart_total')
    total_items=serializers.ReadOnlyField(source="get_total_item")

    def get_shipping_address(self, obj):
         shipping = ShippingAddress.objects.filter(order=obj).last()  # or `.first()` based on your logic
         if shipping:
             return {
                 "address": shipping.address,
                 "city": shipping.city,
                 "zip_code": shipping.zip_code,
             }
         return None
        
    class Meta:
        model=Order
        fields=['id','customer','customer_name','created_at','status','is_checked_out','payment_method','payment_status','completed','items','shipping_address','total_price','total_items']
        read_only_fields=['customer','created_at']

        

