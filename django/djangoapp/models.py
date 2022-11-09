from os.path import exists
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .mappers import UserTaskMapper, UserMapper
from django.http.response import HttpResponse
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
    def create(user, cookie, file, content_type, name, size):
        return UserTaskMapper.insert(user, cookie, file, content_type, name, size)

    @staticmethod
    def get_UserTask(file_id, user=None, user_token=None):
        if user is not None:
            userTask = UserTaskMapper.get(user=user, id=file_id)
        else:
            userTask = UserTaskMapper.get(user_token=user_token, id=file_id)
        return userTask

    @staticmethod
    def get_or_create(user, user_token):
        userTask = UserTaskMapper.get(user=user, user_token=user_token)

        if userTask is not None:
            return userTask, False

        return UserTaskMapper.insert(user=user, user_token=user_token), True

    @staticmethod
    def file_props_to_dict(file_id, user=None, user_token=None):
        if user is not None:
            userTask = UserTaskMapper.get(user=user, id=file_id)
        else:
            userTask = UserTaskMapper.get(user_token=user_token, id=file_id)
        if userTask is not None:
            return {'name': userTask.file_name, 'size': userTask.file_size, 'width': userTask.file_width, 'height': userTask.file_height, 'numframes': userTask.file_numframes}
        else:
            return None

    @staticmethod
    def get_frame(file_id, user=None, user_token=None):
        if user is not None:
            userTask = UserTaskMapper.get(user=user, id=file_id)
        else:
            userTask = UserTaskMapper.get(
                user_token=user_token, id=file_id)
        if userTask is not None:
            vid = VideoCapture(userTask.file.name)
            _, frame = vid.read()
            _, frame = imencode('.jpg', frame)
            vid.release()
            return frame
        else:
            return None

    @staticmethod
    def get_denoised_frame(file_id, user=None, user_token=None):
        if user is not None:
            userTask = UserTaskMapper.get(user=user, id=file_id)
        else:
            userTask = UserTaskMapper.get(
                user_token=user_token, id=file_id)
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
    def file_to_response(file_id, user=None, user_token=None):
        if user is not None:
            userTask = UserTaskMapper.get(user=user, id=file_id)
        else:
            userTask = UserTaskMapper.get(
                user_token=user_token, id=file_id)
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
        self.id = user.id
        self.password = user.password
        self.last_login = user.last_login
        self.is_superuser = user.is_superuser
        self.username = user.username
        self.last_name = user.last_name
        self.email = user.email
        self.is_staff = user.is_staff
        self.is_active = user.is_active
        self.date_joined = user.date_joined
        self.first_name = user.first_name

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
