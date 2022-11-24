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


class ClassUserTask():
    def __init__(self, id=None, user_id=None, user_token=None, file=None, content_type=None, file_name=None, file_size=None, file_width=None, file_height=None, file_fps=None, file_numframes=None, date=None):
        self.id = id
        self.user_id = user_id
        self.user_token = user_token
        self.file = file
        self.content_type = content_type
        self.file_name = file_name
        self.file_size = file_size
        self.file_width = file_width
        self.file_height = file_height
        self.file_fps = file_fps
        self.file_numframes = file_numframes
        self.date = date

    def updateValues(self, userTask):
        self.id = userTask.pk
        self.user_id = userTask.user_id
        self.user_token = userTask.user_token
        self.file = userTask.file
        self.content_type = userTask.content_type
        self.file_name = userTask.file_name
        self.file_size = userTask.file_size
        self.file_width = userTask.file_width
        self.file_height = userTask.file_height
        self.file_fps = userTask.file_fps
        self.file_numframes = userTask.file_numframes
        self.date = userTask.date
        self.userTask = userTask

    def create(self):
        userTask = UserTaskMapper.insert(self)
        self.updateValues(userTask)

    def get_or_create(self):
        try:
            userTask = UserTaskMapper.get(self)
            self.updateValues(userTask)
            return False
        except:
            userTask = UserTaskMapper.insert(self)
            self.updateValues(userTask)
            return True

    def save(self):
        UserTaskMapper.update(self)

    def file_props_to_dict(self):
        userTask = UserTaskMapper.get(self)
        if userTask is not None:
            self.updateValues(userTask)
            return {'name': self.file_name, 'size': self.file_size, 'width': self.file_width, 'height': self.file_height, 'numframes': self.file_numframes}
        else:
            return None

    def get_frame(self):
        userTask = UserTaskMapper.get(self)
        if userTask is not None:
            self.updateValues(userTask)
            vid = VideoCapture(self.file.name)
            _, frame = vid.read()
            _, frame = imencode('.jpg', frame)
            vid.release()
            return frame
        else:
            return None

    def get_denoised_frame(self):
        userTask = UserTaskMapper.get(self)

        if userTask is not None:
            self.updateValues(userTask)
            vid = VideoCapture(self.file.name)

            for den_frame, _ in denoise(model, device, vid):
                _, den_frame = imencode('.jpg', den_frame)
                break

            vid.release()
            return den_frame
        else:
            return None

    def get_UserTask(self):
        userTask = UserTaskMapper.get(self)
        if userTask is not None:
            self.updateValues(userTask)
            return True
        else:
            return False

    def file_to_response(self):
        userTask = UserTaskMapper.get(self)

        if userTask is not None:
            self.updateValues(userTask)
            s_fp = self.file.name.rsplit('/')
            ofp = s_fp[0] + '/denoised/' + str(self.id) + s_fp[1]
            if exists(ofp):
                self.file.delete()
                self.file = ofp
                self.save()
            response = HttpResponse(
                self.file, content_type=self.content_type)
            response['Content-Disposition'] = "attachment; filename=denoised_" + \
                self.file_name
            return response
        else:
            return None

    def getHistory(self):
        return {'tasks': list(UserTaskMapper.getAll(self).order_by('-date').values('id', 'file_name', 'file_size', 'date'))}

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


class ClassUser(User):
    def __init__(self, user=None, username=None, password=None, first_name=None, last_name=None, email=None):
        self.user = user
        self.username = username
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.email = email

    def already_exists(self):
        return UserMapper.get(self).exists()

    def create(self):
        user = UserMapper.insert(self)
        self.user = user

    def is_authenticated(self):
        return self.user.is_authenticated

    def userAuthenticate(self, request):
        user = authenticate(request, username=self.username,
                            password=self.password)
        if user is not None:
            return ClassUser(user=user)
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
    def get(user):
        return User.objects.filter(username=user.username)

    @staticmethod
    def insert(user):
        user = User.objects.create_user(
            user.username, password=user.password, first_name=user.first_name, last_name=user.last_name, email=user.email)
        user.save()
        return user


class UserTaskMapper:
    @staticmethod
    def get(userTask):
        get = UserTask.objects.get
        if userTask.user_id is not None:
            get = partial(get, user_id=userTask.user_id)
        if userTask.user_token is not None:
            get = partial(get, user_token=userTask.user_token)
        if userTask.id is not None:
            get = partial(get, id=userTask.id)

        userTask = get()
        return userTask

    @staticmethod
    def getAll(userTask):
        return UserTask.objects.filter(user_id=userTask.user_id)

    @staticmethod
    def insert(userTask):
        create = partial(UserTask.objects.create,
                         user_id=userTask.user_id, user_token=userTask.user_token)
        if userTask.file is not None:
            create = partial(create, file=userTask.file)
        if userTask.content_type is not None:
            create = partial(create, content_type=userTask.content_type)
        if userTask.file_name is not None:
            create = partial(create, file_name=userTask.file_name)
        if userTask.file_size is not None:
            create = partial(create, file_size=userTask.file_size)

        userTask = create()
        return userTask

    @staticmethod
    def update(userTask):
        record = userTask.userTask
        record.file = userTask.file
        record.content_type = userTask.content_type
        record.file_name = userTask.file_name
        record.file_size = userTask.file_size
        record.file_width = userTask.file_width
        record.file_height = userTask.file_height
        record.file_fps = userTask.file_fps
        record.file_numframes = userTask.file_numframes

        record.save()


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
