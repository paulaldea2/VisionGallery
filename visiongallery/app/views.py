from django.conf import settings
from django.shortcuts import redirect, render
from django.views.generic import *
from django.http import *
from requests import Response
from rest_framework.parsers import MultiPartParser
from rest_framework.decorators import api_view, parser_classes
from rest_framework import viewsets
from rest_framework import permissions

from app.models import *
from app.forms import *

from datetime import datetime
import phonenumbers
import re
import random, string
import os
import shutil
import secrets
import os

from .vision_api import *
from .metadata import *
from .cryptography import *
from .validator import *
from .send_text import *
from .send_email import *
from .serializers import *
from .kMeans import *

#key_store_location = "VisionGalleryKeyStore"
key_store_location = "/mnt/visiongallery_storage/media/" + "VisionGalleryKeyStore"
key_store_password = os.environ["VG_KS_PASSWORD"]

class PhotoViewSet(viewsets.ModelViewSet):
	queryset = UploadModel.objects.all()
	serializer_class = UploadSerializer
	permission_classes = [permissions.IsAuthenticated]

class UserViewSetPublic(viewsets.ModelViewSet):
	queryset = User.objects.all()
	serializer_class = PublicUserSerializer
	permission_classes = []

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

def logged_in(request):

	if "id" in request.session:
		try:
			user = User.objects.get(user_id = request.session['id'])
			return True
		except:
			return False

	return False

def clear_session(request):

	if "auth_id" in request.session:
		del request.session["auth_id"]

	if "authentication" in request.session:
		del request.session["authentication"]

	if "recover_id" in request.session:
		del request.session["recover_id"]

	if "sec_sett_can_access" in request.session:
		del request.session["sec_sett_can_access"]

def privacy(request):
	tts = True

	if not logged_in(request):
		clear_session(request)
		return render(request, 'app/privacy.html', locals())

	clear_session(request)
	tts= True

	currentUser = User.objects.get(user_id=request.session["id"])
	user_settings = UserSettings.objects.get(owner_id = currentUser.user_id)

	userFontSizeText = user_settings.preferred_font_size
	userFontSizeHeading1 = (int(user_settings.preferred_font_size)*2)
	userFontSizeHeading2 = (int(user_settings.preferred_font_size) + ((int(user_settings.preferred_font_size)) /2))
	userFontSizeHeading3 = (int(user_settings.preferred_font_size) + ((int(user_settings.preferred_font_size)) /3))
	tts = user_settings.text_to_speech
	theme = user_settings.background_colour

	return render(request, 'app/postLoginPrivacy.html', locals())

def strong_password_guide(request):
	
	if not logged_in(request):
		return render(request, 'app/passwordGuide.html')

	clear_session(request)
	tts = True

	currentUser = User.objects.get(user_id=request.session["id"])
	user_settings = UserSettings.objects.get(owner_id = currentUser.user_id)

	userFontSizeText = user_settings.preferred_font_size
	userFontSizeHeading1 = (int(user_settings.preferred_font_size)*2)
	userFontSizeHeading2 = (int(user_settings.preferred_font_size) + ((int(user_settings.preferred_font_size)) /2))
	userFontSizeHeading3 = (int(user_settings.preferred_font_size) + ((int(user_settings.preferred_font_size)) /3))
	tts = user_settings.text_to_speech
	theme = user_settings.background_colour

	return render(request, 'app/postLoginPasswordGuide.html', locals())

def main(request):

	if logged_in(request):
		return redirect("/home")

	clear_session(request)

	return render(request, 'app/main.html', locals())

def redirectToMain(request):
	return redirect('/main')

def login(request):

	if logged_in(request):
		return redirect("/home")

	clear_session(request)
	tts = True

	login = LoginForm(request.GET)

	if request.method == "GET":
		if login.is_valid():
			username_input = request.GET['username']
			username_valid = valid_username(username_input)	

			if not username_valid:
				temp = locals()
				temp.update({ 'error_message': 'Not a valid username.' })
				return render(request, "app/login.html", temp)

			try:
				user = User.objects.get(username = username_input)
			except:
				temp = locals()
				temp.update({ 'error_message': 'User does not exist. Please check your credentials or sign up now.'})
				return render(request, "app/login.html", temp)

			password_input = request.GET['password']
			password_format_valid = valid_password(password_input)

			if not password_format_valid:
				temp = locals()
				temp.update({ 'error_message': 'Not a valid password.' })
				return render(request, "app/login.html", temp)

			db_password = user.password
			password_valid = validate(password_input, db_password)

			if password_valid:
				user_settings = UserSettings.objects.get(owner_id = user.user_id)
				
				if user_settings.two_factor_enabled:
					out = { 'auth_id' : user.user_id, 'authentication': True }
					request.session.update(out)

					return redirect("/authenticate")
				else:
					out = { 'id' : user.user_id }
					request.session.update(out)

					user_key = get_key(key_store_location, username_input, key_store_password, key_store_password)
					user_dir = str(settings.MEDIA_ROOT) + "/" + username_input

					decrypt_dir(user_dir, user_key)

					creation_date = user.key_creation_date
					creation_date = creation_date.replace(tzinfo=None)
					date_today = datetime.now()
					difference = date_today - creation_date
					diff_in_s = difference.total_seconds()

					if diff_in_s >= 604800:
						if change_key(key_store_location, username_input, key_store_password):
							new_key_date = datetime.now()
							user.key_creation_date = new_key_date
							user.save()

					return redirect("/home")
			else:
				temp = locals()
				temp.update({'error_message': 'Password is incorrect. Please enter the correct password.'})
				return render(request, "app/login.html", temp)
		else:
			login = LoginForm()

	return render(request, 'app/login.html', locals())

def authenticate(request):

	if logged_in(request):
		return redirect("/home")
	
	if not "auth_id" in request.session:
		return redirect("/login")

	try:
		user = User.objects.get(user_id=request.session["auth_id"])
	except:
		del request.session["auth_id"]
		del request.session["authentication"]
		return redirect("/login")
		
	authentication_code = 1

	try:
		phone = user.phone
	except:
		temp = locals()
		temp.update({'error_message': 'No phone number exists for 2FA.'})
		del request.session["auth_id"]
		del request.session["authentication"]
		return render(request, "app/authentication.html", temp)

	to_display_number = crop_phone_number(phone)

	if request.session["authentication"]:
		try:
			authentication_code = generate_authentication_code(phone)
		except Exception as e:
			e = str(e)
			if "Duplicate" in e:
				auth_obj = Authentication.objects.get(phone = phone)
				auth_obj.delete()
				authentication_code = generate_authentication_code(phone)
			else:
				temp = locals()
				temp.update({'error_message': "There's been an error while generating the authentication code."})
				del request.session["auth_id"]
				del request.session["authentication"]
				return render(request, "app/authentication.html", temp)

	authentication_form = AuthenticationForm()

	if authentication_code:
		auth_obj = Authentication.objects.get(phone = phone)
		request.session.update({"authentication" : False})

		try:
			send_authentication_code(phone, authentication_code)
		except:
			temp = locals()
			temp.update({'error_message': "There's been an error while sending the text message."})
			auth_obj.delete()
			del request.session["auth_id"]
			del request.session["authentication"]
			return render(request, "app/authentication.html", temp)
		
		authentication_form = AuthenticationForm(request.GET)
		
		username_input = user.username

		if request.method == "GET":
			if authentication_form.is_valid():
				code_input = request.GET['code']
				db_code = auth_obj.code
				code_valid = validate(code_input, db_code)

				if code_valid:
					auth_obj.delete()

					user_key = get_key(key_store_location, username_input, key_store_password, key_store_password)
					user_dir = str(settings.MEDIA_ROOT) + "/" + username_input

					decrypt_dir(user_dir, user_key)

					creation_date = user.key_creation_date
					creation_date = creation_date.replace(tzinfo=None)
					date_today = datetime.now()
					difference = date_today - creation_date
					diff_in_s = difference.total_seconds()

					if diff_in_s >= 604800:
						if change_key(key_store_location, username_input, key_store_password):
							new_key_date = datetime.now()
							user.key_creation_date = new_key_date
							user.save()

					out = { 'id' : user.user_id }
					request.session.update(out)

					del request.session["auth_id"]
					del request.session["authentication"]
					return redirect("/home")
				else:
					temp = locals()
					temp.update({'error_message': "Not a valid code. Please try again later."})
					auth_obj.delete()
					del request.session["auth_id"]
					del request.session["authentication"]	
					return render(request, "app/authentication.html", temp)
			else:
				authentication_form = AuthenticationForm()

	return render(request, "app/authentication.html", locals())

def register(request):
	
	if logged_in(request):
		return redirect("/home")

	clear_session(request)
	tts = True

	regist = RegisterForm(request.GET)
	
	if request.method == "GET":
		if regist.is_valid():
			user = User()

			user.first = request.GET['first']
			first = valid_name(user.first)

			if not first:
				temp = locals()
				temp.update({ 'error_message': 'Not a valid first name.' })
				return render(request, "app/register.html", temp)
			
			user.first = first

			user.last = request.GET['last']
			last = valid_name(user.last)

			if not last:
				temp = locals()
				temp.update({ 'error_message': 'Not a valid last name.' })
				return render(request, "app/register.html", temp)
			
			user.last = last

			user.email = request.GET['email']
			email_valid = valid_email(user.email)

			if not email_valid:
				temp = locals()
				temp.update({ 'error_message': 'Not a valid e-mail address.' })
				return render(request, "app/register.html", temp)
			
			if User.objects.filter(email=request.GET['email']):
				temp = locals()
				temp.update({ 'error_message': 'E-mail already exists.' })
				return render(request, "app/register.html", temp)
	
			user.username = request.GET['username']
			username_valid = valid_username(user.username)

			if not username_valid:
				temp = locals()
				temp.update({ 'error_message': 'Not a valid username.' })
				return render(request, "app/register.html", temp)

			if User.objects.filter(username=request.GET['username']):
				temp = locals()
				temp.update({ 'error_message': 'Username already exists.' })
				return render(request, "app/register.html", temp)

			if request.GET['phone'] != "":
				user.phone = request.GET['phone']
				phone_valid = valid_phone(user.phone)

				if not phone_valid:
					temp = locals()
					temp.update({ 'error_message': 'Not a valid phone number.' })
					return render(request, "app/register.html", temp)
				
				if User.objects.filter(phone=request.GET['phone']):
					temp = locals()
					temp.update({ 'error_message': 'Phone number already exists.' })
					return render(request, "app/register.html", temp)
			else:
				user.phone = ""

			password = request.GET['password']
			password_repeat = request.GET['password_repeat']

			password_valid = valid_password(password)

			if not password_valid:
				temp = locals()
				temp.update({ 'error_message': 'Not a valid password.' })
				return render(request, "app/register.html", temp)

			pass_strength = calc_password_str(password)

			if pass_strength != "Strong":
				temp = locals()
				temp.update({ 'error_message': 'Not a strong password.' })
				return render(request, "app/register.html", temp)

			if(password != password_repeat):
				temp = locals()
				temp.update({'error_message': "Passwords do not match."})
				return render(request, "app/register.html", temp)

			secure_pass = enc_password(password)
			user.password = str(secure_pass)
			
			user.save()

			user_setting = UserSettings()
			user_setting.owner_id = user.user_id
			user_setting.save()

			if not key_exists(key_store_location, user.username, key_store_password):
				generate_key(key_store_location, user.username, key_store_password)
				current_date = datetime.now()
				user.key_creation_date = current_date
				user.save()

			out = { 'id' : user.user_id }
			request.session.update(out)

			return redirect("/home")
		else:
			regist = RegisterForm()

	return render(request, 'app/register.html', locals())

def recover_first(request):

	if logged_in(request):
		return redirect("/home")

	recovery_email = RecoveryFormEmail(request.GET)
	tts = True

	if request.method == "GET":
		if recovery_email.is_valid():
			email = request.GET['email']
			email_format_valid = valid_email(email)

			if not email_format_valid:
				temp = locals()
				temp.update({'error_message': "Not a valid e-mail address."})
				return render(request, "app/forgetPasswordOne.html", temp)

			try:
				user = User.objects.get(email = email)
			except:
				temp = locals()
				temp.update({'error_message': "Not an existing e-mail address."})
				return render(request, "app/forgetPasswordOne.html", temp)

			try:
				recovery_code = generate_recovery_code(email)
			except Exception as e:
				e = str(e)
				if "Duplicate" in e:
					recovery_obj = AccountRecovery.objects.get(email = email)
					recovery_obj.delete()
					recovery_code = generate_recovery_code(email)
				else:
					temp = locals()
					temp.update({'error_message': "There's been an error while generating the recovery code."})
					return render(request, "app/forgetPasswordOne.html", temp)

			if recovery_code:
				recovery_obj = AccountRecovery.objects.get(email = email)

				out = { 'recover_id' : recovery_obj.id }
				request.session.update(out)

				try:
					name = user.first
					send_recovery_code(email, name, recovery_code)
				except:
					temp = locals()
					temp.update({'error_message': "There's been an error while sending the e-mail."})
					recovery_obj.delete()
					del request.session["recover_id"]
					return render(request, "app/forgetPasswordOne.html", temp)

				return redirect('/recover_account/step_2')
		else:
			recovery_email = RecoveryFormEmail()

	return render(request, 'app/forgetPasswordOne.html', locals())

def recover_second(request):
	
	if logged_in(request):
		return redirect("/home")
	
	tts = True

	recovery_code = RecoveryFormCode(request.GET)

	recovery_obj = AccountRecovery.objects.get(id = request.session["recover_id"])

	if request.method == "GET":
		if recovery_code.is_valid():
			code = request.GET['code']
			code_format_valid = valid_recovery_code(code)

			if not code_format_valid:
				temp = locals()
				temp.update({'error_message': "Not a valid recovery code."})
				recovery_obj.delete()
				del request.session["recover_id"]
				return render(request, "app/forgetPasswordTwo.html", temp)

			db_code = recovery_obj.code
			code_valid = validate(code, db_code)

			if code_valid:
				return redirect('/recover_account/step_3')
			else:
				temp = locals()
				temp.update({'error_message': "Recovery code does not exists. Please try again later."})
				recovery_obj.delete()
				del request.session["recover_id"]
				return render(request, "app/forgetPasswordTwo.html", temp)
		else:
			recovery_code = RecoveryFormCode()

	return render(request, 'app/forgetPasswordTwo.html', locals())

def recover_third(request):

	if logged_in(request):
		return redirect("/home")

	tts = True
	recovery_password = RecoveryFormNewPassword(request.GET)

	recovery_obj = AccountRecovery.objects.get(id = request.session["recover_id"])

	if request.method == "GET":
		if recovery_password.is_valid():
			password = request.GET['new_password']
			password_repeat = request.GET['new_password_repeat']

			password_valid = valid_password(password)

			if not password_valid:
				temp = locals()
				temp.update({ 'error_message': 'Not a valid password.' })
				return render(request, "app/forgetPasswordThree.html", temp)

			pass_strength = calc_password_str(password)

			if pass_strength != "Strong":
				temp = locals()
				temp.update({ 'error_message': 'Not a strong password.' })
				return render(request, "app/forgetPasswordThree.html", temp)

			if(password != password_repeat):
				temp = locals()
				temp.update({'error_message': "Passwords do not match."})
				return render(request, "app/forgetPasswordThree.html", temp)

			secure_pass = enc_password(password)
			
			user = User.objects.get(email = recovery_obj.email)
			user.password = str(secure_pass)

			recovery_obj.delete()
			user.save()

			del request.session["recover_id"]
			return redirect('/login')
		else:
			recovery_password = RecoveryFormNewPassword()

	return render(request, 'app/forgetPasswordThree.html', locals())

def logout(request):

	if not logged_in(request):
		return redirect("/main")

	clear_session(request)

	session_id = request.session["id"]
	user = User.objects.get(user_id = session_id)
	username = user.username

	user_key = get_key(key_store_location, username, key_store_password, key_store_password)
	user_dir = str(settings.MEDIA_ROOT) + "/" + username

	encrypt_dir(user_dir, user_key)

	del request.session["id"]

	return redirect("/main")

def home(request):

	if not logged_in(request):
		return redirect("/login")

	clear_session(request)

	currentUser = User.objects.get(user_id=request.session["id"])
	user_settings = UserSettings.objects.get(owner_id = currentUser.user_id)

	userFontSizeText = user_settings.preferred_font_size
	userFontSizeHeading1 = (int(user_settings.preferred_font_size)*2)
	userFontSizeHeading2 = (int(user_settings.preferred_font_size) + ((int(user_settings.preferred_font_size)) /2))
	userFontSizeHeading3 = (int(user_settings.preferred_font_size) + ((int(user_settings.preferred_font_size)) /3))
	tts = user_settings.text_to_speech
	theme = user_settings.background_colour

	all_photos = UploadModel.objects.filter(owner_id=request.session["id"]).order_by('upload_datetime').reverse()[0:10]
	shared_photos = SharedModel.objects.filter(user_id = request.session["id"])

	shared = []
	for photo in shared_photos:
		owner = User.objects.get(user_id = photo.owner_id)
		owner_username = owner.username

		get_shared = UploadModel.objects.filter(id = photo.photo_id)

		for photo in get_shared:
			path = str(settings.MEDIA_ROOT) + "/" + str(photo.photo_path) + ".enc"
			
			shared.append(photo)

			if os.path.exists(path):
				key = get_key(key_store_location, owner_username, key_store_password, key_store_password)
				decrypt_file(path, key)

	emotion_stat_enabled = user_settings.emotion_stat_enabled
	location_stat_enabled = user_settings.location_stat_enabled

	if emotion_stat_enabled:
		emotions = ["Joy", "Sorrow", "Anger", "Surprise", "Blurred"]
		emotionValues = []
		emotion_all = get_number_of_emot_img(request)

		joy_num = get_number_of_joy_img(request)
		sorrow_num = get_number_of_sorr_img(request)
		anger_num = get_number_of_angr_img(request)
		surprise_num = get_number_of_surp_img(request)
		blurred_num = get_number_of_blur_img(request)

		if emotion_all != 0:
			joy_percentage = (joy_num/emotion_all)*100
			sorrow_percentage = (sorrow_num/emotion_all)*100
			anger_percentage = (anger_num/emotion_all)*100
			surprise_percentage = (surprise_num/emotion_all)*100
			blurred_percentage = (blurred_num/emotion_all)*100
			emotionValues = [joy_percentage, sorrow_percentage, anger_percentage, surprise_percentage, blurred_percentage]
		else:
			joy_percentage = 0
			sorrow_percentage = 0
			anger_percentage = 0
			surprise_percentage = 0
			blurred_percentage = 0

	if location_stat_enabled:
		location_all = get_number_of_loc_img(request)

		locs = get_location_info(request)

		location_stat = {}
		for loc in locs:
			count = locs.count(loc)
			percentage = (count/location_all)*100

			location_stat[str(loc[0])] = percentage

	return render(request, 'app/home.html', locals())

def UploadPhotoView(request):

	if not logged_in(request):
		return redirect("/login")

	clear_session(request)

	saved = False
	uploadFailed = False

	currentUser = User.objects.get(user_id=request.session["id"])
	user_settings = UserSettings.objects.get(owner_id = currentUser.user_id)

	userFontSizeText = user_settings.preferred_font_size
	userFontSizeHeading1 = (int(user_settings.preferred_font_size)*2)
	userFontSizeHeading2 = (int(user_settings.preferred_font_size) + ((int(user_settings.preferred_font_size)) /2))
	userFontSizeHeading3 = (int(user_settings.preferred_font_size) + ((int(user_settings.preferred_font_size)) /3))
	tts = user_settings.text_to_speech
	theme = user_settings.background_colour
	
	MyUploadForm = UploadForm(request.POST, request.FILES,)

	if request.method == "POST":
		if MyUploadForm.is_valid():
			object = UploadModel()
			object.customPath = currentUser.username
			photo_path = MyUploadForm.cleaned_data["photo_path"]
			object.photo_path = photo_path 
			object.save()

			full_photo_path = str(settings.MEDIA_ROOT) + "/" + str(object.photo_path)
			full_photo_path = full_photo_path.replace("\\", "/")

			object.owner = currentUser

			object.labels = get_labels_API(full_photo_path)
			object.objects_api = get_objects_API(full_photo_path)
			object.properties = get_properties_API(full_photo_path)
			props = object.properties['Properties']
			object.text_image = get_text_image(full_photo_path)
			
			object.location = merge_location(full_photo_path)

			if object.location == []:
				object.location = get_location_API(full_photo_path)

			object.datetime = get_datetime_data(full_photo_path)

			remove_data(full_photo_path)

			userPhotos = UploadModel.objects.filter(owner_id=request.session["id"])
			totalUsed = getAllSize(userPhotos)

			if totalUsed + getImageGB(object.photo_path) < currentUser.storage_size: 
				object.save()
				categories = CategoryModel()
				emotes = get_emotion_API(full_photo_path)
				categories.photo_id = object.id

				if "Joy" in emotes:
					categories.joy = emotes["Joy"]
				if "Sorrow" in emotes:
					categories.sorrow = emotes["Sorrow"]
				if "Anger" in emotes:
					categories.anger = emotes["Anger"]
				if "Surprise" in emotes:
					categories.surprise = emotes["Surprise"]
				if "Blurred" in emotes:
					categories.blurred = emotes["Blurred"]

				categories.save()
				saved = True
				uploadFailed = False
			else:
				MyUploadForm = UploadForm()
				uploadFailed = True
				saved = False
		else:
			MyUploadForm = UploadForm()
		
	return render(request, 'app/upload.html', locals())

def GalleryView(request):

	if not logged_in(request):
		return redirect("/login")
	
	clear_session(request)

	albumRequest = request.GET.get('album')
	
	currentUser = User.objects.get(user_id=request.session["id"])
	user_settings = UserSettings.objects.get(owner_id = currentUser.user_id)

	userFontSizeText = user_settings.preferred_font_size
	userFontSizeHeading1 = (int(user_settings.preferred_font_size)*2)
	userFontSizeHeading2 = (int(user_settings.preferred_font_size) + ((int(user_settings.preferred_font_size)) /2))
	userFontSizeHeading3 = (int(user_settings.preferred_font_size) + ((int(user_settings.preferred_font_size)) /3))
	tts = user_settings.text_to_speech
	theme = user_settings.background_colour

	username = currentUser.username

	#colourOptions = {0:blackPhotos, 1:whitePhotos, 2:redPhotos, 3:limePhotos, 4:bluePhotos, 5:yellowPhotos, 6:cyanPhotos, 7:magentaPhotos, 8:silverPhotos, 9:grayPhotos, 10:maroonPhotos, 11:olivePhotos, 12:greenPhotos, 13:purplePhotos, 14:tealPhotos, 15:navyPhotos,}
	colourSortedPhotos = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
	clusterRGBs = []
	
	all_photos = UploadModel.objects.filter(owner_id=currentUser.user_id).order_by(user_settings.gallery_order_choice).reverse()
	photoRGBs = []
	phColors = []
	colors = [ "color0", "color1", "color2", "color3", "color4", "color5", "color6", "color7", "color8", "color9"]
	albumHasPic = [["Anger", False], ["Blurred", False], ["Joy", False], ["Sorrow", False], ["Surprise", False]]
	emotionDeteted = False

	for i in range(len(all_photos)):
		curPhoto = all_photos[i]
		curID = int(curPhoto.id)
		curRGB = curPhoto.properties["Properties"]
		photoRGBs.append([curID, curRGB[0], curRGB[1], curRGB[2]])
		
	
	print(phColors)
	# read in cluster data
	clusters = readDataIn("static/colours.txt")

	clusterData = directKMeans(photoRGBs, clusters, True, True)
	#clusterData format: [[photo1ID, photo2ID], [photo3ID, photo4ID]]

	print("k-means complete")

	for i in range(len(clusterData)):
		curClusterData = clusterData[i]
		curClusterID = i
		clusterRGBs.append([curClusterData[0], curClusterData[1], curClusterData[2]])
		if (len(curClusterData) > 3):
			phColors.append(["rgb(" + str(curClusterData[0]) + "," + str(curClusterData[1]) + "," + str(curClusterData[2]) + ")", colors[i]] )
		
		for j in range(3, len(curClusterData)):
			curPhotoID = curClusterData[j]
			colourSortedPhotos[curClusterID].append(curPhotoID)


	all_photos = []
	for i in range(len(colourSortedPhotos)):
		if (albumRequest == ("colour" + str(i))):
			clusterRGB = clusterRGBs[i]
			all_photos = []
			for ident in colourSortedPhotos[i]:
				all_photos.append(UploadModel.objects.get(owner_id=request.session["id"], id=ident))

	if albumRequest == None:
		all_photos = UploadModel.objects.filter(owner_id=currentUser.user_id).order_by(user_settings.gallery_order_choice).reverse()
		test_pic = []

		for pic in all_photos:
			category = CategoryModel.objects.get(photo_id=pic.id)
			test_pic.append(category)

		for img in test_pic:
			if (img.joy >= 2):
				albumHasPic[2][1] = True
				emotionDeteted = True
			
			if (img.anger >= 2):
				albumHasPic[0][1] = True
				emotionDeteted = True

			if (img.sorrow >= 2):
				albumHasPic[3][1] = True
				emotionDeteted = True

			if (img.blurred >= 2):
				albumHasPic[1][1] = True
				emotionDeteted = True

			if (img.surprise >= 2):
				albumHasPic[4][1] = True
				emotionDeteted = True
	
	elif albumRequest == "Joy":
		user_pics = UploadModel.objects.filter(owner_id=currentUser.user_id).order_by(user_settings.gallery_order_choice).reverse()
		joy_pics = []
		all_photos = []

		for pic in user_pics:
			category = CategoryModel.objects.get(photo_id=pic.id)
			joy_pics.append(category)

		for i in joy_pics:
			if i.joy >= 2:
				all_photos.append(UploadModel.objects.get(id =i.photo_id))
			
			if (i.anger >= 2):
				albumHasPic[0][1] = True
				emotionDeteted = True

			if (i.sorrow >= 2):
				albumHasPic[3][1] = True
				emotionDeteted = True

			if (i.blurred >= 2):
				albumHasPic[1][1] = True
				emotionDeteted = True

			if (i.surprise >= 2):
				albumHasPic[4][1] = True
				emotionDeteted = True

		if len(all_photos) != 0:
			albumHasPic[2][1] = True
			emotionDeteted = True
			
	elif albumRequest == "Anger":
		user_pics = UploadModel.objects.filter(owner_id=currentUser.user_id).order_by(user_settings.gallery_order_choice).reverse()
		cat_pics = []
		all_photos = []

		for pic in user_pics:
			category = CategoryModel.objects.get(photo_id=pic.id)
			cat_pics.append(category)
			
		for i in cat_pics:
			if i.anger >= 2:
				all_photos.append(UploadModel.objects.get(id =i.photo_id))

			if (i.joy >= 2):
				albumHasPic[2][1] = True
				emotionDeteted = True

			if (i.sorrow >= 2):
				albumHasPic[3][1] = True
				emotionDeteted = True

			if (i.blurred >= 2):
				albumHasPic[1][1] = True
				emotionDeteted = True

			if (i.surprise >= 2):
				albumHasPic[4][1] = True
				emotionDeteted = True

		if len(all_photos) != 0:
			albumHasPic[0][1] = True
			emotionDeteted = True
	
	elif albumRequest == "Blurred":
		user_pics = UploadModel.objects.filter(owner_id=currentUser.user_id).order_by(user_settings.gallery_order_choice).reverse()
		cat_pics = []
		all_photos = []

		for pic in user_pics:
			category = CategoryModel.objects.get(photo_id=pic.id)
			cat_pics.append(category)
			
		for i in cat_pics:
			if i.blurred >= 2:
				all_photos.append(UploadModel.objects.get(id =i.photo_id))
			
			if (i.anger >= 2):
				albumHasPic[0][1] = True
				emotionDeteted = True

			if (i.sorrow >= 2):
				albumHasPic[3][1] = True
				emotionDeteted = True

			if (i.joy >= 2):
				albumHasPic[2][1] = True
				emotionDeteted = True

			if (i.surprise >= 2):
				albumHasPic[4][1] = True
				emotionDeteted = True

		if len(all_photos) != 0:
			albumHasPic[1][1] = True
			emotionDeteted = True

	elif albumRequest == "Sorrow":
		user_pics = UploadModel.objects.filter(owner_id=currentUser.user_id).order_by(user_settings.gallery_order_choice).reverse()
		cat_pics = []
		all_photos = []

		for pic in user_pics:
			category = CategoryModel.objects.get(photo_id=pic.id)
			cat_pics.append(category)
			
		for i in cat_pics:
			if i.sorrow >= 2:
				all_photos.append(UploadModel.objects.get(id =i.photo_id))
			
			if (i.anger >= 2):
				albumHasPic[0][1] = True
				emotionDeteted = True

			if (i.joy >= 2):
				albumHasPic[2][1] = True
				emotionDeteted = True

			if (i.blurred >= 2):
				albumHasPic[1][1] = True
				emotionDeteted = True

			if (i.surprise >= 2):
				albumHasPic[4][1] = True
				emotionDeteted = True
				print(albumHasPic)
		
		if len(all_photos) != 0:
			albumHasPic[3][1] = True
			emotionDeteted = True
	
	elif albumRequest == "Surprise":
		user_pics = UploadModel.objects.filter(owner_id=currentUser.user_id).order_by(user_settings.gallery_order_choice).reverse()
		cat_pics = []
		all_photos = []

		for pic in user_pics:
			category = CategoryModel.objects.get(photo_id=pic.id)
			cat_pics.append(category)
			
		for i in cat_pics:
			if i.surprise >= 2:
				all_photos.append(UploadModel.objects.get(id =i.photo_id))
			
			if (i.anger >= 2):
				albumHasPic[0][1] = True
				emotionDeteted = True

			if (i.sorrow >= 2):
				albumHasPic[3][1] = True
				emotionDeteted = True

			if (i.blurred >= 2):
				albumHasPic[1][1] = True
				emotionDeteted = True

			if (i.joy >= 2):
				albumHasPic[2][1] = True
				emotionDeteted = True
		
		if len(all_photos) != 0:
			albumHasPic[4][1] = True
			emotionDeteted = True

	elif albumRequest == "color0":
		all_photos = UploadModel.objects.filter(owner_id=currentUser.user_id).order_by(user_settings.gallery_order_choice).reverse()
		test_pic = []

		for pic in all_photos:
			category = CategoryModel.objects.get(photo_id=pic.id)
			test_pic.append(category)

		for img in test_pic:
			if (img.joy >= 2):
				albumHasPic[2][1] = True
				emotionDeteted = True
			
			if (img.anger >= 2):
				albumHasPic[0][1] = True
				emotionDeteted = True

			if (img.sorrow >= 2):
				albumHasPic[3][1] = True
				emotionDeteted = True

			if (img.blurred >= 2):
				albumHasPic[1][1] = True
				emotionDeteted = True

			if (img.surprise >= 2):
				albumHasPic[4][1] = True
				emotionDeteted = True
		all_photos = []
		
		for ident in colourSortedPhotos[0]:
			all_photos.append(UploadModel.objects.get(owner_id=request.session["id"], id=ident))
	
	elif albumRequest == "color1":
		all_photos = UploadModel.objects.filter(owner_id=currentUser.user_id).order_by(user_settings.gallery_order_choice).reverse()
		test_pic = []

		for pic in all_photos:
			category = CategoryModel.objects.get(photo_id=pic.id)
			test_pic.append(category)

		for img in test_pic:
			if (img.joy >= 2):
				albumHasPic[2][1] = True
				emotionDeteted = True
			
			if (img.anger >= 2):
				albumHasPic[0][1] = True
				emotionDeteted = True

			if (img.sorrow >= 2):
				albumHasPic[3][1] = True
				emotionDeteted = True

			if (img.blurred >= 2):
				albumHasPic[1][1] = True
				emotionDeteted = True

			if (img.surprise >= 2):
				albumHasPic[4][1] = True
				emotionDeteted = True
		all_photos = []
		
		for ident in colourSortedPhotos[1]:
			all_photos.append(UploadModel.objects.get(owner_id=request.session["id"], id=ident))
	
	elif albumRequest == "color2":
		all_photos = UploadModel.objects.filter(owner_id=currentUser.user_id).order_by(user_settings.gallery_order_choice).reverse()
		test_pic = []

		for pic in all_photos:
			category = CategoryModel.objects.get(photo_id=pic.id)
			test_pic.append(category)

		for img in test_pic:
			if (img.joy >= 2):
				albumHasPic[2][1] = True
				emotionDeteted = True
			
			if (img.anger >= 2):
				albumHasPic[0][1] = True
				emotionDeteted = True

			if (img.sorrow >= 2):
				albumHasPic[3][1] = True
				emotionDeteted = True

			if (img.blurred >= 2):
				albumHasPic[1][1] = True
				emotionDeteted = True

			if (img.surprise >= 2):
				albumHasPic[4][1] = True
				emotionDeteted = True
		all_photos = []
		
		for ident in colourSortedPhotos[2]:
			all_photos.append(UploadModel.objects.get(owner_id=request.session["id"], id=ident))
	
	elif albumRequest == "color3":
		all_photos = UploadModel.objects.filter(owner_id=currentUser.user_id).order_by(user_settings.gallery_order_choice).reverse()
		test_pic = []

		for pic in all_photos:
			category = CategoryModel.objects.get(photo_id=pic.id)
			test_pic.append(category)

		for img in test_pic:
			if (img.joy >= 2):
				albumHasPic[2][1] = True
				emotionDeteted = True
			
			if (img.anger >= 2):
				albumHasPic[0][1] = True
				emotionDeteted = True

			if (img.sorrow >= 2):
				albumHasPic[3][1] = True
				emotionDeteted = True

			if (img.blurred >= 2):
				albumHasPic[1][1] = True
				emotionDeteted = True

			if (img.surprise >= 2):
				albumHasPic[4][1] = True
				emotionDeteted = True
		all_photos = []
		
		for ident in colourSortedPhotos[3]:
			all_photos.append(UploadModel.objects.get(owner_id=request.session["id"], id=ident))
	
	elif albumRequest == "color4":
		all_photos = UploadModel.objects.filter(owner_id=currentUser.user_id).order_by(user_settings.gallery_order_choice).reverse()
		test_pic = []

		for pic in all_photos:
			category = CategoryModel.objects.get(photo_id=pic.id)
			test_pic.append(category)

		for img in test_pic:
			if (img.joy >= 2):
				albumHasPic[2][1] = True
				emotionDeteted = True
			
			if (img.anger >= 2):
				albumHasPic[0][1] = True
				emotionDeteted = True

			if (img.sorrow >= 2):
				albumHasPic[3][1] = True
				emotionDeteted = True

			if (img.blurred >= 2):
				albumHasPic[1][1] = True
				emotionDeteted = True

			if (img.surprise >= 2):
				albumHasPic[4][1] = True
				emotionDeteted = True
		all_photos = []
		
		for ident in colourSortedPhotos[4]:
			all_photos.append(UploadModel.objects.get(owner_id=request.session["id"], id=ident))
	
	elif albumRequest == "color5":
		all_photos = UploadModel.objects.filter(owner_id=currentUser.user_id).order_by(user_settings.gallery_order_choice).reverse()
		test_pic = []

		for pic in all_photos:
			category = CategoryModel.objects.get(photo_id=pic.id)
			test_pic.append(category)

		for img in test_pic:
			if (img.joy >= 2):
				albumHasPic[2][1] = True
				emotionDeteted = True
			
			if (img.anger >= 2):
				albumHasPic[0][1] = True
				emotionDeteted = True

			if (img.sorrow >= 2):
				albumHasPic[3][1] = True
				emotionDeteted = True

			if (img.blurred >= 2):
				albumHasPic[1][1] = True
				emotionDeteted = True

			if (img.surprise >= 2):
				albumHasPic[4][1] = True
				emotionDeteted = True
		all_photos = []
		
		for ident in colourSortedPhotos[5]:
			all_photos.append(UploadModel.objects.get(owner_id=request.session["id"], id=ident))
	
	elif albumRequest == "color6":
		all_photos = UploadModel.objects.filter(owner_id=currentUser.user_id).order_by(user_settings.gallery_order_choice).reverse()
		test_pic = []

		for pic in all_photos:
			category = CategoryModel.objects.get(photo_id=pic.id)
			test_pic.append(category)

		for img in test_pic:
			if (img.joy >= 2):
				albumHasPic[2][1] = True
				emotionDeteted = True
			
			if (img.anger >= 2):
				albumHasPic[0][1] = True
				emotionDeteted = True

			if (img.sorrow >= 2):
				albumHasPic[3][1] = True
				emotionDeteted = True

			if (img.blurred >= 2):
				albumHasPic[1][1] = True
				emotionDeteted = True

			if (img.surprise >= 2):
				albumHasPic[4][1] = True
				emotionDeteted = True
		all_photos = []
		
		for ident in colourSortedPhotos[6]:
			all_photos.append(UploadModel.objects.get(owner_id=request.session["id"], id=ident))
	
	elif albumRequest == "color7":
		all_photos = UploadModel.objects.filter(owner_id=currentUser.user_id).order_by(user_settings.gallery_order_choice).reverse()
		test_pic = []

		for pic in all_photos:
			category = CategoryModel.objects.get(photo_id=pic.id)
			test_pic.append(category)

		for img in test_pic:
			if (img.joy >= 2):
				albumHasPic[2][1] = True
				emotionDeteted = True
			
			if (img.anger >= 2):
				albumHasPic[0][1] = True
				emotionDeteted = True

			if (img.sorrow >= 2):
				albumHasPic[3][1] = True
				emotionDeteted = True

			if (img.blurred >= 2):
				albumHasPic[1][1] = True
				emotionDeteted = True

			if (img.surprise >= 2):
				albumHasPic[4][1] = True
				emotionDeteted = True
		all_photos = []
		
		for ident in colourSortedPhotos[7]:
			all_photos.append(UploadModel.objects.get(owner_id=request.session["id"], id=ident))
	
	elif albumRequest == "color8":
		all_photos = UploadModel.objects.filter(owner_id=currentUser.user_id).order_by(user_settings.gallery_order_choice).reverse()
		test_pic = []

		for pic in all_photos:
			category = CategoryModel.objects.get(photo_id=pic.id)
			test_pic.append(category)

		for img in test_pic:
			if (img.joy >= 2):
				albumHasPic[2][1] = True
				emotionDeteted = True
			
			if (img.anger >= 2):
				albumHasPic[0][1] = True
				emotionDeteted = True

			if (img.sorrow >= 2):
				albumHasPic[3][1] = True
				emotionDeteted = True

			if (img.blurred >= 2):
				albumHasPic[1][1] = True
				emotionDeteted = True

			if (img.surprise >= 2):
				albumHasPic[4][1] = True
				emotionDeteted = True
		all_photos = []
		
		for ident in colourSortedPhotos[8]:
			all_photos.append(UploadModel.objects.get(owner_id=request.session["id"], id=ident))
	
	elif albumRequest == "color9":
		all_photos = UploadModel.objects.filter(owner_id=currentUser.user_id).order_by(user_settings.gallery_order_choice).reverse()
		test_pic = []

		for pic in all_photos:
			category = CategoryModel.objects.get(photo_id=pic.id)
			test_pic.append(category)

		for img in test_pic:
			if (img.joy >= 2):
				albumHasPic[2][1] = True
				emotionDeteted = True
			
			if (img.anger >= 2):
				albumHasPic[0][1] = True
				emotionDeteted = True

			if (img.sorrow >= 2):
				albumHasPic[3][1] = True
				emotionDeteted = True

			if (img.blurred >= 2):
				albumHasPic[1][1] = True
				emotionDeteted = True

			if (img.surprise >= 2):
				albumHasPic[4][1] = True
				emotionDeteted = True
		all_photos = []
		
		for ident in colourSortedPhotos[9]:
			all_photos.append(UploadModel.objects.get(owner_id=request.session["id"], id=ident))

	print(emotionDeteted)
	return render(request, 'app/gallery.html', locals())

def PhotoView(request, path):

	if not logged_in(request):
		return redirect("/login")

	clear_session(request)

	currentUser = User.objects.get(user_id=request.session["id"])
	user_settings = UserSettings.objects.get(owner_id = currentUser.user_id)

	userFontSizeText = user_settings.preferred_font_size
	userFontSizeHeading1 = (int(user_settings.preferred_font_size)*2)
	userFontSizeHeading2 = (int(user_settings.preferred_font_size) + ((int(user_settings.preferred_font_size)) /2))
	userFontSizeHeading3 = (int(user_settings.preferred_font_size) + ((int(user_settings.preferred_font_size)) /3))
	tts = user_settings.text_to_speech
	theme = user_settings.background_colour
	
	username = currentUser.username

	photo = UploadModel.objects.get(photo_path = path)

	pk = int(photo.id)

	photo_path = str(photo.photo_path)

	categories = []
	labels = []
	prop_array = []
	objects_array = []
	text_array= []

	categories = CategoryModel.objects.get(photo_id = pk)

	labels = photo.labels["Labels"]
	prop_array= photo.properties["Properties"]
	objects_array = photo.objects_api
	text_array = photo.text_image
	sharePhoto = sharePhotoForm(request.GET)
	
	if request.method == "GET":
		if sharePhoto.is_valid():
			shared = SharedModel()
			searched_username = sharePhoto.cleaned_data["user"]

			if searched_username == "":
				temp = locals()
				temp.update({ 'error_message': 'You need to add a user.' })
				return render(request, 'app/photo.html', temp)
			elif searched_username == username:
				temp = locals()
				temp.update({ 'error_message': 'You cannot share the photo with yourself.' })
				return render(request, 'app/photo.html', temp)
			elif searched_username == User.objects.get(user_id=photo.owner_id).username:
				temp = locals()
				temp.update({ 'error_message': 'You cannot share the photo with its owner.' })
				return render(request, 'app/photo.html', temp)
			else:
				if User.objects.filter(username = searched_username).count() == 0:
					temp = locals()
					temp.update({ 'error_message': 'The user does not exist.' })
					return render(request, 'app/photo.html', temp)
				else:	
					checkuser = User.objects.get(username = searched_username)
					validate = SharedModel.objects.filter(user_id = checkuser.user_id).filter(photo_id = photo.id).count()
					if validate < 1 and checkuser: 
						shared.user_id = checkuser.user_id
						shared.owner = currentUser
						shared.photo_id = photo.id
						shared.save()
					else:
						temp = locals()
						temp.update({ 'error_message': 'You already shared the photo with this user.' })
						return render(request, 'app/photo.html', temp)
		else:
			sharePhoto = sharePhotoForm()

	return render(request, 'app/photo.html', locals())

def DeletePhotoView(request, path):

	if not logged_in(request):
		return redirect("/login")

	clear_session(request)

	photo = UploadModel.objects.get(photo_path = path)
	pk = int(photo.id)
	photo_path = str(photo.photo_path)
	categories = CategoryModel.objects.get(photo_id = pk)
	photo.delete()
	categories.delete()

	if os.path.isfile(str(settings.MEDIA_ROOT) + "/" + photo_path):
		os.remove(str(settings.MEDIA_ROOT) + "/" + photo_path)

	return redirect(GalleryView)

def maps(request):
	
	if not logged_in(request):
		return redirect("/login")
	
	clear_session(request)

	user_settings = UserSettings.objects.get(owner_id = request.session["id"])

	userFontSizeText = user_settings.preferred_font_size
	userFontSizeHeading1 = (int(user_settings.preferred_font_size)*2)
	userFontSizeHeading2 = (int(user_settings.preferred_font_size) + ((int(user_settings.preferred_font_size)) /2))
	userFontSizeHeading3 = (int(user_settings.preferred_font_size) + ((int(user_settings.preferred_font_size)) /3))
	tts = user_settings.text_to_speech
	theme = user_settings.background_colour

	all_photos = UploadModel.objects.filter(owner_id=request.session["id"])
	location_array = []
	path_array = []
	index = 1

	for photo in all_photos:
		if photo.location:
			loc = []
			loc.append(str(photo.photo_path))
			for elem in photo.location:
				loc.append(elem[0])
				loc.append(elem[1])
				loc.append(elem[2])
				loc.append(index)
			index += 1
			
			location_array.append(loc) 

	return render(request, 'app/maps.html', locals())
	
def settings_general(request):

	if not logged_in(request):
		return redirect("/login")

	clear_session(request)

	user_settings = UserSettings.objects.get(owner_id = request.session["id"])

	userFontSizeText = user_settings.preferred_font_size
	userFontSizeHeading1 = (int(user_settings.preferred_font_size)*2)
	userFontSizeHeading2 = (int(user_settings.preferred_font_size) + ((int(user_settings.preferred_font_size)) /2))
	userFontSizeHeading3 = (int(user_settings.preferred_font_size) + ((int(user_settings.preferred_font_size)) /3))
	tts = user_settings.text_to_speech
	theme = user_settings.background_colour

	if request.method == "POST":
		data = request.POST
		action = data.get("theme_option_button")

		user_settings.background_colour = action
		user_settings.save()

		return redirect("/settings/general/")

	if request.method == "GET":
		data = request.GET
		action = data.get("gallery_option_button")

		if action == "upload_datetime":
			user_settings.gallery_order_choice = action
			user_settings.save()

			return redirect("/settings/general/")
		
		elif action == "datetime":
			user_settings.gallery_order_choice = action
			user_settings.save()

			return redirect("/settings/general/")

	return render(request, 'app/Settings/general_settings.html', locals())

def settings_account(request):

	if not logged_in(request):
		return redirect("/login")

	clear_session(request)

	currentUser = User.objects.get(user_id=request.session["id"])
	user_settings = UserSettings.objects.get(owner_id = currentUser.user_id)

	userFontSizeText = user_settings.preferred_font_size
	userFontSizeHeading1 = (int(user_settings.preferred_font_size)*2)
	userFontSizeHeading2 = (int(user_settings.preferred_font_size) + ((int(user_settings.preferred_font_size)) /2))
	userFontSizeHeading3 = (int(user_settings.preferred_font_size) + ((int(user_settings.preferred_font_size)) /3))
	tts = user_settings.text_to_speech
	theme = user_settings.background_colour

	profile_picture = currentUser.profile_picture
	
	username = currentUser.username
	join_date = currentUser.join_date

	profile_pic = ProfilePictureForm(request.POST, request.FILES, None)

	if request.method == "POST":
		if profile_pic.is_valid():
			currentUser.customPath = currentUser.username
			photo_path = profile_pic.cleaned_data["profile_pic"]
			currentUser.profile_picture = photo_path
			currentUser.save()

			return redirect("/settings/account")
		else:
			profile_pic = ProfilePictureForm()

	account_info = AccountSettingsForm(request.GET or None)

	account_info.fields['first'].widget.attrs.update({
            'placeholder': currentUser.first
        })

	account_info.fields['last'].widget.attrs.update({
            'placeholder': currentUser.last
        })

	account_info.fields['email'].widget.attrs.update({
            'placeholder': currentUser.email
        })

	account_info.fields['phone'].widget.attrs.update({
            'placeholder': currentUser.phone
        })
	
	if request.method == "GET":
		if account_info.is_valid():
			first = request.GET['first']

			if first != "":
				first = valid_name(first)

				if not first:
					temp = locals()
					temp.update({ 'error_message': 'Not a valid first name.' })
					return render(request, 'app/Settings/account_settings.html', temp)
			
				currentUser.first = first
				
			last = request.GET['last']

			if last != "":
				last = valid_name(last)

				if not last:
					temp = locals()
					temp.update({ 'error_message': 'Not a valid last name.' })
					return render(request, 'app/Settings/account_settings.html', temp)
				
				currentUser.last = last
			
			email = request.GET['email']

			if email != "":
				email_valid = valid_email(email)

				if not email_valid:
					temp = locals()
					temp.update({ 'error_message': 'Not a valid e-mail address.' })
					return render(request, 'app/Settings/account_settings.html', temp)
				
				if User.objects.filter(email=request.GET['email']):
					temp = locals()
					temp.update({ 'error_message': 'E-mail already exists.' })
					return render(request, 'app/Settings/account_settings.html', temp)		

				currentUser.email = email

			phone = request.GET['phone']

			if phone != "":
				phone_valid = valid_phone(phone)

				if not phone_valid:
					temp = locals()
					temp.update({ 'error_message': 'Not a valid phone number.' })
					return render(request, 'app/Settings/account_settings.html', temp)
				
				if User.objects.filter(phone=request.GET['phone']):
					temp = locals()
					temp.update({ 'error_message': 'Phone number already exists.' })
					return render(request, 'app/Settings/account_settings.html', temp)

				currentUser.phone = phone

			currentUser.save()

			return redirect("/settings/account")
		else:
			account_info = AccountSettingsForm()

			account_info.fields['first'].widget.attrs.update({
            'placeholder': currentUser.first
				})

			account_info.fields['last'].widget.attrs.update({
					'placeholder': currentUser.last
				})

			account_info.fields['email'].widget.attrs.update({
					'placeholder': currentUser.email
				})

			account_info.fields['phone'].widget.attrs.update({
					'placeholder': currentUser.phone
				})

	return render(request, 'app/Settings/account_settings.html', locals())

def remove_pp(request):

	if not logged_in(request):
		return redirect("/login")

	clear_session(request)

	currentUser = User.objects.get(user_id=request.session["id"])

	pp = currentUser.profile_picture
	pp_path = str(settings.MEDIA_ROOT) + "/" + str(pp)
	os.remove(pp_path)

	currentUser.profile_picture = ""
	currentUser.save()

	return redirect("/settings/account")

def remove_phone(request):

	if not logged_in(request):
		return redirect("/login")

	clear_session(request)

	currentUser = User.objects.get(user_id=request.session["id"])

	currentUser.phone = ""
	currentUser.two_factor_enabled = False
	currentUser.save()

	return redirect("/settings/account")

def delete_account(request):
	
	if not logged_in(request):
		return redirect("/login")

	clear_session(request)

	currentUser = User.objects.get(user_id=request.session["id"])
	username = currentUser.username

	user_settings = UserSettings.objects.get(owner_id = currentUser.user_id)

	photos = UploadModel.objects.filter(owner_id=currentUser.user_id)
	categories = getCategories(request)

	for category in categories:
		category.delete()

	photos.delete()

	user_settings.delete()

	currentUser.delete()

	user_dir = str(settings.MEDIA_ROOT) + "/" + username
	shutil.rmtree(user_dir, ignore_errors=True)

	delete_key(key_store_location, username, key_store_password)

	del request.session["id"]

	return redirect("/main")

def settings_password(request):

	if not logged_in(request):
		return redirect("/login")

	clear_session(request)

	currentUser = User.objects.get(user_id=request.session["id"])
	user_settings = UserSettings.objects.get(owner_id = currentUser.user_id)

	userFontSizeText = user_settings.preferred_font_size
	userFontSizeHeading1 = (int(user_settings.preferred_font_size)*2)
	userFontSizeHeading2 = (int(user_settings.preferred_font_size) + ((int(user_settings.preferred_font_size)) /2))
	userFontSizeHeading3 = (int(user_settings.preferred_font_size) + ((int(user_settings.preferred_font_size)) /3))
	tts = user_settings.text_to_speech
	theme = user_settings.background_colour

	password_change = PasswordSettingsForm(request.GET or None)

	if request.method == "GET":
		if password_change.is_valid():
			current_pass = request.GET['current_password']
			current_pass_format_valid = valid_password(current_pass)

			if not current_pass_format_valid:
				temp = locals()
				temp.update({ 'error_message': 'Not a valid password.' })
				return render(request, 'app/Settings/password_settings.html', temp)

			db_password = currentUser.password
			password_valid = validate(current_pass, db_password)

			if password_valid:
				new_password = request.GET["new_password"]
				new_password_repeat = request.GET["new_password_repeat"]

				password_valid = valid_password(new_password)

				if not password_valid:
					temp = locals()
					temp.update({ 'error_message': 'Not a valid password.' })
					return render(request, 'app/Settings/password_settings.html', temp)

				pass_strength = calc_password_str(new_password)

				if pass_strength != "Strong":
					temp = locals()
					temp.update({ 'error_message': 'Not a strong password.' })
					return render(request, 'app/Settings/password_settings.html', temp)

				if new_password != new_password_repeat:
					temp = locals()
					temp.update({'error_message': "Passwords do not match."})
					return render(request, 'app/Settings/password_settings.html', temp)

				secure_pass = enc_password(new_password)
				
				currentUser.password = str(secure_pass)

				currentUser.save()

				if change_key(key_store_location, currentUser.username, key_store_password):
					new_key_date = datetime.now()
					currentUser.key_creation_date = new_key_date
					currentUser.save()

				temp = locals()
				temp.update({'success_message' : 'Your password has been successfully changed.'})
				
				return render(request, 'app/Settings/password_settings.html', temp)
			else:
				temp = locals()
				temp.update({'error_message': 'Your current password is incorrect. Please enter the correct password.'})
				return render(request, 'app/Settings/password_settings.html', temp)
		else:
			password_change = PasswordSettingsForm()

	return render(request, 'app/Settings/password_settings.html', locals())
	
def settings_security(request):

	if not logged_in(request):
		return redirect("/login")

	if not "sec_sett_can_access" in request.session or not request.session["sec_sett_can_access"]:
		return redirect("/settings/access_check")
	
	currentUser = User.objects.get(user_id=request.session["id"])
	user_settings = UserSettings.objects.get(owner_id = currentUser.user_id)

	userFontSizeText = user_settings.preferred_font_size
	userFontSizeHeading1 = (int(user_settings.preferred_font_size)*2)
	userFontSizeHeading2 = (int(user_settings.preferred_font_size) + ((int(user_settings.preferred_font_size)) /2))
	userFontSizeHeading3 = (int(user_settings.preferred_font_size) + ((int(user_settings.preferred_font_size)) /3))
	tts = user_settings.text_to_speech
	theme = user_settings.background_colour

	phone_exists = currentUser.phone
	two_factor_enabled = user_settings.two_factor_enabled

	if request.method == "POST":
		data = request.POST
		action = data.get("two_factor")

		if action == "enable":
			if not phone_exists:
				temp = locals()
				temp.update({ 'error_message': 'You need to add a phone number to your account.' })
				return render(request, "app/Settings/security_settings.html", temp)
			
			user_settings.two_factor_enabled = True
			user_settings.save()

			return redirect("/settings/security/")

		elif action == "disable":
			user_settings.two_factor_enabled = False
			user_settings.save()

			return redirect("/settings/security/")

	return render(request, 'app/Settings/security_settings.html', locals())

def access_check(request):
	
	if not logged_in(request):
		return redirect("/login")

	if "sec_sett_can_access" in request.session:
		return redirect("/settings/security")

	clear_session(request)

	currentUser = User.objects.get(user_id=request.session["id"])
	user_settings = UserSettings.objects.get(owner_id = currentUser.user_id)

	userFontSizeText = user_settings.preferred_font_size
	userFontSizeHeading1 = (int(user_settings.preferred_font_size)*2)
	userFontSizeHeading2 = (int(user_settings.preferred_font_size) + ((int(user_settings.preferred_font_size)) /2))
	userFontSizeHeading3 = (int(user_settings.preferred_font_size) + ((int(user_settings.preferred_font_size)) /3))
	tts = user_settings.text_to_speech
	theme = user_settings.background_colour

	access_form = SettingsAccessForm(request.GET)

	if request.method == "GET":
		if access_form.is_valid():
			password_input = request.GET['password']
			password_format_valid = valid_password(password_input)

			if not password_format_valid:
				temp = locals()
				temp.update({ 'error_message': 'Not a valid password.' })
				return render(request, "app/Settings/access_check.html", temp)

			db_password = currentUser.password
			password_valid = validate(password_input, db_password)

			if password_valid:
				out = {'sec_sett_can_access': True }
				request.session.update(out)
				
				return redirect("/settings/security")
			else:
				temp = locals()
				temp.update({'error_message': 'Password is incorrect. Please enter the correct password.'})
				return render(request, "app/Settings/access_check.html", temp)
		else:
			access_form = SettingsAccessForm()

	return render(request, 'app/Settings/access_check.html', locals())

def settings_statistics(request):

	if not logged_in(request):
		return redirect("/login")

	clear_session(request)
	
	user_settings = UserSettings.objects.get(owner_id = request.session["id"])

	userFontSizeText = user_settings.preferred_font_size
	userFontSizeHeading1 = (int(user_settings.preferred_font_size)*2)
	userFontSizeHeading2 = (int(user_settings.preferred_font_size) + ((int(user_settings.preferred_font_size)) /2))
	userFontSizeHeading3 = (int(user_settings.preferred_font_size) + ((int(user_settings.preferred_font_size)) /3))
	tts = user_settings.text_to_speech
	theme = user_settings.background_colour

	loc_stat_enable = user_settings.location_stat_enabled
	emotion_stat_enable = user_settings.emotion_stat_enabled

	if request.method == "POST":
		data = request.POST
		action = data.get("statistics_button")

		if action == "enable":
			user_settings.location_stat_enabled = True
			user_settings.save()

			return redirect("/settings/statistics/")

		elif action == "disable":
			user_settings.location_stat_enabled = False
			user_settings.save()

			return redirect("/settings/statistics/")
	
	if request.method == "POST":
		data = request.POST
		action = data.get("emotion_button")

		if action == "enable":
			user_settings.emotion_stat_enabled = True
			user_settings.save()

			return redirect("/settings/statistics/")
	
		elif action == "disable":
			user_settings.emotion_stat_enabled = False
			user_settings.save()

			return redirect("/settings/statistics/")

	return render(request, 'app/Settings/statistics_settings.html', locals())

def settings_accessibility(request):

	if not logged_in(request):
		return redirect("/login")

	clear_session(request)

	user_settings = UserSettings.objects.get(owner_id = request.session["id"])

	userFontSizeText = user_settings.preferred_font_size
	userFontSizeHeading1 = (int(user_settings.preferred_font_size)*2)
	userFontSizeHeading2 = (int(user_settings.preferred_font_size) + ((int(user_settings.preferred_font_size)) /2))
	userFontSizeHeading3 = (int(user_settings.preferred_font_size) + ((int(user_settings.preferred_font_size)) /3))
	tts = user_settings.text_to_speech
	theme = user_settings.background_colour

	font_size = userFont(request.GET or None)

	if request.method == "GET":
		if font_size.is_valid():
			fontSize = request.GET['font_choice']

			user_settings.preferred_font_size = fontSize
			user_settings.save()

			return redirect("/settings/accessibility/")
		
	if request.method == "POST":
		data = request.POST
		action = data.get("tts_button")

		if action == "enable":
			user_settings.text_to_speech = True
			user_settings.save()

			return redirect("/settings/accessibility/")

		elif action == "disable":
			user_settings.text_to_speech = False
			user_settings.save()

			return redirect("/settings/accessibility/")

	return render(request, 'app/Settings/accessibility_settings.html', locals())

def settings_api(request):
	
	if not logged_in(request):
		return redirect("/login")

	clear_session(request)

	currentUser = User.objects.get(user_id=request.session["id"])
	user_token = currentUser.token

	user_settings = UserSettings.objects.get(owner_id = currentUser.user_id)

	userFontSizeText = user_settings.preferred_font_size
	userFontSizeHeading1 = (int(user_settings.preferred_font_size)*2)
	userFontSizeHeading2 = (int(user_settings.preferred_font_size) + ((int(user_settings.preferred_font_size)) /2))
	userFontSizeHeading3 = (int(user_settings.preferred_font_size) + ((int(user_settings.preferred_font_size)) /3))
	tts = user_settings.text_to_speech
	theme = user_settings.background_colour

	if request.method == "POST":
		data = request.POST
		action = data.get("token_button")

		if action == "generate":
			if user_token:
				temp = locals()
				temp.update({'error_message': 'You currently have a token. Please refresh the page.'})
				return render(request, "app/Settings/api_settings.html", temp)

			generate_token(currentUser.username)

			return redirect("/settings/api/")

	return render(request, 'app/Settings/api_settings.html', locals())

# Vision API methods:
#
def get_emotion_API(image_path):
	client, image_name = getImages(image_path)
	photoEmot = getEmotions(client, image_name)

	return photoEmot

def get_labels_API(image_path):
	client, image_name = getImages(image_path)
	photoLabels = getLabels(client, image_name)
	
	return photoLabels

def get_properties_API(image_path):
	client, image_name = getImages(image_path)
	photoProp = getProperties(client, image_name)

	return photoProp
    
def get_objects_API(image_path):
	client, image_name = getImages(image_path)
	photoObjs = getObjects(client, image_name)

	return photoObjs

def get_location_API(image_path):
	client, image_name = getImages(image_path)
	locationInfo = detect_landmarks(client, image_name)

	return locationInfo
    
def get_location_data(image_path):
	try:
		coordinates = getCoordinates(image_path)
		coordinates = tuple(coordinates)
		city = reverseGeocode(coordinates)
		
		return city
	except:
		return ""

def get_coordinates(image_path):
	try:
		coordinates = getCoordinates(image_path)
		return tuple(coordinates)
	except:
		return ""

def merge_location(image_path):
	locations = []
	location = []
	
	if get_coordinates(image_path) != "":
		coord1, coord2 = get_coordinates(image_path)
		location.append(get_location_data(image_path))
		location.append(coord1)
		location.append(coord2)
	
		locations.append(location)

	return(locations)

def get_datetime_data(image_path):
	try:
		outDate = getDateImage(image_path)
		return outDate
	except:
		return ""
		
def get_text_image(image_path):
	try:
		client, image_name = getImages(image_path)
		text_img = detect_text(client, image_name)
		return text_img
	except:
		return ""

# User Operations for registration + login + 2FA + 
# 	Account Recovery:
def enc_password(password):
    return hash(password)
    
def crop_phone_number(phone):
	number = phonenumbers.parse(phone)
	international_f = phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)

	splitted = international_f.split(" ")
	
	country_code = splitted[0]
	new_number = []
	str_new_number = ""

	for i in range(1, len(splitted)):
		new_number += splitted[i]

	for idx, word in enumerate(new_number):
		if word == "-":
			del new_number[idx]

	for j in range(len(new_number)-2):
		new_number[j] = "*"

	for s in new_number:
		str_new_number += s

	return f"{country_code}{str_new_number}"

def calc_password_str(password):
	password_scores = {1:'Weak', 2:'Weak', 3:'Medium', 4:'Strong'}
	password_strength = dict.fromkeys(['has_upper', 'has_lower', 'has_num', 'has_spec'], False)

	if len(password) < 8:
		return "Your password must be at least 8 characters long!"
	
	if re.search(r'[A-Z]', password):
		password_strength['has_upper'] = True
	if re.search(r'[a-z]', password):
		password_strength['has_lower'] = True
	if re.search(r'[0-9]', password):
		password_strength['has_num'] = True
	if re.search(r"[ !#$%&'()*+,-./[\\\]^_`{|}~"+r'"]', password):
		password_strength['has_spec'] = True

	score = len([i for i in password_strength.values() if i])

	return password_scores[score]

def generate_authentication_code(phone):
	code = str(random.randrange(10000000,99999999,8))
	print(f"GENERATED CODE = {code}")
	secure_code = enc_password(code)

	object = Authentication()
	object.phone = phone
	object.code = secure_code
	object.save()

	return code

def generate_recovery_code(email):
	length = 10
	lower = string.ascii_lowercase
	upper = string.ascii_uppercase
	num = string.digits

	all = lower + upper + num
	temp = random.sample(all, length)

	code = "".join(temp)
	secure_code = enc_password(code)

	object = AccountRecovery()
	object.email = email
	object.code = secure_code
	object.save()

	return code

def generate_token(username):
	token = secrets.token_urlsafe(32)
	currentUser = User.objects.get(username = username)
	
	currentUser.token = token
	currentUser.save()

	return token

# Getting current user's photos with emotions & location 
#	for albums + statistics:
def getCategories(request):
	categories = []
	photos = UploadModel.objects.filter(owner_id=request.session["id"])

	for phot in photos:
		cat = CategoryModel.objects.get(photo_id=phot.id)
		categories.append(cat)

	return categories

def get_number_of_emot_img(request):
	return len(getCategories(request))

def get_number_of_joy_img(request):
	joy_list = []
	categories = getCategories(request)

	for category in categories:

		if int(category.joy) > 0:
			joy_list.append(category)
	
	return len(joy_list)

def get_number_of_sorr_img(request):
	sorrow_list = []
	categories = getCategories(request)

	for category in categories:
		if int(category.sorrow) > 0:
			sorrow_list.append(category)
	
	return len(sorrow_list)

def get_number_of_angr_img(request):
	anger_list = []
	categories = getCategories(request)

	for category in categories:
		if int(category.anger) > 0:
			anger_list.append(category)
	
	return len(anger_list)

def get_number_of_surp_img(request):
	surprise_list = []
	categories = getCategories(request)

	for category in categories:
		if int(category.surprise) > 0:
			surprise_list.append(category)
	
	return len(surprise_list)

def get_number_of_blur_img(request):
	blurred_list = []
	categories = getCategories(request)

	for category in categories:
		if int(category.blurred) > 0:
			blurred_list.append(category)
	
	return len(blurred_list)

def get_location_img(request):
	photos_list = []
	photos = UploadModel.objects.filter(owner_id = request.session["id"])

	for photo in photos:
		if photo.location:
			photos_list.append(photo)

	return photos_list

def get_location_info(request):
	all_photos = UploadModel.objects.filter(owner_id=request.session["id"])
	location_array = []

	for photo in all_photos:
		if photo.location:
			loc = []
			for elem in photo.location:
				loc.append(elem[0])
			location_array.append(loc) 
	
	return location_array

def get_number_of_loc_img(request):
	return len(get_location_img(request))

# Operations for verifying user storage:
# 
def getAllSize(photos):
	out = 0
	for photo in photos:
		out += getPhotoSize(photo)
	
	return round(out / 1000000000, 2)

def getPhotoSize(photoObj):
    media = str(settings.MEDIA_ROOT)
    media.replace('\\','/')
    photo = media + '/' + str(photoObj.photo_path) 
    
    if not os.path.exists(photo):
        photo = media + '/' + str(photoObj.photo_path) + '.enc'

    return os.stat(photo).st_size

def getImageGB(imgPath):
	media = str(settings.MEDIA_ROOT)
	media.replace('\\','/')

	return round(os.stat(media + '/' + str(imgPath)).st_size / 1000000000, 2)
