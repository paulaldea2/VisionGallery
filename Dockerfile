FROM python:3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /usr/src/app/team33-21

# Install requirements
COPY requirements.txt /usr/src/app/team33-21/
RUN pip3 install -r requirements.txt

# Install jdk
RUN apt update
RUN apt install -y openjdk-17-jdk

#COPY VisionGallery /etc/nginx/sites-available/
#COPY letsencrypt/ /etc/

# Copy files over
COPY . /usr/src/app/team33-21/

WORKDIR /usr/src/app/team33-21/visiongallery
EXPOSE 8000

#CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000", "--noreload"]

# Gunicorn setup
RUN mkdir -pv /var/log/gunicorn/
RUN mkdir -pv /var/run/gunicorn/
RUN chown -cR root:root /var/log/gunicorn/
RUN chown -cR root:root /var/run/gunicorn/

# Nginx setup
#RUN mkdir -p /etc/nginx/sites-enabled/
#RUN ln -s /etc/nginx/sites-available/VisionGallery /etc/nginx/sites-enabled/VisionGallery
#RUN mkdir -p /var/log/nginx/

# run gunicorn server
CMD ["gunicorn", "-c", "gunicorn/dev.py"]
