from django.conf import settings
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .views import UserTaskMapper

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
    def get_or_create(user, user_token):
        userTask = UserTaskMapper.get(user=user, user_token=user_token)

        if userTask is not None:
            return userTask, False

        # return UserTask.objects.create(user=user, user_token=user_token), True
        return UserTaskMapper.insert(user=user, user_token=user_token), True

    def file_props_to_dict(self):
        return {'name': self.file_name, 'size': self.file_size, 'width': self.file_width, 'height': self.file_height, 'numframes': self.file_numframes}

    @staticmethod
    def getHistory(user):
        return {'tasks': list(UserTaskMapper.getAll(user).order_by('-date').values('id', 'file_name', 'file_size', 'date'))}


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


# class AbstractUser(AbstractBaseUser, PermissionsMixin):
#     username_validator: UnicodeUsernameValidator = ...

#     username = models.CharField(max_length=150)
#     first_name = models.CharField(max_length=30, blank=True)
#     last_name = models.CharField(max_length=150, blank=True)
#     email = models.EmailField(blank=True)
#     is_staff = models.BooleanField()
#     is_active = models.BooleanField()
#     date_joined = models.DateTimeField()
