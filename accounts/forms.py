from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, validate_ugandan_nin

class UserRegistrationForm(UserCreationForm):
    """
    Extended registration form with profile fields and document uploads
    """
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=True)
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}), 
        required=True
    )
    national_id = forms.CharField(
        max_length=20, 
        required=True, 
        help_text="Enter your 14-character National ID (e.g., CF92105100HN4G or C123456789012)"
    )
    
    # ===== DOCUMENT UPLOAD FIELDS =====
    profile_picture = forms.ImageField(
        required=False, 
        help_text="Upload a clear photo of yourself (passport size, JPG/PNG)"
    )
    national_id_image = forms.ImageField(
        required=False, 
        help_text="Upload a clear photo of your National ID (front side, JPG/PNG)"
    )
    
    employment_status = forms.ChoiceField(
        choices=UserProfile._meta.get_field('employment_status').choices, 
        required=True
    )
    monthly_income = forms.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        required=True
    )
    employer_name = forms.CharField(
        max_length=200, 
        required=False
    )
        # ===== PAYMENT / DISBURSEMENT FIELDS =====
    mobile_money_number = forms.CharField(
        max_length=15, 
        required=True, 
        help_text="Enter your mobile money number (e.g., 0772 123456)"
    )
    mobile_money_network = forms.ChoiceField(
        choices=UserProfile._meta.get_field('mobile_money_network').choices,
        required=True,
        initial='MTN'
    )
    bank_name = forms.CharField(max_length=100, required=False)
    bank_account_name = forms.CharField(max_length=100, required=False)
    bank_account_number = forms.CharField(max_length=30, required=False)
    preferred_disbursement = forms.ChoiceField(
        choices=UserProfile._meta.get_field('preferred_disbursement').choices,
        required=True,
        initial='MOBILE_MONEY'
    )
    residential_address = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2}), 
        required=True
    )
    city = forms.CharField(
        max_length=100, 
        required=True
    )
    state = forms.CharField(
        max_length=50, 
        required=True
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_national_id(self):
        """Validate Ugandan National ID format"""
        nin = self.cleaned_data.get('national_id')
        if nin:
            nin = nin.strip().upper()
            if not validate_ugandan_nin(nin):
                raise forms.ValidationError(
                    'Invalid National ID format. Must be exactly 14 characters '
                    'containing letters and numbers (e.g., CF92105100HN4G)'
                )
        return nin

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add Bootstrap classes to all fields
        for field_name, field in self.fields.items():
            if field_name in ['residential_address']:
                field.widget.attrs.update({
                    'class': 'form-control form-control-lg',
                    'style': 'border-radius: 12px; border: 1px solid #e2e8f0;',
                    'rows': 2
                })
            elif field_name in ['date_of_birth']:
                field.widget.attrs.update({
                    'class': 'form-control form-control-lg',
                    'style': 'border-radius: 12px; border: 1px solid #e2e8f0;',
                    'type': 'date'
                })
            elif field_name in ['profile_picture', 'national_id_image']:
                field.widget.attrs.update({
                    'class': 'form-control form-control-lg',
                    'style': 'border-radius: 12px; border: 1px solid #e2e8f0;',
                    'accept': 'image/*'
                })
            else:
                field.widget.attrs.update({
                    'class': 'form-control form-control-lg',
                    'style': 'border-radius: 12px; border: 1px solid #e2e8f0;'
                })
        
        # Add help text styling for national_id
        self.fields['national_id'].help_text = (
            'Enter your 14-character National ID (e.g., CF92105100HN4G)'
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            profile = user.profile
            
            # Personal Information
            profile.phone_number = self.cleaned_data['phone_number']
            profile.date_of_birth = self.cleaned_data['date_of_birth']
            profile.national_id = self.cleaned_data['national_id'].strip().upper()
            profile.national_id_verified = False
            
            # Employment
            profile.employment_status = self.cleaned_data['employment_status']
            profile.monthly_income = self.cleaned_data['monthly_income']
            profile.employer_name = self.cleaned_data.get('employer_name', '')
            
            # Address
            profile.residential_address = self.cleaned_data['residential_address']
            profile.city = self.cleaned_data['city']
            profile.state = self.cleaned_data['state']
            
            # ===== SAVE IMAGES =====
            if self.cleaned_data.get('profile_picture'):
                profile.profile_picture = self.cleaned_data['profile_picture']
            if self.cleaned_data.get('national_id_image'):
                profile.national_id_image = self.cleaned_data['national_id_image']
            
            # Calculate credit score
            profile.credit_score = profile.calculate_credit_score()
            profile.save()
            
        return user