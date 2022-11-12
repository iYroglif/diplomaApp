from os.path import exists
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http.response import HttpResponse
from functools import partial
from .fastdvdnet import load_model, denoise
from cv2 import VideoCapture, imencode, VideoWriter, VideoWriter_fourcc

model, device = load_model()

# Create your models here.


class UserTask(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             null=True, on_delete=models.CASCADE)
    user_token = models.CharField(max_length=64)
    file = models.FileField(upload_to='files/', null=True)
    content_type = models.CharField(max_length=254, blank=True, default='')
    file_name = models.CharField(max_length=254, blank=True, default='')
    file_size = models.PositiveBigIntegerField(blank=True, default=0)
    file_width = models.PositiveSmallIntegerField(blank=True, default=0)
    file_height = models.PositiveSmallIntegerField(blank=True, default=0)
    file_fps = models.PositiveSmallIntegerField(blank=True, default=0)
    file_numframes = models.PositiveBigIntegerField(blank=True, default=0)
    date = models.DateTimeField(auto_now=True)

    @staticmethod
    def create(user_id, cookie, file, content_type, name, size):
        return UserTaskMapper.insert(user_id, cookie, file, content_type, name, size)

    @staticmethod
    def get_UserTask(file_id, user_id=None, user_token=None):
        userTask = UserTaskMapper.get(
            user_id=user_id, user_token=user_token, id=file_id)
        return userTask

    @staticmethod
    def get_or_create(user_id, user_token):
        try:
            userTask = UserTaskMapper.get(
                user_id=user_id, user_token=user_token)
            return userTask, False
        except:
            return UserTaskMapper.insert(user_id=user_id, user_token=user_token), True

    @staticmethod
    def file_props_to_dict(file_id, user_id=None, user_token=None):
        userTask = UserTaskMapper.get(
            user_id=user_id, user_token=user_token, id=file_id)

        if userTask is not None:
            return {'name': userTask.file_name, 'size': userTask.file_size, 'width': userTask.file_width, 'height': userTask.file_height, 'numframes': userTask.file_numframes}
        else:
            return None

    @staticmethod
    def get_frame(file_id, user_id=None, user_token=None):
        userTask = UserTaskMapper.get(
            user_id=user_id, user_token=user_token, id=file_id)

        if userTask is not None:
            vid = VideoCapture(userTask.file.name)
            _, frame = vid.read()
            _, frame = imencode('.jpg', frame)
            vid.release()
            return frame
        else:
            return None

    @staticmethod
    def get_denoised_frame(file_id, user_id=None, user_token=None):
        userTask = UserTaskMapper.get(
            user_id=user_id, user_token=user_token, id=file_id)

        if userTask is not None:
            vid = VideoCapture(userTask.file.name)

            for den_frame, _ in denoise(model, device, vid):
                _, den_frame = imencode('.jpg', den_frame)
                break

            vid.release()
            return den_frame
        else:
            return None

    @staticmethod
    def file_to_response(file_id, user_id=None, user_token=None):
        userTask = UserTaskMapper.get(
            user_id=user_id, user_token=user_token, id=file_id)

        if userTask is not None:
            s_fp = userTask.file.name.rsplit('/')
            ofp = s_fp[0] + '/denoised/' + str(userTask.pk) + s_fp[1]
            if exists(ofp):
                userTask.file.delete()
                userTask.file = ofp
                userTask.save()
            response = HttpResponse(
                userTask.file, content_type=userTask.content_type)
            response['Content-Disposition'] = "attachment; filename=denoised_" + \
                userTask.file_name
            return response
        else:
            return None

    def processing(self):
        yield 'data:0\nid:0\n\n'
        fp = self.file.name
        s_fp = fp.rsplit('/')
        ofp = s_fp[0] + '/denoised/' + str(self.pk) + s_fp[1]

        i = 0

        vid = VideoCapture(fp)
        wdth = int(vid.get(3))
        hght = int(vid.get(4))
        fps = vid.get(5)
        cdc = int(vid.get(6))

        o_vid = VideoWriter(ofp, VideoWriter_fourcc(
            *'mp4v'), fps, (wdth, hght))

        for den_frame, proc in denoise(model, device, vid):
            o_vid.write(den_frame)
            yield 'data:{:.2f}\nid:{}\n\n'.format(proc, i)
            i += 1

        vid.release()
        o_vid.release()
        return

    @staticmethod
    def getHistory(user_id):
        return {'tasks': list(UserTaskMapper.getAll(user_id).order_by('-date').values('id', 'file_name', 'file_size', 'date'))}


class ClassUser(User):
    def __init__(self, user):
        self.user = user

    @staticmethod
    def already_exists(username):
        return UserMapper.get(username).exists()

    @staticmethod
    def create(username, password, first_name, last_name, email):
        user = UserMapper.insert(
            username, password, first_name, last_name, email)
        return ClassUser(user)

    def is_authenticated(self):
        return self.user.is_authenticated

    @staticmethod
    def userAuthenticate(request, username, password):
        user = authenticate(request, username=username, password=password)
        if user is not None:
            return ClassUser(user)
        return None

    def userLogin(self, request):
        login(request, self.user)
        return

    @staticmethod
    def userLogout(request):
        logout(request)
        return


class UserMapper:
    @staticmethod
    def get(username):
        return User.objects.filter(username=username)

    @staticmethod
    def insert(username, password, first_name, last_name, email):
        user = User.objects.create_user(
            username, password=password, first_name=first_name, last_name=last_name, email=email)
        user.save()
        return user


class UserTaskMapper:
    @staticmethod
    def get(user_id=None, user_token=None, id=None):
        get = UserTask.objects.get
        if user_id is not None:
            get = partial(get, user_id=user_id)
        if user_token is not None:
            get = partial(get, user_token=user_token)
        if id is not None:
            get = partial(get, id=id)

        return get()

    @staticmethod
    def getAll(user_id):
        return UserTask.objects.filter(user_id=user_id)

    @staticmethod
    def insert(user_id, user_token, file=None, content_type=None, file_name=None, file_size=None):
        create = partial(UserTask.objects.create,
                         user_id=user_id, user_token=user_token)
        if file is not None:
            create = partial(create, file=file)
        if content_type is not None:
            create = partial(create, content_type=content_type)
        if file_name is not None:
            create = partial(create, file_name=file_name)
        if file_size is not None:
            create = partial(create, file_size=file_size)

        userTask = create()
        return userTask
