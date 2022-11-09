from django.contrib.auth.models import User
from .models import UserTask


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
    def get(user, user_token, id):
        return UserTask.objects.get(user=user, user_token=user_token, id=id)

    @staticmethod
    def getAll(user_id):
        return UserTask.objects.filter(user=user_id)

    @staticmethod
    def insert(user, user_token, file, content_type, file_name, file_size):
        userTask = UserTask.objects.create(
            user=user,
            user_token=user_token,
            file=file,
            content_type=content_type,
            file_name=file_name,
            file_size=file_size)
        return userTask
