from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from accounts.models import UserProfile
from loans.models import LoanApplication, LoanProduct, RepaymentSchedule
from .auth import admin_login_required
from dateutil.relativedelta import relativedelta
from decimal import Decimal, InvalidOperation
from loans.models import LoanApplication, LoanProduct, RepaymentSchedule, PaymentNotice

from loans.email_service import (
    send_verification_approved_email,
    send_verification_rejected_email,
    send_loan_approved_email,
    send_loan_rejected_email,
    send_loan_disbursed_email,
    send_admin_new_notice_email,
    send_payment_approved_email,
    send_payment_rejected_email,
    send_loan_completed_email,
)

# ============ ADMIN DASHBOARD ============

@admin_login_required
def dashboard(request):
    """Admin dashboard with loan stats and pending applications"""
    pending_loans = LoanApplication.objects.filter(status='PENDING').order_by('-created_at')
    reviewing_loans = LoanApplication.objects.filter(status='REVIEWING')
    approved_loans = LoanApplication.objects.filter(status='APPROVED')
    rejected_loans = LoanApplication.objects.filter(status='REJECTED')
    disbursed_loans = LoanApplication.objects.filter(status='DISBURSED')
    all_loans = LoanApplication.objects.all().order_by('-created_at')  # FIXED: added all_loans
    
    # Calculate totals
    total_pending = pending_loans.count()
    total_reviewing = reviewing_loans.count()
    total_approved = approved_loans.count()
    total_rejected = rejected_loans.count()
    total_disbursed = disbursed_loans.count()
    total_loans = all_loans.count()
    
    # Total amount disbursed
    total_disbursed_amount = sum([loan.amount_approved or 0 for loan in disbursed_loans])
    
    context = {
        'pending_loans': pending_loans,
        'reviewing_loans': reviewing_loans,
        'approved_loans': approved_loans,
        'rejected_loans': rejected_loans,
        'disbursed_loans': disbursed_loans,
        'all_loans': all_loans,  # FIXED: added to context
        'total_pending': total_pending,
        'total_reviewing': total_reviewing,
        'total_approved': total_approved,
        'total_rejected': total_rejected,
        'total_disbursed': total_disbursed,
        'total_loans': total_loans,
        'total_disbursed_amount': total_disbursed_amount,
    }
    return render(request, 'admin/dashboard.html', context)

# ============ REVIEW LOAN ============

@admin_login_required
def loan_detail(request, loan_id):
    """View full loan details for admin review"""
    loan = get_object_or_404(LoanApplication, id=loan_id)
    return render(request, 'admin/loan_detail.html', {'loan': loan})

# ============ LOAN ACTIONS ============

@admin_login_required
def approve_loan(request, loan_id):
    """Approve a loan application"""
    if request.method == 'POST':
        loan = get_object_or_404(LoanApplication, id=loan_id)
        loan.status = 'APPROVED'
        loan.approved_at = timezone.now()
        loan.reviewed_by = request.user
        loan.review_notes = request.POST.get('notes', '')
        loan.amount_approved = request.POST.get('amount_approved', loan.amount_requested)
        loan.save()
        send_loan_approved_email(loan)
        
        messages.success(request, f'✅ Loan #{loan.id} approved successfully!')
        return redirect('admin_panel:dashboard')
    return redirect('admin_panel:loan_detail', loan_id=loan_id)

@admin_login_required
def reject_loan(request, loan_id):
    """Reject a loan application"""
    if request.method == 'POST':
        loan = get_object_or_404(LoanApplication, id=loan_id)
        loan.status = 'REJECTED'
        loan.reviewed_by = request.user
        loan.review_notes = request.POST.get('notes', '')
        loan.rejection_reason = request.POST.get('rejection_reason', '')
        loan.save()
        send_loan_rejected_email(loan, loan.rejection_reason)
        
        messages.warning(request, f'❌ Loan #{loan.id} rejected.')
        return redirect('admin_panel:dashboard')
    return redirect('admin_panel:loan_detail', loan_id=loan_id)

@admin_login_required
def disburse_loan(request, loan_id):
    """Mark a loan as disbursed with details"""
    if request.method == 'POST':
        loan = get_object_or_404(LoanApplication, id=loan_id)
        loan.status = 'DISBURSED'
        loan.disbursed_at = timezone.now()
        loan.disbursed_by = request.user
        loan.disbursement_method = request.POST.get('disbursement_method', 'MOBILE_MONEY')
        loan.disbursement_reference = request.POST.get('disbursement_reference', '')
        loan.disbursement_notes = request.POST.get('disbursement_notes', '')
        loan.save()
        send_loan_disbursed_email(loan)
        
        messages.success(request, f'💰 Loan #{loan.id} has been disbursed!')
        return redirect('admin_panel:dashboard')
    return redirect('admin_panel:loan_detail', loan_id=loan_id)

@admin_login_required
def generate_schedule(request, loan_id):
    """Generate monthly repayment schedule for a loan"""
    loan = get_object_or_404(LoanApplication, id=loan_id)
    
    if loan.status not in ['APPROVED', 'DISBURSED']:
        messages.error(request, 'Loan must be approved or disbursed first.')
        return redirect('admin_panel:loan_detail', loan_id=loan_id)
    
    # Check if schedule already exists
    if RepaymentSchedule.objects.filter(loan=loan).exists():
        messages.warning(request, 'Repayment schedule already exists for this loan.')
        return redirect('admin_panel:loan_detail', loan_id=loan_id)
    
    # Generate monthly payments
    start_date = timezone.now().date()
    emi = loan.monthly_emi
    
    for i in range(loan.tenure_months):
        due_date = start_date + relativedelta(months=i+1)
        RepaymentSchedule.objects.create(
            loan=loan,
            due_date=due_date,
            amount_due=emi,
            amount_paid=0,
            is_paid=False
        )
    
    messages.success(request, f'📋 Repayment schedule generated for Loan #{loan.id}')
    return redirect('admin_panel:loan_detail', loan_id=loan_id)

# ============ PRODUCT MANAGEMENT ============

@admin_login_required
def product_list(request):
    """List all loan products"""
    products = LoanProduct.objects.all().order_by('-is_active', 'name')
    return render(request, 'admin/products.html', {'products': products})

@admin_login_required
def product_create(request):
    """Create a new loan product"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        min_amount = request.POST.get('min_amount')
        max_amount = request.POST.get('max_amount')
        interest_rate = request.POST.get('interest_rate')
        min_tenure_months = request.POST.get('min_tenure_months')
        max_tenure_months = request.POST.get('max_tenure_months')
        processing_fee = request.POST.get('processing_fee')
        is_active = request.POST.get('is_active') == 'on'
        
        try:
            product = LoanProduct.objects.create(
                name=name,
                description=description,
                min_amount=min_amount,
                max_amount=max_amount,
                interest_rate=interest_rate,
                min_tenure_months=min_tenure_months,
                max_tenure_months=max_tenure_months,
                processing_fee=processing_fee or 0,
                is_active=is_active
            )
            messages.success(request, f'✅ Product "{product.name}" created successfully!')
            return redirect('admin_panel:product_list')
        except Exception as e:
            messages.error(request, f'❌ Error creating product: {str(e)}')
            return redirect('admin_panel:product_create')
    
    return render(request, 'admin/product_form.html')

@admin_login_required
def product_edit(request, product_id):
    """Edit an existing loan product"""
    product = get_object_or_404(LoanProduct, id=product_id)
    
    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        product.min_amount = request.POST.get('min_amount')
        product.max_amount = request.POST.get('max_amount')
        product.interest_rate = request.POST.get('interest_rate')
        product.min_tenure_months = request.POST.get('min_tenure_months')
        product.max_tenure_months = request.POST.get('max_tenure_months')
        product.processing_fee = request.POST.get('processing_fee') or 0
        product.is_active = request.POST.get('is_active') == 'on'
        product.save()
        
        messages.success(request, f'✅ Product "{product.name}" updated successfully!')
        return redirect('admin_panel:product_list')
    
    return render(request, 'admin/product_form.html', {'product': product})

@admin_login_required
def product_delete(request, product_id):
    """Delete a loan product"""
    product = get_object_or_404(LoanProduct, id=product_id)
    
    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'✅ Product "{product_name}" deleted successfully!')
        return redirect('admin_panel:product_list')
    
    return render(request, 'admin/product_confirm_delete.html', {'product': product})

# ============ DOCUMENT VERIFICATION ============

@admin_login_required
def verification_list(request):
    """Admin view to see all pending verifications"""
    pending_users = UserProfile.objects.filter(
        verification_status='PENDING'
    ).select_related('user').order_by('-created_at')
    
    verified_users = UserProfile.objects.filter(
        verification_status='VERIFIED'
    ).select_related('user').order_by('-verified_at')
    
    rejected_users = UserProfile.objects.filter(
        verification_status='REJECTED'
    ).select_related('user').order_by('-created_at')
    
    context = {
        'pending_users': pending_users,
        'verified_users': verified_users,
        'rejected_users': rejected_users,
        'pending_count': pending_users.count(),
        'verified_count': verified_users.count(),
        'rejected_count': rejected_users.count(),
    }
    return render(request, 'admin/verification_list.html', context)

@admin_login_required
def verify_user(request, user_id):
    """Approve a user's documents and verify them"""
    if request.method == 'POST':
        profile = get_object_or_404(UserProfile, user_id=user_id)
        profile.is_verified = True
        profile.national_id_verified = True
        profile.verification_status = 'VERIFIED'
        profile.verified_at = timezone.now()
        profile.verified_by = request.user
        profile.verification_notes = request.POST.get('notes', '')
        profile.credit_score = profile.calculate_credit_score()
        profile.save()
        send_verification_approved_email(profile.user)
        
        messages.success(request, f'✅ User {profile.user.username} verified successfully!')
        return redirect('admin_panel:verification_list')
    return redirect('admin_panel:verification_list')

@admin_login_required
def reject_verification(request, user_id):
    """Reject a user's documents with reason"""
    if request.method == 'POST':
        profile = get_object_or_404(UserProfile, user_id=user_id)
        profile.is_verified = False
        profile.national_id_verified = False
        profile.verification_status = 'REJECTED'
        profile.verification_notes = request.POST.get('notes', 'No reason provided')
        profile.save()
        send_verification_rejected_email(profile.user, profile.verification_notes)
        
        messages.warning(request, f'❌ User {profile.user.username} verification rejected.')
        return redirect('admin_panel:verification_list')
    return redirect('admin_panel:verification_list')

@admin_login_required
def mark_payment_paid(request, payment_id):
    """Record a payment (full or partial) for a repayment schedule entry"""
    if request.method == 'POST':
        payment = get_object_or_404(RepaymentSchedule, id=payment_id)
        
        # Get amount from form (default to full amount due)
        try:
            amount_received = Decimal(request.POST.get('amount_paid', payment.amount_due))
        except:
            amount_received = payment.amount_due
        
        # Add to existing amount paid (in case of multiple partial payments)
        payment.amount_paid = (payment.amount_paid or 0) + amount_received
        
        # Cap at amount_due (can't overpay this installment)
        if payment.amount_paid >= payment.amount_due:
            payment.amount_paid = payment.amount_due
            payment.is_paid = True
            payment.payment_date = timezone.now().date()
        
        payment.save()
        
        loan = payment.loan
        
        # Auto-complete loan if ALL payments are fully paid
        all_paid = not loan.repayments.filter(is_paid=False).exists()
        
        if all_paid:
            loan.status = 'COMPLETED'
            loan.save()
            messages.success(
                request,
                f'🎉 Payment of ${amount_received} recorded! Loan #{loan.id} is now COMPLETED!'
            )
        else:
            remaining_in_payment = payment.amount_due - payment.amount_paid
            if remaining_in_payment > 0:
                messages.success(
                    request,
                    f'💰 Partial payment of ${amount_received} recorded. '
                    f'${remaining_in_payment} remaining on this installment.'
                )
            else:
                remaining_count = loan.repayments.filter(is_paid=False).count()
                messages.success(
                    request,
                    f'✅ Payment recorded! {remaining_count} installment(s) remaining on Loan #{loan.id}.'
                )
        
        return redirect('admin_panel:loan_detail', loan_id=loan.id)
    return redirect('admin_panel:dashboard')

@admin_login_required
def loan_detail(request, loan_id):
    """View full loan details for admin review"""
    loan = get_object_or_404(LoanApplication, id=loan_id)
    
    # Annotate each repayment with balance
    repayments = loan.repayments.all().order_by('due_date')
    for r in repayments:
        r.balance = (r.amount_due or 0) - (r.amount_paid or 0)
    
    return render(request, 'admin/loan_detail.html', {
        'loan': loan,
        'repayments': repayments,
        'today': timezone.now().date(),
    })

# ============ PAYMENT NOTICES ============

@admin_login_required
def payment_notices_list(request):
    """View all user-submitted payment notices"""
    pending_notices = PaymentNotice.objects.filter(status='PENDING').order_by('-created_at')
    approved_notices = PaymentNotice.objects.filter(status='APPROVED').order_by('-reviewed_at')[:20]
    rejected_notices = PaymentNotice.objects.filter(status='REJECTED').order_by('-reviewed_at')[:20]
    
    context = {
        'pending_notices': pending_notices,
        'approved_notices': approved_notices,
        'rejected_notices': rejected_notices,
        'pending_count': pending_notices.count(),
    }
    return render(request, 'admin/payment_notices.html', context)


@admin_login_required
def approve_payment_notice(request, notice_id):
    """Approve a payment notice and auto-apply to schedule (FIFO)"""
    if request.method == 'POST':
        notice = get_object_or_404(PaymentNotice, id=notice_id)
        
        if notice.status != 'PENDING':
            messages.error(request, 'This notice has already been reviewed.')
            return redirect('admin_panel:payment_notices_list')
        
        # Mark notice as approved
        notice.status = 'APPROVED'
        notice.reviewed_by = request.user
        notice.reviewed_at = timezone.now()
        notice.review_notes = request.POST.get('review_notes', '')
        notice.save()
        
        # Apply the amount to schedule (FIFO - earliest unpaid first)
        amount_to_apply = Decimal(str(notice.amount_claimed))
        unpaid_payments = notice.loan.repayments.filter(is_paid=False).order_by('due_date')
        
        for payment in unpaid_payments:
            if amount_to_apply <= 0:
                break
            
            balance = (payment.amount_due or 0) - (payment.amount_paid or 0)
            if balance <= 0:
                continue
            
            apply_amount = min(balance, amount_to_apply)
            payment.amount_paid = (payment.amount_paid or 0) + apply_amount
            
            if payment.amount_paid >= payment.amount_due:
                payment.amount_paid = payment.amount_due
                payment.is_paid = True
                payment.payment_date = timezone.now().date()
            
            payment.save()
            amount_to_apply -= apply_amount
        
        # Check if loan is fully paid
        if not notice.loan.repayments.filter(is_paid=False).exists():
            notice.loan.status = 'COMPLETED'
            notice.loan.save()
            send_payment_approved_email(notice)
            send_loan_completed_email(notice.loan)
            messages.success(
                request, 
                f'🎉 Payment approved! Loan #{notice.loan.id} is now COMPLETED!'
            )
        else:
            send_payment_approved_email(notice)
            messages.success(
                request, 
                f'✅ Payment of ${notice.amount_claimed} approved and applied to Loan #{notice.loan.id}.'
            )
        
        return redirect('admin_panel:payment_notices_list')
    return redirect('admin_panel:payment_notices_list')


@admin_login_required
def reject_payment_notice(request, notice_id):
    """Reject a payment notice with reason"""
    if request.method == 'POST':
        notice = get_object_or_404(PaymentNotice, id=notice_id)
        
        if notice.status != 'PENDING':
            messages.error(request, 'This notice has already been reviewed.')
            return redirect('admin_panel:payment_notices_list')
        
        notice.status = 'REJECTED'
        notice.reviewed_by = request.user
        notice.reviewed_at = timezone.now()
        notice.review_notes = request.POST.get('review_notes', 'No reason provided')
        notice.save()
        send_payment_rejected_email(notice)
        
        messages.warning(request, f'❌ Payment notice #{notice.id} rejected.')
        return redirect('admin_panel:payment_notices_list')
    return redirect('admin_panel:payment_notices_list')