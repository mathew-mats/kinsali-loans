from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

class LoanProduct(models.Model):
    """
    Different loan types Kinsali offers
    """
    name = models.CharField(max_length=100)
    description = models.TextField()
    min_amount = models.DecimalField(max_digits=12, decimal_places=2)
    max_amount = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)  # Annual interest rate in %
    min_tenure_months = models.IntegerField()
    max_tenure_months = models.IntegerField()
    processing_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class LoanApplication(models.Model):
    """
    Main loan application model
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending Review'),
        ('REVIEWING', 'Under Review'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('DISBURSED', 'Disbursed'),
        ('COMPLETED', 'Completed'),
        ('DEFAULTED', 'Defaulted'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loan_applications')
    product = models.ForeignKey(LoanProduct, on_delete=models.SET_NULL, null=True)
    
    # Application details
    amount_requested = models.DecimalField(max_digits=12, decimal_places=2)
    amount_approved = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    tenure_months = models.IntegerField()
    interest_rate_applied = models.DecimalField(max_digits=5, decimal_places=2)
    monthly_emi = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    total_repayment = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Documents (we'll handle file uploads later)
    purpose_of_loan = models.TextField()
    
    # System fields
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    credit_score_at_application = models.IntegerField()
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_loans')
    review_notes = models.TextField(blank=True)
    rejection_reason = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    disbursed_at = models.DateTimeField(null=True, blank=True)

    # ===== DISBURSEMENT DETAILS =====
    disbursement_method = models.CharField(max_length=20, choices=[
        ('MOBILE_MONEY', 'Mobile Money'),
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('CASH_PICKUP', 'Cash Pickup'),
    ], null=True, blank=True)
    disbursement_reference = models.CharField(max_length=100, blank=True, default='')
    disbursement_notes = models.TextField(blank=True, default='')
    disbursed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='disbursed_loans'
    )
    
    def __str__(self):
        return f"Loan #{self.id} - {self.user.username} - {self.status}"
    
    def calculate_emi(self):
        """
        Calculate Equated Monthly Installment
        Formula: EMI = P × r × (1+r)^n / ((1+r)^n - 1)
        Where P = Loan amount, r = monthly interest rate, n = number of months
        """
        P = float(self.amount_requested)
        annual_rate = float(self.interest_rate_applied)
        monthly_rate = annual_rate / (12 * 100)  # Convert annual % to monthly decimal
        n = self.tenure_months
        
        if monthly_rate == 0:
            emi = P / n
        else:
            emi = P * monthly_rate * ((1 + monthly_rate) ** n) / (((1 + monthly_rate) ** n) - 1)
        
        return Decimal(round(emi, 2))
    
    def calculate_total_repayment(self):
        if self.monthly_emi:
            return self.monthly_emi * self.tenure_months
        return Decimal(0)
    
    def save(self, *args, **kwargs):
        # Calculate EMI before saving
        if not self.monthly_emi and self.status == 'PENDING':
            self.monthly_emi = self.calculate_emi()
            self.total_repayment = self.calculate_total_repayment()
        super().save(*args, **kwargs)

class RepaymentSchedule(models.Model):
    """
    Monthly repayment schedule for each loan
    """
    loan = models.ForeignKey(LoanApplication, on_delete=models.CASCADE, related_name='repayments')
    due_date = models.DateField()
    amount_due = models.DecimalField(max_digits=12, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_paid = models.BooleanField(default=False)
    payment_date = models.DateField(null=True, blank=True)
    late_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Payment {self.id} - Loan {self.loan.id}"

class PaymentNotice(models.Model):
    """
    User-submitted payment claims that admin needs to review/approve
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending Review'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('MOBILE_MONEY', 'Mobile Money'),
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('CASH', 'Cash'),
    ]
    
    loan = models.ForeignKey(LoanApplication, on_delete=models.CASCADE, related_name='payment_notices')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_notices')
    
    # What user claims they paid
    amount_claimed = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_id = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='MOBILE_MONEY')
    notes = models.TextField(blank=True, default='')
    
    # Review info
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    reviewed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='reviewed_payment_notices'
    )
    review_notes = models.TextField(blank=True, default='')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notice #{self.id} - Loan #{self.loan.id} - ${self.amount_claimed} ({self.status})"