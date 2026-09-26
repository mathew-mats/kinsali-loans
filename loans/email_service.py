from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import threading


def send_email_async(subject, template_name, context, recipient_list):
    """
    Send an HTML email asynchronously (in background thread).
    Won't block the web request if email fails.
    """
    def _send():
        try:
            html_content = render_to_string(f'emails/{template_name}.html', context)
            text_content = strip_tags(html_content)
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=recipient_list,
            )
            email.attach_alternative(html_content, "text/html")
            email.send(fail_silently=True)
        except Exception as e:
            # Log error but don't crash the app
            print(f"[EMAIL ERROR] {subject} -> {recipient_list}: {e}")
    
    thread = threading.Thread(target=_send)
    thread.daemon = True
    thread.start()


# ============ EMAIL FUNCTIONS ============

def send_welcome_email(user):
    """Sent when user registers"""
    send_email_async(
        subject='Welcome to Kinsali Loans! 🎉',
        template_name='welcome',
        context={
            'user': user,
            'username': user.username,
        },
        recipient_list=[user.email],
    )


def send_verification_approved_email(user):
    """Sent when admin verifies the user"""
    send_email_async(
        subject='✅ Your Kinsali Loans account is verified!',
        template_name='verification_approved',
        context={'user': user},
        recipient_list=[user.email],
    )


def send_verification_rejected_email(user, reason):
    """Sent when admin rejects verification"""
    send_email_async(
        subject='❌ Kinsali Loans verification update',
        template_name='verification_rejected',
        context={
            'user': user,
            'reason': reason,
        },
        recipient_list=[user.email],
    )


def send_loan_approved_email(loan):
    """Sent when admin approves a loan"""
    send_email_async(
        subject=f'🎉 Loan #{loan.id} Approved!',
        template_name='loan_approved',
        context={'loan': loan, 'user': loan.user},
        recipient_list=[loan.user.email],
    )


def send_loan_rejected_email(loan, reason):
    """Sent when admin rejects a loan"""
    send_email_async(
        subject=f'❌ Loan #{loan.id} Application Update',
        template_name='loan_rejected',
        context={'loan': loan, 'user': loan.user, 'reason': reason},
        recipient_list=[loan.user.email],
    )


def send_loan_disbursed_email(loan):
    """Sent when admin disburses the loan"""
    send_email_async(
        subject=f'💰 Loan #{loan.id} has been disbursed!',
        template_name='loan_disbursed',
        context={'loan': loan, 'user': loan.user},
        recipient_list=[loan.user.email],
    )


def send_payment_notice_received_email(notice):
    """Sent to user confirming their payment notice was received"""
    send_email_async(
        subject=f'📩 Payment Notice Received – Loan #{notice.loan.id}',
        template_name='payment_notice_received',
        context={'notice': notice, 'user': notice.user, 'loan': notice.loan},
        recipient_list=[notice.user.email],
    )


def send_admin_new_notice_email(notice, admin_emails):
    """Sent to admin(s) when user submits a payment notice"""
    if not admin_emails:
        return
    send_email_async(
        subject=f'🔔 New Payment Notice from {notice.user.username}',
        template_name='admin_new_notice',
        context={'notice': notice, 'user': notice.user, 'loan': notice.loan},
        recipient_list=admin_emails,
    )


def send_payment_approved_email(notice):
    """Sent to user when admin approves their payment"""
    send_email_async(
        subject=f'✅ Payment Approved – Loan #{notice.loan.id}',
        template_name='payment_approved',
        context={
            'notice': notice,
            'user': notice.user,
            'loan': notice.loan,
        },
        recipient_list=[notice.user.email],
    )


def send_payment_rejected_email(notice):
    """Sent to user when admin rejects their payment"""
    send_email_async(
        subject=f'❌ Payment Notice Rejected – Loan #{notice.loan.id}',
        template_name='payment_rejected',
        context={
            'notice': notice,
            'user': notice.user,
            'loan': notice.loan,
            'reason': notice.review_notes,
        },
        recipient_list=[notice.user.email],
    )


def send_loan_completed_email(loan):
    """Sent when loan is fully repaid"""
    send_email_async(
        subject=f'🎊 Congratulations! Loan #{loan.id} Fully Repaid',
        template_name='loan_completed',
        context={'loan': loan, 'user': loan.user},
        recipient_list=[loan.user.email],
    )