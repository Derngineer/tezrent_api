from rest_framework import permissions


class IsStaffUser(permissions.BasePermission):
    """
    Permission class for staff/admin users only.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff


class IsSellerOwner(permissions.BasePermission):
    """
    Permission class for seller company users.
    Allows sellers to access CRM records related to their company.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Staff can access everything
        if request.user.is_staff:
            return True
        
        # Check if user has a company profile
        if not hasattr(request.user, 'company_profile'):
            return False
        
        user_company = request.user.company_profile
        
        # Check if object is related to the user's company
        if hasattr(obj, 'company') and obj.company == user_company:
            return True
        
        return False


class IsCustomerOwner(permissions.BasePermission):
    """
    Permission class for customer users.
    Allows customers to access only their own CRM records.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Staff can access everything
        if request.user.is_staff:
            return True
        
        # Check if user has a customer profile
        if not hasattr(request.user, 'customer_profile'):
            return False
        
        user_customer = request.user.customer_profile
        
        # Check if object belongs to the customer
        if hasattr(obj, 'customer') and obj.customer == user_customer:
            return True
        
        return False


class IsStaffOrSellerOwner(permissions.BasePermission):
    """
    Permission class that allows staff or seller owners.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Staff can access everything
        if request.user.is_staff:
            return True
        
        # Check if user has a company profile
        if hasattr(request.user, 'company_profile'):
            user_company = request.user.company_profile
            
            # Check if object is related to the user's company
            if hasattr(obj, 'company') and obj.company == user_company:
                return True
        
        return False


class IsStaffOrCustomerOwner(permissions.BasePermission):
    """
    Permission class that allows staff or customer owners.
    Used for support tickets where customers can see their own tickets.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Staff can access everything
        if request.user.is_staff:
            return True
        
        # Check if user has a customer profile
        if hasattr(request.user, 'customer_profile'):
            user_customer = request.user.customer_profile
            
            # Check if object belongs to the customer
            if hasattr(obj, 'customer') and obj.customer == user_customer:
                return True
        
        return False


class CanCreateLead(permissions.BasePermission):
    """
    Permission class for creating leads.
    Staff and sellers can create leads.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Staff can always create leads
        if request.user.is_staff:
            return True
        
        # Sellers can create leads for their company
        if hasattr(request.user, 'company_profile'):
            return True
        
        return False


class CanCreateTicket(permissions.BasePermission):
    """
    Permission class for creating support tickets.
    Anyone authenticated can create tickets.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class CanViewSensitiveData(permissions.BasePermission):
    """
    Permission class for viewing sensitive CRM data like internal notes.
    Only staff and related sellers can view.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Staff can always view
        if request.user.is_staff:
            return True
        
        # Sellers can view their own data
        if hasattr(request.user, 'company_profile'):
            return True
        
        return False
    
    def has_object_permission(self, request, view, obj):
        # Staff can access everything
        if request.user.is_staff:
            return True
        
        # Sellers can only view data related to their company
        if hasattr(request.user, 'company_profile'):
            user_company = request.user.company_profile
            if hasattr(obj, 'company') and obj.company == user_company:
                return True
        
        return False
