from tkinter import CASCADE
from django.core.validators import MaxValueValidator
from django.db import models

from .cryptography import hash_img_name

def pathCustomForUser(instance, filename):
    return '{0}/{1}'.format(instance.customPath,hash_img_name(str(filename)))

class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    profile_picture = models.ImageField(upload_to = pathCustomForUser, null = True, max_length = 512)
    first = models.CharField(null = False, max_length = 256)
    last = models.CharField(null = False, max_length = 256)
    email = models.EmailField(null = False, unique = True)
    username = models.CharField(null = False, max_length = 256, unique = True)
    phone = models.CharField(null = True, max_length = 256, unique = False)
    password = models.CharField(null = False, max_length = 512, unique = False)
    key_creation_date = models.DateTimeField(null = True)
    join_date = models.DateTimeField(auto_now_add = True)
    storage_size = models.IntegerField(null = False, validators=[MaxValueValidator(3)], default=2)
    token = models.CharField(null=True, max_length=255)

    class Meta:
        db_table = "userTable"

class Authentication(models.Model):
    phone = models.CharField(max_length = 256, unique = True)
    code = models.CharField(max_length = 512)

    class Meta:
        db_table = "authenticationTable"

class AccountRecovery(models.Model):
    email = models.EmailField(unique = True)
    code = models.CharField(max_length = 512)

    class Meta:
        db_table = "recoveryTable"

class UploadModel(models.Model):
    owner = models.ForeignKey(
        User, on_delete = models.CASCADE, null=False, blank=False, default=1
    )
    photo_path = models.ImageField(upload_to = pathCustomForUser, max_length=512)
    labels = models.JSONField(default = dict)
    objects_api = models.JSONField(default = dict)
    properties = models.JSONField(default = dict)
    text_image = models.JSONField(default = dict)
    location = models.JSONField(default = dict)
    datetime = models.CharField(max_length = 512)
    upload_datetime = models.DateTimeField(auto_now_add = True)
    
    class Meta:
        db_table = 'photoTable'

class CategoryModel(models.Model):
    photo = models.ForeignKey(
        UploadModel, on_delete=models.SET_NULL, null=True, blank=True)
    joy = models.IntegerField(default=0)
    sorrow = models.IntegerField(default=0)
    anger = models.IntegerField(default=0)
    surprise = models.IntegerField(default=0)
    blurred = models.IntegerField(default=0)

    class Meta:
        db_table = "categoryTable"

class SharedModel(models.Model):
    photo = models.ForeignKey(
        UploadModel, on_delete=models.SET_NULL, null=True, blank=True)
    owner = models.ForeignKey(
        User, on_delete = models.CASCADE, null=False, blank=False, default=1
    )
    user_id = models.IntegerField(default=0)

    class Meta:
        db_table = "sharedTable"

class UserSettings(models.Model):
    owner = models.ForeignKey(
        User, on_delete = models.CASCADE, null=False, blank=False, default=1
    )
    background_colour = models.CharField(null = False, default = "white", max_length = 256)
    high_contrast_enabled = models.BooleanField(null = False, default = False)
    preferred_font_size = models.IntegerField(default=16)
    text_to_speech = models.BooleanField(null = False, default = False)
    two_factor_enabled = models.BooleanField(null = False, default = False)
    gallery_order_choice = models.CharField(null = False, default = "upload_datetime", max_length = 256)
    emotion_stat_enabled = models.BooleanField(null = False, default = True)
    location_stat_enabled = models.BooleanField(null = False, default = True)

    class Meta:
        db_table = "settingsTable"