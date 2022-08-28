import numpy as np
import cv2


def add_noise(img, sigma):
    # mp add noise to not norm img bit better
    return img + np.random.normal(0, sigma / 255., img.shape)


def video_to_imgs(vid):
    #vid = cv2.VideoCapture('test/test2.mp4')
    #fps = vid.get(5)
    #cdc = int(vid.get(6))
    ret, frame = vid.read()
    while ret:
        frame = prev_img_proc(frame)
        yield frame
        ret, frame = vid.read()
    vid.release()


def prev_img_proc(img):
    #img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    img = np.float32(img) / 255.
    return img


def save_vid_from_imgs(imgs, fps, cdc, pth='output.mp4'):
    img = next(imgs)
    vid = cv2.VideoWriter(
        pth, cv2.VideoWriter_fourcc(chr(cdc & 0xff), chr((cdc >> 8) & 0xff), chr((cdc >> 16) & 0xff), chr((cdc >> 24) & 0xff)), fps, img.shape[-2::-1])
    img = fin_img_proc(img)
    vid.write(img)
    for img in imgs:
        img = fin_img_proc(img)
        vid.write(img)
    vid.release()
    return True


def fin_img_proc(img):
    # np.around((img * 255)) too slow
    img = (img * 255).clip(0, 255).astype(np.uint8)
    return img
