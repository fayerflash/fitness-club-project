from django import forms
from django.contrib.auth import authenticate
from .models import Membership, Trainer, Promotion, User


class MembershipForm(forms.ModelForm):
    class Meta:
        model = Membership

        fields = [
            'title',
            'description',
            'duration_days',
            'price',
            'visits_limit',
            'is_active',
        ]

        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 4
            }),
        }


class TrainerForm(forms.ModelForm):
    class Meta:
        model = Trainer

        fields = [
            'full_name',
            'specialization',
            'experience_years',
            'bio',
            'is_active',
            'photo',
            'cv_file',
        ]

        widgets = {
            'bio': forms.Textarea(attrs={
                'rows': 5
            }),
        }

    def clean_cv_file(self):
        file = self.cleaned_data.get('cv_file')

        if file:
            if not file.name.endswith('.pdf'):
                raise forms.ValidationError(
                    'Разрешены только PDF файлы'
                )

        return file


class PromotionForm(forms.ModelForm):
    class Meta:
        model = Promotion

        fields = [
            'title',
            'description',
            'discount_percent',
            'start_date',
            'end_date',
            'image',
            'is_active',
            'memberships',
        ]

        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 4
            }),
            'start_date': forms.DateInput(attrs={
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'type': 'date'
            }),
            'memberships': forms.CheckboxSelectMultiple(),
        }


class LoginForm(forms.Form):
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'placeholder': 'Введите email',
            'class': 'form-control'
        })
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Введите пароль',
            'class': 'form-control'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            self.user = authenticate(email=email, password=password)
            if self.user is None:
                raise forms.ValidationError('Неверный email или пароль')
            if not self.user.is_active:
                raise forms.ValidationError('Ваш аккаунт деактивирован')
        return cleaned_data

    def get_user(self):
        return self.user


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Придумайте пароль',
            'class': 'form-control'
        }),
        min_length=6
    )
    password_confirm = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Повторите пароль',
            'class': 'form-control'
        })
    )

    class Meta:
        model = User
        fields = ['full_name', 'email', 'phone', 'password']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'placeholder': 'Ваше полное имя',
                'class': 'form-control'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Ваш email',
                'class': 'form-control'
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': '+7 (XXX) XXX-XX-XX',
                'class': 'form-control'
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('Пароли не совпадают')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.role = 'client'
        if commit:
            user.save()
        return user