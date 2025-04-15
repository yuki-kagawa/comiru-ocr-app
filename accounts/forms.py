from django import forms
from .models import Child
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'username')

User = get_user_model()

class EmailLoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="メールアドレス",
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "メールアドレス"})
    )

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError("このアカウントは無効です。", code='inactive')

class ChildForm(forms.ModelForm):
    class Meta:
        model = Child
        fields = ['name', 'birthday', 'gender', 'juku']
        widgets = {
            'birthday': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'name': '名前',
            'birthday': '誕生日',
            'juku': '塾'
        }