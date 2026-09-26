from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import date
import re

# ============ UGANDAN NIN VALIDATION ============

def validate_ugandan_nin(nin):
    """
    Validate Ugandan National Identification Number (NIN)
    Format: Must be exactly 14 characters
    - Can contain letters (A-Z) and numbers (0-9)
    - At least 1 letter and at least 1 number
    - Case insensitive
    - No special characters or spaces
    Examples: C123456789012, CF92105100HN4G, CM123456789012
    """
    if not nin:
        return False
    
    nin = nin.strip().upper()
    
    # Must be exactly 14 characters
    if len(nin) != 14:
        return False
    
    # Must contain only letters and numbers (no special characters)
    if not nin.isalnum():
        return False
    
    # Must have at least one letter and at least one number
    if not any(c.isalpha() for c in nin):
        return False
    if not any(c.isdigit() for c in nin):
        return False
    
    return True

# ============ USER PROFILE ============

class UserProfile(models.Model):
    """Extends Django's default User with additional fields"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Contact Details
    phone_number = models.CharField(max_length=15, blank=True, default='')
    date_of_birth = models.DateField(null=True, blank=True)
    
    # Identification
    national_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    national_id_verified = models.BooleanField(default=False)
    
    # Employment
    employment_status = models.CharField(max_length=50, choices=[
        ('EMPLOYED', 'Employed'),
        ('SELF_EMPLOYED', 'Self Employed'),
        ('BUSINESS', 'Business Owner'),
        ('STUDENT', 'Student'),
        ('UNEMPLOYED', 'Unemployed'),
    ], default='UNEMPLOYED')
    monthly_income = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    employer_name = models.CharField(max_length=200, blank=True, default='')
    
    # Address
    residential_address = models.TextField(blank=True, default='')
    city = models.CharField(max_length=100, blank=True, default='')
    state = models.CharField(max_length=50, blank=True, default='')
    
    # Documents (NEW)
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        null=True,
        blank=True,
        help_text="Upload a clear photo of yourself"
    )
    national_id_image = models.ImageField(
        upload_to='national_ids/',
        null=True,
        blank=True,
        help_text="Upload a clear photo of your National ID (front side)"
    )
    
    # Verification Status (NEW)
    is_verified = models.BooleanField(default=False)
    verification_status = models.CharField(max_length=20, choices=[
        ('PENDING', 'Pending Verification'),
        ('VERIFIED', 'Verified'),
        ('REJECTED', 'Rejected'),
        ('INCOMPLETE', 'Documents Incomplete'),
    ], default='PENDING')
    verification_notes = models.TextField(blank=True, default='')
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='verified_profiles'
    )
    
    # System fields
    credit_score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ===== PAYMENT / DISBURSEMENT DETAILS =====
    # Mobile Money
    mobile_money_number = models.CharField(max_length=15, blank=True, default='')
    mobile_money_network = models.CharField(max_length=20, choices=[
        ('MTN', 'MTN MoMo'),
        ('AIRTEL', 'Airtel Money'),
        ('TELECOM', 'Telecom'),
        ('OTHER', 'Other'),
    ], blank=True, default='')

    # Bank Account (Optional)
    bank_name = models.CharField(max_length=100, blank=True, default='')
    bank_account_name = models.CharField(max_length=100, blank=True, default='')
    bank_account_number = models.CharField(max_length=30, blank=True, default='')

    # Preferred disbursement method
    preferred_disbursement = models.CharField(max_length=20, choices=[
        ('MOBILE_MONEY', 'Mobile Money'),
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('CASH_PICKUP', 'Cash Pickup'),
    ], default='MOBILE_MONEY')
    
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def calculate_credit_score(self):
        """Simple credit scoring logic"""
        base_score = 300
        if self.employment_status in ['EMPLOYED', 'SELF_EMPLOYED']:
            base_score += 100
        if self.monthly_income > 1000:
            base_score += 50
        if self.monthly_income > 5000:
            base_score += 100
        if self.is_verified:
            base_score += 50
        if self.national_id_verified:
            base_score += 50
        return base_score
    
    def is_nin_valid(self):
        """Check if National ID is valid Ugandan format"""
        if not self.national_id:
            return False
        return validate_ugandan_nin(self.national_id)

# ============ SIGNALS ============

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        pass


