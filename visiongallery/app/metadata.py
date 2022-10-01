from datetime import datetime
from PIL import Image
from GPSPhoto import gpsphoto
import reverse_geocoder as rg

def getDateImage(image_path):
    format = '%Y:%m:%d %H:%M:%S.%f'
    
    tags = [(36867, 37521),  # (DateTimeOriginal, SubsecTimeOriginal)
            (36868, 37522),  # (DateTimeDigitized, SubsecTimeDigitized)
            (306, 37520), ]  # (DateTime, SubsecTime)
    
    exif = Image.open(image_path)._getexif()
    
    if exif != None:
        for t in tags:
            dat = exif.get(t[0])
            sub = exif.get(t[1], 0)
    
            dat = dat[0] if type(dat) == tuple else dat
            sub = sub[0] if type(sub) == tuple else sub

            if dat != None: 
                break

        if not dat: 
            return ""
        
        full = '{}.{}'.format(dat, sub)
        T = datetime.strptime(full, format)
        
        return T
    
    return ""

def getCoordinates(image_path):
	data = gpsphoto.getGPSData(image_path)

	latitude = data['Latitude']
	longitude = data['Longitude']

	list = []
	list.append(latitude)
	list.append(longitude)

	return list

def reverseGeocode(coordinates):
	result = rg.search(coordinates)
	city = result[0]['name']
	return city

def remove_data(image_path):
    image = Image.open(image_path)

    data = list(image.getdata())

    image_without_exif = Image.new(image.mode, image.size)
    image_without_exif.putdata(data)

    image_without_exif.save(image_path)
