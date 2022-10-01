from inspect import trace
from tkinter import E
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from app.models import *
from app.views import *

@csrf_exempt
@api_view(['GET'])
def api_get_public_user_info(request, username):
	
	if request.method == 'GET':
		try:
			user = User.objects.get(username = username)
		except:
			return Response({'error' : 'Not a valid username.'}, status=status.HTTP_404_NOT_FOUND)
		
		serializer = PublicUserSerializer(user)
		return JsonResponse(serializer.data, safe=False)

@csrf_exempt
@api_view(['GET'])
def api_get_user_info(request, username):
	try:
		try_user = User.objects.get(token=request.GET['token'])
	except:
		return Response({'error' : 'Not a valid token.'}, status=status.HTTP_401_UNAUTHORIZED)
	
	if try_user.username == username:
		if request.method == 'GET':
			user = User.objects.filter(username = username)
			serializer = UserSerializer(user, many=True)
			return JsonResponse(serializer.data, safe=False)
	else:
		return Response({'error' : 'Not a valid username.'}, status=status.HTTP_401_UNAUTHORIZED)

@csrf_exempt
@api_view(['GET'])
def api_get_photos_of_emotion(request, emotion):
	try:
		user = User.objects.get(token=request.GET['token'])
	except:
		return Response({'error' : 'Not a valid token.'}, status=status.HTTP_401_UNAUTHORIZED)
	
	try:
		photos = UploadModel.objects.filter(owner_id=user.user_id) 
	except Exception as e:
		return Response({'error' : 'Not a matching query for this user.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
	
	out_photos = []
	for photo in photos:
		try:
			photoEmote = CategoryModel.objects.get(**{'photo' : photo.id, emotion + '__gte' :  1})
		except:
			continue
		
		path = str(settings.MEDIA_ROOT) + "/" + str(photo.photo_path) + ".enc"

		if os.path.exists(path):
			user_key = get_key(key_store_location, user.username, ".tW1Te!Z021ckNbr3k1le", ".tW1Te!Z021ckNbr3k1le")
			decrypt_file(path, user_key)

		out_photos.append(str(photo.photo_path))

	return JsonResponse({'photos' : out_photos})

@csrf_exempt
@api_view(['GET'])
def api_get_photo(request, photo_name):
	
	try:
		currentUser = User.objects.get(token=request.GET['token'])
	except:
		return Response({'error' : 'Not a valid token'}, status=status.HTTP_401_UNAUTHORIZED)
	
	if os.path.isfile(str(settings.MEDIA_ROOT) + "/" + currentUser.username + '/' + photo_name) or os.path.isfile(str(settings.MEDIA_ROOT) + "/" + currentUser.username + '/' + photo_name + '.enc'):
		photo = UploadModel.objects.get(photo_path = currentUser.username + '/' + photo_name)
	else:
		return Response({'error' : 'No photo found with name given.'}, status=status.HTTP_404_NOT_FOUND)

	path = str(settings.MEDIA_ROOT) + "/" + str(photo.photo_path) + ".enc"

	if os.path.exists(path):
		user_key = get_key(key_store_location, currentUser.username, ".tW1Te!Z021ckNbr3k1le", ".tW1Te!Z021ckNbr3k1le")
		decrypt_file(path, user_key)
	serializer = UploadSerializer(photo)
	return JsonResponse({'url' : request.scheme + "://" + request.META['HTTP_HOST'] + "/media/" + str(photo.photo_path), 'photoInformation' : serializer.data})

@csrf_exempt
@api_view(['POST'])
def api_upload_photo(request):
	try:
		currentUser = User.objects.get(token=request.GET['token'])
	except:
		return Response({'error' : 'Not a valid token.'}, status=status.HTTP_401_UNAUTHORIZED)
	
	saved = False
	uploadFailed = False
	try :
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
				file = open('static/colours.txt' , 'w')
				file.write('{0} {1} {2} \n'.format(props[0], props[1], props[2]))
				file.close()
				object.text_image = get_text_image(full_photo_path)
				
				object.location = merge_location(full_photo_path)

				if object.location == []:
					object.location = get_location_API(full_photo_path)

				object.datetime = get_datetime_data(full_photo_path)

				remove_data(full_photo_path)

				userPhotos = UploadModel.objects.filter(owner_id=currentUser.user_id)
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

					return JsonResponse({'photo' : str(object.photo_path)})
				else:
					MyUploadForm = UploadForm()
					uploadFailed = True
					saved = False

					return Response({'error' : 'Save failed due to capacity exceedance.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
			else:
				MyUploadForm = UploadForm()
	except Exception as e:
		file = open("/errors/error.log", 'w')
		file.write(e)
		traceback = e.__traceback__.__str__()
		file.write(traceback)
		file.close
	return Response({'error' : 'Photo is not valid/present. '}, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['PUT'])
@parser_classes([MultiPartParser])
def api_update_emotion(request, photo_name):
	try:
		currentUser = User.objects.get(token=request.GET['token'])
	except:
		return Response({'error' : 'Not a valid token.'}, status=status.HTTP_401_UNAUTHORIZED)
	try:
		searched_photo = UploadModel.objects.get(photo_path__icontains = photo_name)
		categories = CategoryModel.objects.get(photo_id=searched_photo.id)
	except Exception as e:
		print(e)
		return Response({'error' : 'No such image found'}, status=status.HTTP_404_NOT_FOUND)

	if 'joy' in request.POST:
		categories.joy = request.POST['joy']
	if 'sorrow' in request.POST:
		categories.sorrow = request.POST['sorrow']
	if 'anger' in request.POST:
		categories.anger = request.POST['anger']
	if 'surprise' in request.POST:
		categories.surprise = request.POST['surprise']
	if 'blurred' in request.POST:
		categories.blurred = request.POST['blurred']
	
	categories.save()

	return JsonResponse({'photo_name' : photo_name})

@csrf_exempt
@api_view(['DELETE'])
def api_delete_photo(request, photo_name):
	try:
		currentUser = User.objects.get(token=request.GET['token'])
	except:
		return Response({'error' : 'Not a valid token.'}, status=status.HTTP_401_UNAUTHORIZED)
	
	if os.path.isfile(str(settings.MEDIA_ROOT) + "/" + currentUser.username + '/' + photo_name) or os.path.isfile(str(settings.MEDIA_ROOT) + "/" + currentUser.username + '/' + photo_name + '.enc'): 

		photo = UploadModel.objects.get(photo_path = currentUser.username + '/' + photo_name)
		
		pk = int(photo.id)
		photo_path = str(photo.photo_path)

		categories = CategoryModel.objects.get(photo_id = pk)

		photo.delete()
		categories.delete()

		os.remove(str(settings.MEDIA_ROOT) + "/" + photo_path)
	else:
		return Response({'error' : 'No photo found with name given.'}, status=status.HTTP_404_NOT_FOUND)
	return JsonResponse({'message' : 'Image has been deleted Successfully!'})
