from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.http.response import HttpResponse, StreamingHttpResponse, HttpResponseRedirect
from django.views.decorators.gzip import gzip_page
from .models import UserTask, ClassUser
# from django.contrib.auth import authenticate, login, logout
from http import HTTPStatus
from django.http import JsonResponse
from django.contrib.auth.models import User
from os.path import exists

from cv2 import VideoCapture, VideoWriter, imencode, VideoWriter_fourcc
from .fastdvdnet import load_model, denoise

model, device = load_model()


class UserMapper:
    @staticmethod
    def get(username):
        return User.objects.filter(username=username)

    @staticmethod
    def insert(username, password, first_name, last_name, email):
        user = User.objects.create_user(
            username, password=password, first_name=first_name, last_name=last_name, email=email)
        user.save()
        return ClassUser(user)


class UserTaskMapper:
    @staticmethod
    def get(user, user_token, id):
        return UserTask.objects.get(user=user, user_token=user_token, id=id)

    @staticmethod
    def getAll(user):
        return UserTask.objects.filter(user=user)

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


def processing(obj):
    yield 'data:0\nid:0\n\n'
    fp = obj.file.name
    s_fp = fp.rsplit('/')
    ofp = s_fp[0] + '/denoised/' + str(obj.pk) + s_fp[1]

    #img = cv2.imdecode(np.fromstring(files[token][0], np.uint8), 1)
    #img = testtt(img)
    #files[token][0] = cv2.imencode('.png', img)[1].tobytes()

    i = 0

    vid = VideoCapture(fp)
    wdth = int(vid.get(3))
    hght = int(vid.get(4))
    fps = vid.get(5)
    cdc = int(vid.get(6))
    # @FIX разобраться с кодеками в докере линукс
    o_vid = VideoWriter(ofp, VideoWriter_fourcc(*'mp4v'), fps, (wdth, hght))

    for den_frame, proc in denoise(model, device, vid):
        o_vid.write(den_frame)
        yield 'data:{:.2f}\nid:{}\n\n'.format(proc, i)
        i += 1

    vid.release()
    o_vid.release()
    return


# Create your views here.

@csrf_exempt  # @FIX почему не работает без декоратора
def upload(request):
    if request.method == 'POST':
        if request.FILES['file'] is not None:
            if request.FILES['file'].content_type == 'video/mp4' or request.FILES['file'].content_type == 'video/avi':
                # request.user.is_authenticated:
                user = ClassUser(request.user)
                if user.is_authenticated():
                    userTask = UserTaskMapper.insert(
                        request.user, request.COOKIES["csrftoken"], request.FILES['file'], request.FILES['file'].content_type, request.FILES['file'].name, request.FILES['file'].size)
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
        user = ClassUser(request.user)
        if user.is_authenticated():
            userTask = UserTaskMapper.get(user=request.user, id=file_id)
        else:
            userTask = UserTaskMapper.get(
                user_token=request.COOKIES["csrftoken"], id=file_id)
        if userTask is not None:
            return JsonResponse(userTask.file_props_to_dict())
        else:
            return HttpResponse(status=HTTPStatus.BAD_REQUEST)
    else:
        return HttpResponse(status=HTTPStatus.METHOD_NOT_ALLOWED)


def getFilePreview(request, file_id):
    if request.method == 'GET':
        user = ClassUser(request.user)
        if user.is_authenticated():
            # проверить работу (раньше было: user_id=request.user.pk, id=file_id)
            userTask = UserTaskMapper.get(user=request.user, id=file_id)
        else:
            userTask = UserTaskMapper.get(
                user_token=request.COOKIES["csrftoken"], id=file_id)
        if userTask is not None:
            vid = VideoCapture(userTask.file.name)
            _, frame = vid.read()
            _, frame = imencode('.jpg', frame)
            vid.release()
            return HttpResponse(frame.tobytes(), content_type='image/jpeg')
        else:
            return HttpResponse(status=HTTPStatus.BAD_REQUEST)
    else:
        return HttpResponse(status=HTTPStatus.METHOD_NOT_ALLOWED)


def getFilePreviewDenoised(request, file_id):
    if request.method == 'GET':
        user = ClassUser(request.user)
        if user.is_authenticated():
            # проверить работу (раньше было: user_id=request.user.pk, id=file_id)
            userTask = UserTaskMapper.get(user=request.user, id=file_id)
        else:
            userTask = UserTaskMapper.get(
                user_token=request.COOKIES["csrftoken"], id=file_id)
        if userTask is not None:
            vid = VideoCapture(userTask.file.name)

            for den_frame, _ in denoise(model, device, vid):
                _, den_frame = imencode('.jpg', den_frame)
                break

            vid.release()
            return HttpResponse(den_frame.tobytes(), content_type='image/jpeg')
        else:
            return HttpResponse(status=HTTPStatus.BAD_REQUEST)
    else:
        return HttpResponse(status=HTTPStatus.METHOD_NOT_ALLOWED)


def progress(request, file_id):
    user = ClassUser(request.user)
    if user.is_authenticated():
        # проверить работу (раньше было: user_id=request.user.pk, id=file_id)
        userTask = UserTaskMapper.get(user=request.user, id=file_id)
    else:
        userTask = UserTaskMapper.get(
            user_token=request.COOKIES["csrftoken"], id=file_id)
    if userTask is not None:
        return StreamingHttpResponse(processing(userTask), content_type='text/event-stream')
    else:
        return HttpResponse(status=HTTPStatus.BAD_REQUEST)


@gzip_page
def download(request, file_id):
    if request.method == 'GET':
        user = ClassUser(request.user)
        if user.is_authenticated():
            # проверить работу (раньше было: user_id=request.user.pk, id=file_id)
            userTask = UserTaskMapper.get(user=request.user, id=file_id)
        else:
            userTask = UserTaskMapper.get(
                user_token=request.COOKIES["csrftoken"], id=file_id)
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
            # return FileResponse(io.BytesIO(file).seek(), as_attachment=True, filename='test.png')
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
        if UserMapper.get(request.POST['username']).exists():
            return HttpResponse(status=HTTPStatus.CONFLICT)
        else:
            user = UserMapper.insert(request.POST['username'], request.POST['password'],
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
