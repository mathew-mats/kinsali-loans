from django.urls import path
from . import views

app_name = 'loans'

urlpatterns = [
    # Public pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('how-it-works/', views.how_it_works, name='how_it_works'),
    path('faq/', views.faq, name='faq'),
    path('contact/', views.contact, name='contact'),
    
    # User pages (login required)
    path('dashboard/', views.dashboard, name='dashboard'),
    path('apply/', views.apply_loan, name='apply_loan'),
    path('loan/<int:loan_id>/', views.loan_detail, name='loan_detail'),
    path('loan/<int:loan_id>/submit-payment/', views.submit_payment_notice, name='submit_payment_notice'),
]