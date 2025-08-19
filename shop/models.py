from django.db import models
from django.contrib.auth.models import AbstractUser

# Custom user model
class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('customer', 'Customer'),
        ('staff', 'Staff'),
    )
    email = models.EmailField(unique=True)  # Email must be unique
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')

    def __str__(self):
        return self.username


# Product Category
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


# Product
class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)  # Used for cart vs order
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')  # ✅ new field
    
    @property
    def get_cart_total(self):
        """Sum of all items in cart"""
        items = self.items.all()
        return sum([item.get_total for item in items])
    
    @property 
    def get_total_item(self):
        """Sum of total items"""
        items=self.items.all()
        return sum([item.quantity for item in items])

    def __str__(self):
        return f"Order #{self.id} by {self.customer.username} - {self.status}"


# Order Item
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    @property
    def get_total(self):
        """Total price of this item"""
        return self.product.price*self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.title}"


# Shipping Address
class ShippingAddress(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    date_added = models.DateTimeField(auto_now_add=True,null=True)

    def __str__(self):
        return f"{self.address}, {self.city}"
