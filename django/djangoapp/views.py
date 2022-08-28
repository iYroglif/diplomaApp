from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.http.response import HttpResponse, StreamingHttpResponse, HttpResponseRedirect
from django.views.decorators.gzip import gzip_page
from .models import UserTask
from django.contrib.auth import authenticate, login, logout
from http import HTTPStatus
from django.http import JsonResponse
from django.contrib.auth.models import User
from os.path import exists

from cv2 import VideoCapture, VideoWriter, imencode, VideoWriter_fourcc
from .fastdvdnet import load_model, denoise

model, device = load_model()


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
                if request.user.is_authenticated:
                    obj = UserTask.objects.create(
                        user=request.user,
                        user_token=request.COOKIES["csrftoken"],
                        file=request.FILES['file'],
                        content_type=request.FILES['file'].content_type,
                        file_name=request.FILES['file'].name,
                        file_size=request.FILES['file'].size)
                else:
                    obj, created = UserTask.objects.get_or_create(
                        user=None,
                        user_token=request.COOKIES["csrftoken"])
                    if not created:
                        obj.file.delete()
                    obj.file = request.FILES['file']
                    obj.content_type = request.FILES['file'].content_type
                    obj.file_name = request.FILES['file'].name
                    obj.file_size = request.FILES['file'].size
                obj.save()
                vid = VideoCapture(obj.file.name)
                obj.file_width = int(vid.get(3))
                obj.file_height = int(vid.get(4))
                obj.file_fps = int(vid.get(5))
                obj.file_numframes = int(vid.get(7))
                obj.save()
                vid.release()
                return JsonResponse({'file_id': obj.pk})
            else:
                return HttpResponse(status=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)
        else:
            return HttpResponse(status=HTTPStatus.BAD_REQUEST)
    else:
        return HttpResponse(status=HTTPStatus.METHOD_NOT_ALLOWED)


def file_props(request, file_id):
    if request.method == 'GET':
        if request.user.is_authenticated:
            obj = UserTask.objects.get(user=request.user, id=file_id)
        else:
            obj = UserTask.objects.get(
                user_token=request.COOKIES["csrftoken"], id=file_id)
        if obj is not None:
            return JsonResponse({'name': obj.file_name, 'size': obj.file_size, 'width': obj.file_width, 'height': obj.file_height, 'numframes': obj.file_numframes})
        else:
            return HttpResponse(status=HTTPStatus.BAD_REQUEST)
    else:
        return HttpResponse(status=HTTPStatus.METHOD_NOT_ALLOWED)


def file_preview(request, file_id):
    if request.method == 'GET':
        if request.user.is_authenticated:
            obj = UserTask.objects.get(
                user_id=request.user.pk, id=file_id)
        else:
            obj = UserTask.objects.get(
                user_token=request.COOKIES["csrftoken"], id=file_id)
        if obj is not None:
            vid = VideoCapture(obj.file.name)
            _, frame = vid.read()
            _, frame = imencode('.jpg', frame)
            vid.release()
            return HttpResponse(frame.tobytes(), content_type='image/jpeg')
        else:
            return HttpResponse(status=HTTPStatus.BAD_REQUEST)
    else:
        return HttpResponse(status=HTTPStatus.METHOD_NOT_ALLOWED)


def file_preview_denoised(request, file_id):
    if request.method == 'GET':
        if request.user.is_authenticated:
            obj = UserTask.objects.get(
                user_id=request.user.pk, id=file_id)
        else:
            obj = UserTask.objects.get(
                user_token=request.COOKIES["csrftoken"], id=file_id)
        if obj is not None:
            vid = VideoCapture(obj.file.name)

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
    if request.user.is_authenticated:
        obj = UserTask.objects.get(
            user_id=request.user.pk, id=file_id)
    else:
        obj = UserTask.objects.get(
            user_token=request.COOKIES["csrftoken"], id=file_id)
    if obj is not None:
        return StreamingHttpResponse(processing(obj), content_type='text/event-stream')
    else:
        return HttpResponse(status=HTTPStatus.BAD_REQUEST)


@gzip_page
def download(request, file_id):
    if request.method == 'GET':
        if request.user.is_authenticated:
            obj = UserTask.objects.get(
                user_id=request.user.pk, id=file_id)
        else:
            obj = UserTask.objects.get(
                user_token=request.COOKIES["csrftoken"], id=file_id)
        if obj is not None:
            s_fp = obj.file.name.rsplit('/')
            ofp = s_fp[0] + '/denoised/' + str(obj.pk) + s_fp[1]
            if exists(ofp):
                obj.file.delete()
                obj.file = ofp
                obj.save()
            response = HttpResponse(obj.file, content_type=obj.content_type)
            response['Content-Disposition'] = "attachment; filename=denoised_" + obj.file_name
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
        if request.user.is_authenticated:
            return JsonResponse({'username': request.user.username})
        else:
            return HttpResponse(status=HTTPStatus.UNAUTHORIZED)
    elif request.method == 'POST':
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            login(request, user)
            return JsonResponse({'username': request.user.username})
        else:
            return HttpResponse(status=HTTPStatus.UNAUTHORIZED)
    else:
        return HttpResponse(status=HTTPStatus.METHOD_NOT_ALLOWED)


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')


@csrf_exempt  # @FIX почему не работает без декоратора
def register(request):
    if request.method == 'POST':
        if User.objects.filter(username=request.POST['username']).exists():
            return HttpResponse(status=HTTPStatus.CONFLICT)
        else:
            user = User.objects.create_user(
                request.POST['username'], password=request.POST['password'], first_name=request.POST['first_name'], last_name=request.POST['last_name'], email=request.POST['email'], )
            user.save()
            login(request, user)
            return HttpResponse(status=HTTPStatus.OK)
    else:
        return HttpResponse(status=HTTPStatus.METHOD_NOT_ALLOWED)


def history(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            return JsonResponse({'tasks': list(UserTask.objects.filter(user=request.user).order_by('-date').values('id', 'file_name', 'file_size', 'date'))})
        else:
            return HttpResponse(status=HTTPStatus.UNAUTHORIZED)
    else:
        return HttpResponse(status=HTTPStatus.METHOD_NOT_ALLOWED)
