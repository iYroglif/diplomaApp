from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.http.response import HttpResponse, StreamingHttpResponse, HttpResponseRedirect
from django.views.decorators.gzip import gzip_page
from .models import UserTask, ClassUser
from http import HTTPStatus
from django.http import JsonResponse
from cv2 import VideoCapture

# Create your views here.


@csrf_exempt  # @FIX почему не работает без декоратора
def upload(request):
    if request.method == 'POST':
        if request.FILES['file'] is not None:
            if request.FILES['file'].content_type == 'video/mp4' or request.FILES['file'].content_type == 'video/avi':
                if request.user.is_authenticated:
                    userTask = UserTask.create(request.user, request.COOKIES["csrftoken"], request.FILES['file'],
                                               request.FILES['file'].content_type, request.FILES['file'].name, request.FILES['file'].size)
                else:
                    userTask, created = UserTask.get_or_create(
                        user=None, user_token=request.COOKIES["csrftoken"])
                    if not created:
                        userTask.file.delete()
                    userTask.file = request.FILES['file']
                    userTask.content_type = request.FILES['file'].content_type
                    userTask.file_name = request.FILES['file'].name
                    userTask.file_size = request.FILES['file'].size
                userTask.save()
                vid = VideoCapture(userTask.file.name)
                userTask.file_width = int(vid.get(3))
                userTask.file_height = int(vid.get(4))
                userTask.file_fps = int(vid.get(5))
                userTask.file_numframes = int(vid.get(7))
                userTask.save()
                vid.release()
                return JsonResponse({'file_id': userTask.pk})
            else:
                return HttpResponse(status=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)
        else:
            return HttpResponse(status=HTTPStatus.BAD_REQUEST)
    else:
        return HttpResponse(status=HTTPStatus.METHOD_NOT_ALLOWED)


def getFileProps(request, file_id):
    if request.method == 'GET':
        if request.user.is_authenticated:
            fileProps = UserTask.file_props_to_dict(file_id, user=request.user)
        else:
            fileProps = UserTask.file_props_to_dict(
                file_id, user_token=request.COOKIES["csrftoken"])
        if fileProps is not None:
            return JsonResponse(fileProps)
        else:
            return HttpResponse(status=HTTPStatus.BAD_REQUEST)
    else:
        return HttpResponse(status=HTTPStatus.METHOD_NOT_ALLOWED)


def getFilePreview(request, file_id):
    if request.method == 'GET':
        if request.user.is_authenticated:
            frame = UserTask.get_frame(file_id, user=request.user)
        else:
            frame = UserTask.get_frame(
                file_id, user_token=request.COOKIES["csrftoken"])
        if frame is not None:
            return HttpResponse(frame.tobytes(), content_type='image/jpeg')
        else:
            return HttpResponse(status=HTTPStatus.BAD_REQUEST)
    else:
        return HttpResponse(status=HTTPStatus.METHOD_NOT_ALLOWED)


def getFilePreviewDenoised(request, file_id):
    if request.method == 'GET':
        if request.user.is_authenticated:
            den_frame = UserTask.get_denoised_frame(file_id, user=request.user)
        else:
            den_frame = UserTask.get_denoised_frame(
                file_id, user_token=request.COOKIES["csrftoken"])
        if den_frame is not None:
            return HttpResponse(den_frame.tobytes(), content_type='image/jpeg')
        else:
            return HttpResponse(status=HTTPStatus.BAD_REQUEST)
    else:
        return HttpResponse(status=HTTPStatus.METHOD_NOT_ALLOWED)


def progress(request, file_id):
    if request.user.is_authenticated:
        userTask = UserTask.get_UserTask(file_id, user=request.user)
    else:
        userTask = UserTask.get_UserTask(
            file_id, user_token=request.COOKIES["csrftoken"])
    if userTask is not None:
        return StreamingHttpResponse(userTask.processing(), content_type='text/event-stream')
    else:
        return HttpResponse(status=HTTPStatus.BAD_REQUEST)


@gzip_page
def download(request, file_id):
    if request.method == 'GET':
        if request.user.is_authenticated:
            response = UserTask.file_to_response(file_id, user=request.user)
        else:
            response = UserTask.file_to_response(
                file_id, user_token=request.COOKIES["csrftoken"])
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
        user = ClassUser(request.user)
        if user.is_authenticated():
            return JsonResponse({'username': request.user.username})
        else:
            return HttpResponse(status=HTTPStatus.UNAUTHORIZED)
    elif request.method == 'POST':
        user = ClassUser.userAuthenticate(
            request, request.POST['username'], request.POST['password'])
        # user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            user.userLogin(request)  # login(request, user)
            return JsonResponse({'username': request.user.username})
        else:
            return HttpResponse(status=HTTPStatus.UNAUTHORIZED)
    else:
        return HttpResponse(status=HTTPStatus.METHOD_NOT_ALLOWED)


def logout_view(request):
    ClassUser.userLogout(request)  # logout(request)
    return HttpResponseRedirect('/')


@csrf_exempt  # @FIX почему не работает без декоратора
def register(request):
    if request.method == 'POST':
        if ClassUser.already_exists(request.POST['username']):
            return HttpResponse(status=HTTPStatus.CONFLICT)
        else:
            user = ClassUser.create(request.POST['username'], request.POST['password'],
                                    request.POST['first_name'], request.POST['last_name'], request.POST['email'])
            user.userLogin(request)  # login(request, user)
            return HttpResponse(status=HTTPStatus.OK)
    else:
        return HttpResponse(status=HTTPStatus.METHOD_NOT_ALLOWED)


def getHistory(request):
    if request.method == 'GET':
        user = ClassUser(request.user)
        if user.is_authenticated():
            return JsonResponse(UserTask.getHistory(request.user))
        else:
            return HttpResponse(status=HTTPStatus.UNAUTHORIZED)
    else:
        return HttpResponse(status=HTTPStatus.METHOD_NOT_ALLOWED)
