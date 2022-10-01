from django import forms
from .models import User

class RegisterForm(forms.Form):
    first = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    last = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    phone = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}), required=False)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))
    password_repeat = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))
    
class AuthenticationForm(forms.Form):
    code = forms.IntegerField()

class RecoveryFormEmail(forms.Form):
    email = forms.EmailField()

class RecoveryFormCode(forms.Form):
    code = forms.CharField(widget=forms.TextInput())

class RecoveryFormNewPassword(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))
    new_password_repeat = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))

class UploadForm(forms.Form):
    photo_path = forms.ImageField(label='', required=False)

    def __init__(self, *args, **kwargs):
        super(UploadForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'dropzone dz'

class sharePhotoForm(forms.Form):
    user = forms.CharField(label="",widget=forms.TextInput(attrs={'class':'form-control'}), required=False)

class AccountSettingsForm(forms.Form):
    first = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': ''}), required=False)
    last = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': ''}), required=False)
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control', 'placeholder': ''}), required=False)
    phone = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': ''}), required=False)

class ProfilePictureForm(forms.Form):
    profile_pic = forms.ImageField(required = False)

class PasswordSettingsForm(forms.Form):
    current_password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))
    new_password_repeat = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))

class SettingsAccessForm(forms.Form):
    password = forms.CharField(label="",widget=forms.PasswordInput(attrs={'class':'form-control'}))

class SecuritySettingsForm(forms.Form):
    two_factor_choice = forms.CharField(widget=forms.TextInput(attrs={'class':'switch'}), required=False)

FONT_CHOICES = [
    ('12', '12'),
    ('13', '13'),
    ('14', '14'),
    ('16', '16'),
    ('18', '18'),
    ('20', '20'),
    ('22', '22'),
    ('24', '24'),
    ('26', '26'),
    ('28', '28'),
    ('32', '32'),
]

class userFont(forms.Form):
    font_choice = forms.IntegerField(label="", widget=forms.Select(choices=FONT_CHOICES))
