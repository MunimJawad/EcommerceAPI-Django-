from django.urls import path
from .views import RegisterView,LoginView,UserListView,UserDetailUpdateDeleteView,CategoryCreateOrListView,CategoryUpdateOrDeleteView,ProductListCreateAPIView,ProductDetailOrDeleteView,CartAPI,CheckoutAPIView


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('users/',UserListView.as_view(),name='user_list'),
    path('user/<int:pk>/',UserDetailUpdateDeleteView.as_view(),name="user_detail"),

    #Category URL
    path('categories/',CategoryCreateOrListView.as_view(),name='categories'),
    path('category/<int:pk>/',CategoryUpdateOrDeleteView.as_view(),name='category_detail'),

    #Product URL
    path('products/',ProductListCreateAPIView.as_view(),name='products'),
    path('products/<int:pk>/', ProductDetailOrDeleteView.as_view(), name='product-detail'),

    #Cart URL
    path('cart/',CartAPI.as_view(),name='cart-api'),
    path("checkout/", CheckoutAPIView.as_view(), name="checkout"),
]