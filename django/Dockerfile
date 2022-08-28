FROM python:3.10.4
WORKDIR /django
COPY requirements.txt requirements.txt
RUN python -m pip install -r requirements.txt
RUN apt-get -y update && apt-get install -y python3-opencv
#RUN apt-get install -y ffmpeg
COPY . .
RUN python manage.py migrate --noinput
RUN python manage.py collectstatic --noinput
EXPOSE 8000
CMD daphne -b 0.0.0.0 -p 8000 diploma.asgi:application