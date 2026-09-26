from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils import timezone
from .models import LoanApplication, LoanProduct, RepaymentSchedule
from decimal import Decimal
from dateutil.relativedelta import relativedelta
import datetime

# ============ ADMIN DASHBOARD ============

@staff_member_required
def admin_dashboard(request):
    """Admin dashboard showing all loans"""
    pending_loans = LoanApplication.objects.filter(status='PENDING').order_by('-created_at')
    reviewing_loans = LoanApplication.objects.filter(status='REVIEWING')
    approved_loans = LoanApplication.objects.filter(status='APPROVED')
    rejected_loans = LoanApplication.objects.filter(status='REJECTED')
    disbursed_loans = LoanApplication.objects.filter(status='DISBURSED')
    
    # Calculate totals
    total_pending = pending_loans.count()
    total_reviewing = reviewing_loans.count()
    total_approved = approved_loans.count()
    total_rejected = rejected_loans.count()
    total_disbursed = disbursed_loans.count()
    
    # Calculate total amount disbursed
    total_disbursed_amount = sum([loan.amount_approved or 0 for loan in disbursed_loans])
    
    context = {
        'pending_loans': pending_loans,
        'reviewing_loans': reviewing_loans,
        'approved_loans': approved_loans,
        'rejected_loans': rejected_loans,
        'disbursed_loans': disbursed_loans,
        'total_pending': total_pending,
        'total_reviewing': total_reviewing,
        'total_approved': total_approved,
        'total_rejected': total_rejected,
        'total_disbursed': total_disbursed,
        'total_disbursed_amount': total_disbursed_amount,
        'all_loans_count': LoanApplication.objects.count(),
    }
    return render(request, 'admin/dashboard.html', context)

# ============ LOAN REVIEW ============

@staff_member_required
def admin_loan_detail(request, loan_id):
    """View full loan details for admin review"""
    loan = get_object_or_404(LoanApplication, id=loan_id)
    return render(request, 'admin/loan_detail.html', {'loan': loan})

# ============ LOAN ACTIONS ============

@staff_member_required
def admin_approve_loan(request, loan_id):
    """Approve a loan"""
    if request.method == 'POST':
        loan = get_object_or_404(LoanApplication, id=loan_id)
        loan.status = 'APPROVED'
        loan.approved_at = timezone.now()
        loan.reviewed_by = request.user
        loan.review_notes = request.POST.get('notes', '')
        loan.amount_approved = request.POST.get('amount_approved', loan.amount_requested)
        loan.save()
        
        messages.success(request, f'✅ Loan #{loan.id} approved successfully!')
        return redirect('admin_panel:dashboard')
    return redirect('admin_panel:loan_detail', loan_id=loan_id)

@staff_member_required
def admin_reject_loan(request, loan_id):
    """Reject a loan"""
    if request.method == 'POST':
        loan = get_object_or_404(LoanApplication, id=loan_id)
        loan.status = 'REJECTED'
        loan.reviewed_by = request.user
        loan.review_notes = request.POST.get('notes', '')
        loan.rejection_reason = request.POST.get('rejection_reason', '')
        loan.save()
        
        messages.warning(request, f'❌ Loan #{loan.id} rejected.')
        return redirect('admin_panel:dashboard')
    return redirect('admin_panel:loan_detail', loan_id=loan_id)

@staff_member_required
def admin_disburse_loan(request, loan_id):
    """Mark a loan as disbursed"""
    if request.method == 'POST':
        loan = get_object_or_404(LoanApplication, id=loan_id)
        loan.status = 'DISBURSED'
        loan.disbursed_at = timezone.now()
        loan.save()
        
        messages.success(request, f'💰 Loan #{loan.id} has been disbursed!')
        return redirect('admin_panel:dashboard')
    return redirect('admin_panel:loan_detail', loan_id=loan_id)

# ============ REPAYMENT SCHEDULE ============

@staff_member_required
def generate_repayment_schedule(request, loan_id):
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