from django.urls import path
from . import views, auth

app_name = 'admin_panel'

urlpatterns = [
    # Admin Authentication
    path('login/', auth.admin_login, name='login'),
    path('logout/', auth.admin_logout, name='logout'),
    
    # Admin Dashboard
    path('', views.dashboard, name='dashboard'),
    path('loan/<int:loan_id>/', views.loan_detail, name='loan_detail'),
    
    # Loan Actions
    path('approve/<int:loan_id>/', views.approve_loan, name='approve'),
    path('reject/<int:loan_id>/', views.reject_loan, name='reject'),
    path('disburse/<int:loan_id>/', views.disburse_loan, name='disburse'),
    path('generate-schedule/<int:loan_id>/', views.generate_schedule, name='generate_schedule'),
    
    # Product Management
    path('products/', views.product_list, name='product_list'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/<int:product_id>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:product_id>/delete/', views.product_delete, name='product_delete'),
    
    # Document Verification (NEW)
    path('verifications/', views.verification_list, name='verification_list'),
    path('verify/<int:user_id>/', views.verify_user, name='verify_user'),
    path('reject-verification/<int:user_id>/', views.reject_verification, name='reject_verification'),
    path('payment/<int:payment_id>/mark-paid/', views.mark_payment_paid, name='mark_payment_paid'),
    path('payment-notices/', views.payment_notices_list, name='payment_notices_list'),
    path('payment-notices/<int:notice_id>/approve/', views.approve_payment_notice, name='approve_payment_notice'),
    path('payment-notices/<int:notice_id>/reject/', views.reject_payment_notice, name='reject_payment_notice'),
]