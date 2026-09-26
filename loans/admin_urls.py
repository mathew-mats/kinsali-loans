from django.urls import path
from . import admin_views

app_name = 'admin_panel'

urlpatterns = [
    # Admin Dashboard
    path('', admin_views.admin_dashboard, name='dashboard'),
    
    # Loan Review
    path('loan/<int:loan_id>/', admin_views.admin_loan_detail, name='loan_detail'),
    
    # Loan Actions
    path('approve/<int:loan_id>/', admin_views.admin_approve_loan, name='approve'),
    path('reject/<int:loan_id>/', admin_views.admin_reject_loan, name='reject'),
    path('disburse/<int:loan_id>/', admin_views.admin_disburse_loan, name='disburse'),
    
    # Generate Repayment Schedule
    path('generate-schedule/<int:loan_id>/', admin_views.generate_repayment_schedule, name='generate_schedule'),
]