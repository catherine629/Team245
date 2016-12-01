from django import forms
from django.forms import ModelForm
from tripPlanner.models import *
from django.contrib.auth.models import User
from django.forms.widgets import HiddenInput

class DateInput(forms.DateInput):
    input_type = 'date'

class TripSettingForm(forms.Form):
    
    start_date = forms.DateField(widget=DateInput(attrs={
                                'placeholder':'start_date',
                                'class': 'form-control'
                                }))
    end_date = forms.DateField(widget=DateInput(attrs={
                                'placeholder':'end_date',
                                'class': 'form-control'
                                }))
    destination = forms.CharField(max_length = 200,
                                  widget=forms.TextInput(attrs={
                                  'placeholder': 'destination',
                                  'class': 'form-control'
                                  }))
    origin = forms.CharField(max_length = 200,
                             widget=forms.TextInput(attrs={
                             'placeholder': 'depart city',
                             'class': 'form-control'
                             }))

    def clean(self):
        cleaned_data = super(TripSettingForm, self).clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        if start_date > end_date:
            raise forms.ValidationError("End date is before start date.")
        diff = end_date - start_date
        if diff.days > 10:
            raise forms.ValidationError("The trip cannot be more than 10 days.")
        return cleaned_data


class RegistrationForm(forms.Form):
    username = forms.CharField(max_length = 200,
                            widget=forms.TextInput(attrs={
                            'placeholder': 'Email',
                            'class': 'form-control'}))
    first_name = forms.CharField(max_length = 200,
                                 widget=forms.TextInput(attrs={
                                 'placeholder': 'First Name',
                                 'class': 'form-control'}))
    last_name = forms.CharField(max_length = 200,
                                widget=forms.TextInput(attrs={
                                'placeholder': 'Last Name',
                                'class': 'form-control'}))
    password1 = forms.CharField(max_length = 200,
                                widget = forms.PasswordInput(attrs={
                                'placeholder': 'Password',
                                'class': 'form-control'}))
    password2 = forms.CharField(max_length = 200,
                                widget = forms.PasswordInput(attrs={
                                'placeholder': 'Confirm Password',
                                'class': 'form-control'}))

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords did not match.")
        return cleaned_data

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__exact=username):
            raise forms.ValidationError("Email is already registered.")
        return username

class AttractionEditForm(ModelForm):
    class Meta:
        model=Attraction
        fields='__all__'
        widgets={
            'name':forms.TextInput(attrs={'placeholder':'Attraction Name'}),
            'address':forms.TextInput(attrs={'placeholder':'Address'}),
            'picture':forms.FileInput(),
            'description':forms.Textarea(attrs={'placeholder':'description'})
        }

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'size': '100px'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ForgetPasswordForm(forms.Form):
    username = forms.CharField(max_length = 200,
                            widget=forms.TextInput(attrs={
                            'placeholder': 'Email',
                            'class': 'form-control'}))
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not User.objects.filter(username__exact=username):
            raise forms.ValidationError("Email has not been registered.")
        return username

class ModifyPasswordForm(forms.Form):
    password1 = forms.CharField(max_length = 200,
                                widget = forms.PasswordInput(attrs={
                                'placeholder': 'New Password',
                                'class': 'form-control'}))
    password2 = forms.CharField(max_length = 200,
                                widget = forms.PasswordInput(attrs={
                                'placeholder': 'Confirm New Password',
                                'class': 'form-control'}))
    def clean(self):
        cleaned_data = super(ModifyPasswordForm, self).clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords did not match.")
        return cleaned_data
