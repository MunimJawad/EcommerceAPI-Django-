from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        # Allow GET, HEAD, OPTIONS for everyone
        if request.method in SAFE_METHODS:
            return True
        # Only allow admin users to POST, PUT, DELETE, etc.
        return request.user and request.user.is_staff

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role=="admin"
    
class IsStaff(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role=="satff"
    
class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role=="customer"
    
class IsAdminOrSelf(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Admin can access any object
        if request.user.role == 'admin':
            return True
        # Non-admin user can only access their own object
        return request.user == obj
    

    