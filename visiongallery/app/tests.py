from ntpath import join
from django.test import TestCase
from .models import User
import os
from .vision_api import *

# aaa

# Create your tests here.
class LoginTests(TestCase):
    def setUp(self):
        # set up logins
        User.objects.create(user_id=1,first="root",last="root",email="root@root.root",username="root",phone="",password="rtpwd",join_date="2022-03-21 12:24:45.536579",storage_size=1000)
        #User.objects.create(user_id=999,first="i",last="don't",email="exist@nope.nope",username="missingno",phone="",password="password",join_date="",storage_size=1000)

    def test_knownLogin(self):
        # test a known login
        known = User.objects.get(user_id=1)
        login = User.objects.filter(username="root",password="rtpwd")
        self.assertEqual(len(login)>0, True)
    def test_unknownLogin(self):
        # test an unknown login
        login = User.objects.filter(username="Idon't",password="exist")
        self.assertEqual(len(login)==0, True)

    def test_tooLongLogin(self):
        # test a login that is too long
        lol = ""
        for i in range(500):
            lol += "a"
        login = User.objects.filter(username=lol,password=lol)
        self.assertEqual(len(login)==0, True)

    def test_emptyLogin(self):
        # test an empty login
        login = User.objects.filter(username="",password="")

        self.assertEqual(len(login) ==0, True)

class RegTest(TestCase):
    def setUp(self):
        User.objects.create(user_id=1,first="root",last="root",email="root@root.root",username="root",phone="",password="rtpwd",join_date="2022-03-21 12:24:45.536579",storage_size=1000)

    def test_newUser(self):
        passs = True
        user_id = 2
        first="lol"
        last="fuckme"
        email="what.yougonna@do.about.it"
        username="big_chungus"
        phone="423123"
        password="passord"
        join_date="2022-03-21 12:24:45.536579"
        storage_size=2
        try:
            User.objects.create(user_id=user_id,first=first,last=last,email=email,username=username,phone=phone,password=password,join_date=join_date,storage_size=storage_size)
        except Exception as e:
            passs = False
        
        self.assertEqual(passs, True)

    def test_existingUser(self):
        passs = True
        user_id = 1
        first="root"
        last="root"
        email="root@root.root"
        username="root"
        phone=""
        password="rtpwd"
        join_date="2022-03-21 12:24:45.536579"
        storage_size=1000
        try:
            User.objects.create(user_id=user_id,first=first,last=last,email=email,username=username,phone=phone,password=password,join_date=join_date,storage_size=storage_size)
        except Exception as e:
            passs = False
        
        self.assertEqual(passs, False)
    
"""   def test_NoPassword(self):
        passs = True
        user_id = 2
        first="lol"
        last="fuckme"
        email="what.yougonna@do.about.it"
        username="big_chungus"
        phone="423123"
        
        join_date="2022-03-21 12:24:45.536579"
        storage_size=2
        try:
            User.objects.create(user_id=user_id,first=first,last=last,email=email,username=username,phone=phone,join_date=join_date,storage_size=storage_size)
        except Exception as e:
            passs = False
        
        self.assertEqual(passs, False)
    

    def test_NoUsername(self):
        passs = True
        user_id = 2
        first="lol"
        last="fuckme"
        email="what.yougonna@do.about.it"
        username=""
        phone="423123"
        password="passord"
        join_date="2022-03-21 12:24:45.536579"
        storage_size=2
        try:
            User.objects.create(user_id=user_id,first=first,last=last,email=email,phone=phone,password=password,join_date=join_date,storage_size=storage_size)
        except Exception as e:
            passs = False
        
        self.assertEqual(passs, False)

    
    def test_NoEmail(self):
        passs = True
        user_id = 2
        first="lol"
        last="fuckme"
        email=""
        username="big_chungus"
        phone="423123"
        password="passord"
        join_date="2022-03-21 12:24:45.536579"
        storage_size=2
        try:
            User.objects.create(user_id=user_id,first=first,last=last,username=username,phone=phone,password=password,join_date=join_date,storage_size=storage_size)
        except Exception as e:
            passs = False
        
        self.assertEqual(passs, False)

    def test_NoFirst(self):
        passs = True
        user_id = 2
        first=""
        last="fuckme"
        email="what.yougonna@do.about.it"
        username="big_chungus"
        phone="423123"
        password="passord"
        join_date="2022-03-21 12:24:45.536579"
        storage_size=2
        try:
            User.objects.create(user_id=user_id,last=last,email=email,username=username,phone=phone,password=password,join_date=join_date,storage_size=storage_size)
        except Exception as e:
            passs = False
        
        self.assertEqual(passs, False)

    def test_NoLast(self):
        passs = True
        user_id = 2
        first="lol"
        last=""
        email="what.yougonna@do.about.it"
        username="big_chungus"
        phone="423123"
        password="passord"
        join_date="2022-03-21 12:24:45.536579"
        storage_size=2
        try:
            User.objects.create(user_id=user_id,first=first,email=email,username=username,phone=phone,password=password,join_date=join_date,storage_size=storage_size)
        except Exception as e:
            passs = False
        
        self.assertEqual(passs, False)"""

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/root/app/static/JSON/visiongallery-aabe5f69b6b1.json"

class TestImageMethods(TestCase):

    #[Test getImage method]
    def test_getImage(self):
        image_names = os.listdir('/root/app/photos/')
        for image_name in image_names:
            client, image = getImages('/root/app/photos' + '/' + image_name)

    #[Test getEmotions method]
    def test_getEmotions(self):
        succ = False
        image_names = os.listdir('/root/app/photos/')
        client, image = getImages('/root/app/photos' + '/' + image_names[0])
        emote = getEmotions(client, image)
        allEmotes = ["Joy", "Sorrow", "Anger", "Surprise", "Blurred"]
        if len(emote) != 0 and any( x in emote for x in allEmotes):
            print("EMOTION SUCCESS!!")
            succ = True
        
        self.assertEqual(succ, True)

    #[Test getLabels method]
    def test_getLabels(self):
        succ = False
        image_names = os.listdir('/root/app/photos/')
        client, image = getImages('/root/app/photos' + '/' + image_names[0])
        labels = getLabels(client,image)
        print(labels)
        if len(labels) !=0 and "Labels" in labels:
            print("LABELS SUCCESS!!")
            succ = True
        
        self.assertEqual(succ, True)

    #[Test getObjects method]
    def test_getObjects(self):
        succ = False
        image_names = os.listdir('/root/app/photos/')
        client, image = getImages('/root/app/photos' + '/' + image_names[0])
        objects = getObjects(client, image)
        print(objects)
        if len(objects) != 0:
            print("OBJECTS SUCCESS!!")
            succ = True
        
        self.assertEqual(succ, True)

    #[Test getProperties method]
    def test_getProperties(self):
        succ = False
        image_names = os.listdir('/root/app/photos/')
        client, image = getImages('/root/app/photos' + '/' + image_names[0])
        props = getProperties(client, image)
        print(props)
        if len(props) != 0 and "Properties" in props:
            print("PROPS SUCCESS!!")
            succ = True
        
        self.assertEqual(succ, True)

    #[Test detect_text method]
    def test_detecttext(self):
        succ = False
        image_names = os.listdir('/root/app/photos/')
        client, image = getImages('/root/app/photos' + '/' + image_names[0])
        landmarks = detect_landmarks(client, image)
        print(landmarks)
        if len(landmarks) >= 0:
            print("LANDMARKS SUCCESS!!")
            succ = True
        
        self.assertEqual(succ, True)

    #Test detect_landmarks method]
    def test_getlandmarks(self):
        succ = False
        image_names = os.listdir('/root/app/photos/')
        client, image = getImages('/root/app/photos' + '/' + image_names[0])
   
        self.assertEqual(succ, True)

    #Test detect_landmarks method]
    def test_getlandmarks(self):
        succ = False
        image_names = os.listdir('/root/app/photos/')
        client, image = getImages('/root/app/photos' + '/' + image_names[0])
        text = detect_text(client, image)
        print(text)
        if len(text) >= 0:
            print("TEXT SUCCESS!!")      
            succ = True
        
        self.assertEqual(succ, True)


class UploadTests(TestCase):
    def test_normalUpload(self):
        # test standard upload case
        return

    def test_tooLargePhoto(self):
        # test upload of photo that is too large
        return

    def test_noPhoto(self):
        # test upload of no photo
        return

    def test_notPhoto(self):
        # test upload of file that is not an allowed filetype
        return

