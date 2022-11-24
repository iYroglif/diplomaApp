from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.http.response import HttpResponse, StreamingHttpResponse, HttpResponseRedirect
from django.views.decorators.gzip import gzip_page
from .models import ClassUser, ClassUserTask
from http import HTTPStatus
from django.http import JsonResponse
from cv2 import VideoCapture

# Create your views here.


@csrf_exempt
def upload(request):
    if request.method == 'POST':
        if request.FILES['file'] is not None:
            if request.FILES['file'].content_type == 'video/mp4' or request.FILES['file'].content_type == 'video/avi':
                if request.user.is_authenticated:
                    userTask = ClassUserTask(user_id=request.user.pk,
                                             user_token=request.COOKIES["csrftoken"],
                                             file=request.FILES['file'],
                                             content_type=request.FILES['file'].content_type,
                                             file_name=request.FILES['file'].name,
                                             file_size=request.FILES['file'].size)
                    userTask.create()
                else:
                    userTask = ClassUserTask(
                        user_token=request.COOKIES["csrftoken"])
                    created = userTask.get_or_create()
                    if not created:
                        userTask.file.delete()
                    userTask.file = request.FILES['file']
                    userTask.content_type = request.FILES['file'].content_type
                    userTask.file_name = request.FILES['file'].name
                    userTask.file_size = request.FILES['file'].size
                vid = VideoCapture(userTask.file.name)
                userTask.file_width = int(vid.get(3))
                userTask.file_height = int(vid.get(4))
                userTask.file_fps = int(vid.get(5))
                userTask.file_numframes = int(vid.get(7))
                userTask.save()
                vid.release()
                return JsonResponse({'file_id': userTask.id})
            else:
                return HttpResponse(status=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)
        else:
            return HttpResponse(status=HTTPStatus.BAD_REQUEST)
    else:
        return HttpResponse(status=HTTPStatus.METHOD_NOT_ALLOWED)


def getFileProps(request, file_id):
    if request.method == 'GET':
        if request.user.is_authenticated:
            userTask = ClassUserTask(id=file_id, user_id=request.user.pk)
            fileProps = userTask.file_props_to_dict()
        else:
            userTask = ClassUserTask(
                id=file_id, user_token=request.COOKIES["csrftoken"])
            fileProps = userTask.file_props_to_dict()
        if fileProps is not None:
            return JsonResponse(fileProps)
        else:
            return HttpResponse(status=HTTPStatus.BAD_REQUEST)
    else:
        return HttpResponse(status=HTTPStatus.METHOD_NOT_ALLOWED)


def getFilePreview(request, file_id):
    if request.method == 'GET':
        if request.user.is_authenticated:
            userTask = ClassUserTask(id=file_id, user_id=request.user.pk)
            frame = userTask.get_frame()
        else:
            userTask = ClassUserTask(
                id=file_id, user_token=request.COOKIES["csrftoken"])
            frame = userTask.get_frame()
        if frame is not None:
            return HttpResponse(frame.tobytes(), content_type='image/jpeg')
        else:
            return HttpResponse(status=HTTPStatus.BAD_REQUEST)
    else:
        return HttpResponse(status=HTTPStatus.METHOD_NOT_ALLOWED)


def getFilePreviewDenoised(request, file_id):
    if request.method == 'GET':
        if request.user.is_authenticated:
            userTask = ClassUserTask(id=file_id, user_id=request.user.pk)
            den_frame = userTask.get_denoised_frame()
        else:
            userTask = ClassUserTask(
                id=file_id, user_token=request.COOKIES["csrftoken"])
            den_frame = userTask.get_denoised_frame()
        if den_frame is not None:
            return HttpResponse(den_frame.tobytes(), content_type='image/jpeg')
        else:
            return HttpResponse(status=HTTPStatus.BAD_REQUEST)
    else:
        return HttpResponse(status=HTTPStatus.METHOD_NOT_ALLOWED)


def progress(request, file_id):
    if request.user.is_authenticated:
        userTask = ClassUserTask(id=file_id, user_id=request.user.pk)
        got = userTask.get_UserTask()
    else:
        userTask = ClassUserTask(
            id=file_id, user_token=request.COOKIES["csrftoken"])
        got = userTask.get_UserTask()
    if got is True:
        return StreamingHttpResponse(userTask.processing(), content_type='text/event-stream')
    else:
        return HttpResponse(status=HTTPStatus.BAD_REQUEST)


@gzip_page
def download(request, file_id):
    if request.method == 'GET':
        if request.user.is_authenticated:
            userTask = ClassUserTask(id=file_id, user_id=request.user.pk)
            response = userTask.file_to_response()
        else:
            userTask = ClassUserTask(
                id=file_id, user_token=request.COOKIES["csrftoken"])
            response = userTask.file_to_response()
        if response is not None:
            return response
        else:
            return HttpResponse(status=HTTPStatus.BAD_REQUEST)
    else:
        return HttpResponse(status=HTTPStatus.METHOD_NOT_ALLOWED)


@ensure_csrf_cookie
@csrf_exempt
def login_view(request):
    if request.method == 'GET':
        user = ClassUser(user=request.user)
        if user.is_authenticated():
            return JsonResponse({'username': user.user.username})
        else:
            return HttpResponse(status=HTTPStatus.UNAUTHORIZED)
    elif request.method == 'POST':
        user = ClassUser(
            username=request.POST['username'], password=request.POST['password'])
        user = user.userAuthenticate(request)
        if user is not None:
            user.userLogin(request)
            return JsonResponse({'username': user.username})
        else:
            return HttpResponse(status=HTTPStatus.UNAUTHORIZED)
    else:
        return HttpResponse(status=HTTPStatus.METHOD_NOT_ALLOWED)


def logout_view(request):
    ClassUser.userLogout(request)
    return HttpResponseRedirect('/')


@csrf_exempt
def register(request):
    if request.method == 'POST':
        user = ClassUser(username=request.POST['username'])
        if user.already_exists():
            return HttpResponse(status=HTTPStatus.CONFLICT)
        else:
            user = ClassUser(username=request.POST['username'],
                             password=request.POST['password'],
                             first_name=request.POST['first_name'],
                             last_name=request.POST['last_name'],
                             email=request.POST['email'])
            user.create()
            user.userLogin(request)
            return HttpResponse(status=HTTPStatus.OK)
    else:
        return HttpResponse(status=HTTPStatus.METHOD_NOT_ALLOWED)


def getHistory(request):
    if request.method == 'GET':
        user = ClassUser(request.user)
        if user.is_authenticated():
            userTask = ClassUserTask(user_id=request.user.pk)
            return JsonResponse(userTask.getHistory())
        else:
            return HttpResponse(status=HTTPStatus.UNAUTHORIZED)
    else:
        return HttpResponse(status=HTTPStatus.METHOD_NOT_ALLOWED)
