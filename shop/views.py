from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status,permissions
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from .permissions import IsAdmin,IsCustomer,IsStaff,IsAdminOrSelf,IsAdminOrReadOnly
from .serializers import RegisterSerializer,LoginSerializer,UserSerializer,CategorySerializer,ProductSerializer,OrderItemSerializer,OrderSerializer,ShippingAddressSerializer,AdminOrderSerializer
from .models import CustomUser,Category,Product,Order,OrderItem,ShippingAddress
from django.shortcuts import get_object_or_404


class RegisterView(APIView):
    def post(self,request):
        serializer=RegisterSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
    
class UserListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):  
        if request.user.role !="admin":
            return Response({"error":"You have no permission to view this page"})
        users = CustomUser.objects.all()
        total_users = users.count()
        serializer = UserSerializer(users, many=True)
        return Response({
            'users': serializer.data,
            'total_users': total_users
        })

class UserDetailUpdateDeleteView(APIView):
    permission_classes=[IsAdminOrSelf]

    def get(self,request,pk):
        user=get_object_or_404(CustomUser,pk=pk)
        self.check_object_permissions(request, user)
        return Response(UserSerializer(user).data)
    
    def put(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        self.check_object_permissions(request, user)
        if request.user != user and request.user.role != 'admin':
            return Response({"error": "Permission denied"}, status=403)
        serializer = UserSerializer(user, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
    def delete(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        self.check_object_permissions(request, user)
        if request.user.role != 'admin':
            return Response({"error": "Only admins can delete users"}, status=403)
        user.delete()
        return Response({"message":"Successfully deleted {user.username}"},status=204)


#Categroy Crud

class CategoryCreateOrListView(APIView):
    permission_classes=[IsAdminOrReadOnly]

    def get(self, request):
      categories = Category.objects.all()
      total = categories.count()
      serializer = CategorySerializer(categories, many=True)
      return Response({
          "message": "Here is the List of Categories",
          'categories': serializer.data,
          'total': total            
      })
    

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryUpdateOrDeleteView(APIView):
    permission_classes=[IsAdminOrReadOnly]
    def get_object(self, pk):
        category = get_object_or_404(Category, pk=pk)
        # Check object-level permissions
        self.check_object_permissions(self.request, category)
        return category

    def get(self, request, pk):
        category = self.get_object(pk)
        serializer = CategorySerializer(category)
        return Response(serializer.data)
    
    def delete(self, request, pk):
        category = self.get_object(pk)
        if category:
             category.delete()
             return Response(
                 {"message": f"Category {category.name} deleted successfully"},
                 status=status.HTTP_204_NO_CONTENT
             )
        return Response({'error':"You do not have permission to perform this operation"},status=status.HTTP_403_FORBIDDEN)

#Product Crud

class ProductListCreateAPIView(APIView):
   
    country="Bangladesh"
    def get(self,request):
        products=Product.objects.all()
        if products:
           serializer=ProductSerializer(products,many=True)
           return Response({
               "message":f"Total {products.count()} products availbale now:",
               "product_list":serializer.data
           },status=status.HTTP_200_OK)
        else:
            return Response({"message":"There is no prodcts please Add some"})
        
    def post(self, request):
      if request.user.role=='admin':
          serializer = ProductSerializer(data=request.data)
          if serializer.is_valid():
              serializer.save()
              return Response({
                  "message": "New Product added",
                  "data": serializer.data
              }, status=status.HTTP_201_CREATED)
          return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ProductDetailOrDeleteView(APIView):
    def get_object(self, pk):
        return get_object_or_404(Product, pk=pk)

    def get(self, request, pk):
        product = self.get_object(pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data)
    
    def put(self,request,pk):
        product=self.get_object(pk)
        serializer=ProductSerializer(product,data=request.data,partial=True,context={'request': request})
        
        if request.user.role=="admin":
           if serializer.is_valid():
               serializer.save()
               return Response({
                   'product':serializer.data,
                   'message':"Product Updated Successfully"
                   })
        return Response({
            'error':"You have no access to edit product"
        },status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request,pk):
        product=self.get_object(pk)

        if request.user.role=="admin":
            product.delete()
            return Response({
                'message':'Product Deleted Successfully'
            },status=status.HTTP_204_NO_CONTENT)
        return Response({
            'error':'You have no access to delete the product'
        },status=status.HTTP_403_FORBIDDEN)
    

    
#Cart APIView

class CartAPI(APIView):

    permission_classes=[IsAuthenticated]

    def get_cart(self,user):
        cart,created=Order.objects.get_or_create(customer=user,is_checked_out=False)
        return cart
    
    def get(self,request):
        cart=self.get_cart(request.user)
        serializer=OrderSerializer(cart)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    def post(self,request):
        """Add product to cart"""

        product_id=request.data.get("product_id")
        quantity=request.data.get("quantity",1)

        if not product_id:
            return Response({"error": "Product ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            product=Product.objects.get(id=product_id)
        
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        
        cart=self.get_cart(request.user)

        item,created=OrderItem.objects.get_or_create(order=cart,product=product)

        if not created:
            item.quantity+=int(quantity)
        else:
            item.quantity=quantity
        item.save()

        serializer=OrderSerializer(cart)

        return Response(serializer.data,status=status.HTTP_201_CREATED)
    
    def put(self,request):
        """Update quantity of a product in cart"""

        item_id=request.data.get("item_id")
        quantity=request.data.get("quantity")

        if not item_id or quantity is None:
            return Response({'error':'ID and Quantity Required'},status=status.HTTP_400_BAD_REQUEST)
        
        try:
            item=OrderItem.objects.get(id=item_id,order__customer=request.user,order__is_checked_out=False)
        
        except Product.DoesNotExist:
            return Response({'error':'Product not found in cart'},status=status.HTTP_400_BAD_REQUEST)
        
        item.quantity=int(quantity)
        item.save()

        cart=self.get_cart(request.user)
        serializer=OrderSerializer(cart)
        return Response(serializer.data,status=status.HTTP_200_OK)


    
    def delete(self,request):
        """Remove Product from cart"""

        item_id=request.data.get("item_id")

        if not item_id:
            return Response({'error':'Item ID is required'},status=status.HTTP_400_BAD_REQUEST)
        try:
          item=OrderItem.objects.get(id=item_id,order__customer=request.user,order__is_checked_out=False)
          item.delete()
        except OrderItem.DoesNotExist:
            return Response({'error':'Order Item Does not Found '},status=status.HTTP_400_BAD_REQUEST)
        
        cart=self.get_cart(request.user)
        serializer=OrderSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)
        



class CheckoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Get the active order for this user
            order = Order.objects.get(customer=request.user, is_checked_out=False)
        except Order.DoesNotExist:
            return Response({'error': 'Order Does not Exist'}, status=status.HTTP_400_BAD_REQUEST)
        
        
        payment_method=request.data.get('payment_method')
        
        serializer = ShippingAddressSerializer(data=request.data)

        if serializer.is_valid():
            # Save shipping address and link it with user + order
            shipping = serializer.save(user=request.user, order=order)

         
            order.is_checked_out = True
            order.payment_method=payment_method
            if order.payment_method=='COD':
              order.payment_status=True
            order.save()

            return Response({
                "message": "Checkout successfully",
                "order_id": order.id,
                "order_username": request.user.username,
                "total_price": order.get_cart_total,
                'payment_method':order.payment_method,
                'payment_status':order.payment_status,
                "shipping_address": ShippingAddressSerializer(shipping).data

            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

#Payment API

class PaymentOrderAPI(APIView):
    permission_classes=[IsAuthenticated]

    def post(self,request,pk):
        try:
            order=Order.objects.get(id=pk,is_checked_out=True)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if order.payment_status:
            order.status="delivered"
            order.completed=True      

        order.save()

        return Response({
            "message": f" Order Delivered and Completed successfully",
            "order_id": order.id,
            "total_price": order.get_cart_total,
            "completed": order.completed
        }, status=status.HTTP_200_OK)




#User
class OrderListAPIView(APIView):
    permission_classes=[IsAuthenticated]

    def get(self,request):
        orders=Order.objects.filter(customer=request.user,is_checked_out=True).order_by('-created_at')
        serializer=OrderSerializer(orders,many=True)
        return Response(serializer.data)
    

class OrderDetailUpdateDeleteView(APIView):
    permission_classes=[IsAuthenticated]

    def get_order(self, pk):
        # Ensure that the order is retrieved using the pk
        return get_object_or_404(Order, pk=pk)

    def get(self, request, pk):
        order = self.get_order(pk)
        serializer = OrderSerializer(order)  # Make sure to pass the context as well
        return Response(serializer.data)
    
   


#Payment Integration


#Admin Functionality

class AdminOrderListAPIView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        orders=Order.objects.all().order_by('-created_at')
        #orders = Order.objects.filter(is_checked_out=True ).order_by('-created_at')
        serializer = AdminOrderSerializer(orders, many=True)
        return Response(serializer.data)
    
    
    

class AdminOrderUpdateView(APIView):
    permission_classes=[IsAdmin]

    def patch(self,request,pk):
        try:
          order=Order.objects.get(is_checked_out=True,pk=pk)
        except Order.DoesNotExist:
            return Response({'error':'Order not found'},status=status.HTTP_404_NOT_FOUND)
        
        status_value=request.data.get('status')

        if status_value not in dict(Order.STATUS_CHOICES):
            return Response({'error':'Invalid status'},status=status.HTTP_400_BAD_REQUEST)

        order.status=status_value
        order.save()

        serializer = AdminOrderSerializer(order)

        return Response({'message':'Order status updated Successfully',
                         'order':serializer.data                         
                         },status=status.HTTP_200_OK)
    
    def delete(self,request,pk):

        if request.user.role=='admin':
           order=self.get_order(pk)
           order.delete()
           return Response({
               'message':'Order Deleted Successfully'
           },status=status.HTTP_200_OK)
        return Response({
            'error':'You have no permission'
        },status=status.HTTP_403_FORBIDDEN)
    




        



"""

class CompletedOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            order = Order.objects.get(
                pk=pk,
                customer=request.user,
                is_checked_out=True,
                is_paid=True
            )
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        if order.status == "Delivered":
            order.is_completed = True
            order.save()
            return Response(
                {
                    'message': 'Order marked as completed successfully',
                    'order_id': order.id,
                    'status': 'Completed'
                },
                status=status.HTTP_200_OK
            )
        
        return Response(
            {'error': 'Order cannot be completed until it is delivered'},
            status=status.HTTP_400_BAD_REQUEST
        )
"""