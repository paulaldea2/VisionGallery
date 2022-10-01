from urllib import response
from google.cloud import vision
import os
import io

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "static/JSON/visiongallery-aabe5f69b6b1.json"

def getImages(image_name):
    client = vision.ImageAnnotatorClient()
    file_path = os.path.abspath(image_name)

    with io.open(file_path, 'rb') as image_file:
        content = image_file.read()

        image = vision.Image(content=content)

        return client,image

def sort_emotions(dic):

    if len(dic) < 1:
        return {}

    sorted_dic = {key: val for key, val in sorted(dic.items(), key = lambda ele: ele[1], reverse = True)}

    tmp = {}
    counter = 0
    while counter < 3:
        for key, value in sorted_dic.items():
            if counter != 3:
                tmp[key] = value
                counter += 1
            else:
                break

    return tmp

def sort_objects(dic):

    if len(dic) < 1:
        return {}

    sorted_dic = {key: val for key, val in sorted(dic.items(), key = lambda ele: ele[1], reverse = True)}

    tmp = {}
    counter = 0
    while counter < 5:
        for key, value in sorted_dic.items():
            if counter != 5:
                tmp[key] = value
                counter += 1
            else:
                break

    return tmp

# Detect Emotions:
#
def getEmotions(client, image):
    response = client.face_detection(image=image)
    faces = response.face_annotations

    likelihood_name = ('UNKNOWN', 'VERY_UNLIKELY', 'UNLIKELY', 'POSSIBLE','LIKELY', 'VERY_LIKELY')
    
    joy_rating = 0
    sorrow_rating = 0
    anger_rating = 0
    surprise_rating = 0
    blurred_rating = 0

    if len(faces) > 0:
        face = faces[0]
        joy_rating = likelihood_name.index(likelihood_name[face.joy_likelihood])
        sorrow_rating = likelihood_name.index(likelihood_name[face.sorrow_likelihood])
        anger_rating = likelihood_name.index(likelihood_name[face.anger_likelihood])
        surprise_rating = likelihood_name.index(likelihood_name[face.surprise_likelihood])
        blurred_rating = likelihood_name.index(likelihood_name[face.blurred_likelihood])

    emotions = {
        "Joy" : joy_rating,
        "Sorrow" : sorrow_rating,
        "Anger" : anger_rating,
        "Surprise" : surprise_rating,
        "Blurred" : blurred_rating,
    }

    print(emotions)

    if response.error.message:
        raise Exception('Somethong went wrong'.format(response.error.message))

    return sort_emotions(emotions)

# Detect Labels:
#
def getLabels(client, image):
    response = client.label_detection(image=image)
    labels = response.label_annotations
    
    print('\nLabels:')

    hastags_json = {
        "Labels": [],
    }

    hastags = []
    counter = 0
    for label in labels:
        if counter <= 5:
            hastags.append(str(label.description))
            counter += 1
        else:
            break

    if response.error.message:
        raise Exception('Something went wrong'.format(response.error.message))

    for elem in hastags:
        hastags_json["Labels"].append(elem)
        
    return hastags_json

# Detect Objects:
#
def getObjects(client, image):
    response = client.object_localization(image=image)
    objects = client.object_localization(image=image).localized_object_annotations

    print('\nNumber of objects found: {}'.format(len(objects)))
    
    objects_dic = {}

    if len(objects) > 0:
        for obj in objects:
            objects_dic[obj.name] = obj.score

    if response.error.message:
        raise Exception('Something went wrong'.format(response.error.message))

    return sort_objects(objects_dic)

# Get Properties:
#
def getProperties(client, image):
    response =  client.image_properties(image=image)
    colors = response.image_properties_annotation.dominant_colors.colors
    print('\nProperties: ')
    
    properties_json = {
        "Properties": [],
    }
    dominant_color = colors[0].color

    red = int(dominant_color.red)
    green = int(dominant_color.green)
    blue = int(dominant_color.blue)

    colors_dominant = []
    colors_dominant.append(red)
    colors_dominant.append(green)
    colors_dominant.append(blue)

    if response.error.message:
        raise Exception ('Something went wrong'.format(response.error.message))
    
    for elem in colors_dominant:
        properties_json["Properties"].append(elem)

    return properties_json

# Detect Landmarks/Location:
#
def detect_landmarks(client, image):
    response = client.landmark_detection(image=image)
    landmarks = response.landmark_annotations

    print('Landmarks: ')
    landmarks_array = []
    for landmark in landmarks:
        landmark_array = []
        landmark_array.append(landmark.description)
        for location in landmark.locations:
            lat_lng = location.lat_lng
            landmark_array.append(lat_lng.latitude)
            landmark_array.append(lat_lng.longitude)
        
        landmarks_array.append(landmark_array)

    if response.error.message:
        raise Exception ('Something went wrong'.format(response.error.message))
    
    return landmarks_array

# Detect Texts:
#
def detect_text(client, image):
    print('Texts:')
    response = client.text_detection(image=image)
    texts = response.text_annotations
    
    text_array = []
    text_array.append(str(texts[0].description))
    
    if response.error.message:
        raise Exception ('Something went wrong'.format(response.error.message))
    
    return text_array
