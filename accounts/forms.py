from django import forms
from django.contrib.auth.forms import UserChangeForm as DjangoUserChangeForm
from .models import User, UserProfile


class UserProfileForm(DjangoUserChangeForm):
    """Form for editing user profile"""
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'})
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'})
    )
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}))
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'})
    )
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg', 'rows': 3})
    )
    profile_picture = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'w-full'}))
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg', 'type': 'date'})
    )
    gender = forms.ChoiceField(
        required=False,
        choices=[('', 'Select Gender')] + list(User._meta.get_field('gender').choices),
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'})
    )
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg', 'rows': 3})
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone', 'address', 'profile_picture', 'date_of_birth', 'gender', 'bio')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove the password field that comes from DjangoUserChangeForm
        if 'password' in self.fields:
            del self.fields['password']


class UserProfileDetailsForm(forms.ModelForm):
    """Form for editing extended user profile"""
    class Meta:
        model = UserProfile
        fields = ('nip', 'nis', 'employee_id', 'department', 'bio')
        widgets = {
            'nip': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'nis': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'employee_id': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'department': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'bio': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg', 'rows': 3}),
        }
