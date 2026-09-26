from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from decimal import Decimal, InvalidOperation
from .models import LoanApplication, LoanProduct, RepaymentSchedule, PaymentNotice
from .email_service import (
    send_payment_notice_received_email,
    send_admin_new_notice_email,
)

# ============ PUBLIC PAGES ============

def home(request):
    products = LoanProduct.objects.filter(is_active=True)[:3]
    return render(request, 'loans/home.html', {'products': products})

def about(request):
    return render(request, 'loans/about.html')

def services(request):
    products = LoanProduct.objects.filter(is_active=True)
    return render(request, 'loans/services.html', {'products': products})

def how_it_works(request):
    return render(request, 'loans/how_it_works.html')

def faq(request):
    return render(request, 'loans/faq.html')

def contact(request):
    return render(request, 'loans/contact.html')

# ============ USER DASHBOARD ============

@login_required
def dashboard(request):
    """User dashboard showing loans, stats, and upcoming payments"""
    loans = LoanApplication.objects.filter(user=request.user).order_by('-created_at')
    
    # Stats
    total_loans = loans.count()
    active_loans = loans.filter(status__in=['APPROVED', 'DISBURSED'])
    active_count = active_loans.count()
    total_borrowed = sum([loan.amount_approved or 0 for loan in loans if loan.status in ['APPROVED', 'DISBURSED']])
    
    # ===== REPAYMENT TRACKING =====
    # Get all active/disbursed loans with repayment schedules
    active_loan_ids = active_loans.values_list('id', flat=True)
    
    # Upcoming payments (next 30 days)
    today = timezone.now().date()
    upcoming_payments = RepaymentSchedule.objects.filter(
        loan_id__in=active_loan_ids,
        is_paid=False,
        due_date__gte=today
    ).order_by('due_date')[:5]
    
    # Overdue payments
    overdue_payments = RepaymentSchedule.objects.filter(
        loan_id__in=active_loan_ids,
        is_paid=False,
        due_date__lt=today
    ).order_by('due_date')
    
    # Next payment due
    next_payment = upcoming_payments.first()
    next_payment_days = None
    if next_payment:
        days_until = (next_payment.due_date - today).days
        next_payment_days = days_until if days_until >= 0 else 0
    
    context = {
        'loans': loans,
        'total_loans': total_loans,
        'active_loans_count': active_count,
        'total_borrowed': total_borrowed,
        'credit_score': request.user.profile.credit_score,
        'upcoming_payments': upcoming_payments,
        'overdue_payments': overdue_payments,
        'overdue_count': overdue_payments.count(),
        'next_payment': next_payment,
        'next_payment_days': next_payment_days,
        'today': today,
    }
    return render(request, 'loans/dashboard.html', context)

# ============ LOAN DETAIL ============

@login_required
def loan_detail(request, loan_id):
    """View details of a specific loan with repayment schedule"""
    loan = get_object_or_404(LoanApplication, id=loan_id, user=request.user)
    
    # Get repayment schedule
    repayments = RepaymentSchedule.objects.filter(loan=loan).order_by('due_date')
    
    # Annotate each repayment with balance
    for r in repayments:
        r.balance = (r.amount_due or 0) - (r.amount_paid or 0)
    
    # Calculate summary
    total_paid = sum([r.amount_paid for r in repayments])
    total_due = sum([r.amount_due for r in repayments])
    total_remaining = total_due - total_paid
    paid_count = repayments.filter(is_paid=True).count()
    total_count = repayments.count()
    remaining_count = total_count - paid_count
    
    today = timezone.now().date()
    next_payment = repayments.filter(is_paid=False, due_date__gte=today).first()
    next_payment_days = None
    if next_payment:
        next_payment_days = (next_payment.due_date - today).days
    overdue_count = repayments.filter(is_paid=False, due_date__lt=today).count()
    
    # ===== PAYMENT NOTICES (NEW) =====
    payment_notices = PaymentNotice.objects.filter(
        loan=loan, 
        user=request.user
    ).order_by('-created_at')
    pending_notices_count = payment_notices.filter(status='PENDING').count()
    
    context = {
        'loan': loan,
        'repayments': repayments,
        'total_paid': total_paid,
        'total_due': total_due,
        'total_remaining': total_remaining,
        'paid_count': paid_count,
        'total_count': total_count,
        'remaining_count': remaining_count,
        'next_payment': next_payment,
        'next_payment_days': next_payment_days,
        'overdue_count': overdue_count,
        'today': today,
        'progress_percentage': int((paid_count / total_count * 100)) if total_count > 0 else 0,
        'payment_notices': payment_notices,               # ← NEW
        'pending_notices_count': pending_notices_count,   # ← NEW
    }
    return render(request, 'loans/loan_detail.html', context)

# ============ APPLY FOR LOAN ============

@login_required
def apply_loan(request):
    """Apply for a new loan"""
    if request.method == 'POST':
        product_id = request.POST.get('product')
        amount = Decimal(request.POST.get('amount'))
        tenure = int(request.POST.get('tenure'))
        purpose = request.POST.get('purpose')
        
        product = get_object_or_404(LoanProduct, id=product_id)
        
        if amount < product.min_amount or amount > product.max_amount:
            messages.error(request, f'Amount must be between ${product.min_amount} and ${product.max_amount}')
            return redirect('loans:apply_loan')
        
        if request.user.profile.credit_score < 300:
            messages.error(request, 'Your credit score is too low for a loan at this time.')
            return redirect('loans:dashboard')
        
        if not request.user.profile.is_verified:
            messages.error(request, 'Your account is not verified. Please wait for admin verification.')
            return redirect('loans:dashboard')
        
        loan = LoanApplication(
            user=request.user,
            product=product,
            amount_requested=amount,
            tenure_months=tenure,
            interest_rate_applied=product.interest_rate,
            purpose_of_loan=purpose,
            credit_score_at_application=request.user.profile.credit_score,
            status='PENDING'
        )
        loan.save()
        
        messages.success(request, '✅ Your loan application has been submitted successfully!')
        return redirect('loans:dashboard')
    
    products = LoanProduct.objects.filter(is_active=True)
    return render(request, 'loans/apply_loan.html', {'products': products})

@login_required
def submit_payment_notice(request, loan_id):
    """User submits a payment claim for admin review"""
    loan = get_object_or_404(LoanApplication, id=loan_id, user=request.user)
    
    # Only allow if loan is active
    if loan.status not in ['DISBURSED']:
        messages.error(request, 'You can only submit payments for active loans.')
        return redirect('loans:loan_detail', loan_id=loan.id)
    
    if request.method == 'POST':
        try:
            amount = Decimal(request.POST.get('amount_claimed', '0'))
            transaction_id = request.POST.get('transaction_id', '').strip()
            payment_method = request.POST.get('payment_method', 'MOBILE_MONEY')
            notes = request.POST.get('notes', '').strip()
            
            if amount <= 0:
                messages.error(request, 'Amount must be greater than 0.')
                return redirect('loans:loan_detail', loan_id=loan.id)
            
            if not transaction_id:
                messages.error(request, 'Please provide the transaction ID from your payment.')
                return redirect('loans:loan_detail', loan_id=loan.id)
            
            # ✅ FIXED: Capture the created object directly
            notice = PaymentNotice.objects.create(
                loan=loan,
                user=request.user,
                amount_claimed=amount,
                transaction_id=transaction_id,
                payment_method=payment_method,
                notes=notes,
                status='PENDING'
            )
            
            # Send email to user (confirmation)
            send_payment_notice_received_email(notice)
            
            # Send email to all admins
            admin_emails = list(
                User.objects.filter(is_staff=True, is_active=True)
                .exclude(email='')
                .values_list('email', flat=True)
            )
            send_admin_new_notice_email(notice, admin_emails)
            
            messages.success(
                request, 
                f'✅ Payment notice submitted! We will verify and record your payment shortly.'
            )
            return redirect('loans:loan_detail', loan_id=loan.id)
        
        except (ValueError, InvalidOperation):
            messages.error(request, 'Invalid amount entered.')
            return redirect('loans:loan_detail', loan_id=loan.id)
    
    return redirect('loans:loan_detail', loan_id=loan.id)