import torch
import torch.nn as nn
import numpy as np
from .utils import video_to_imgs, fin_img_proc
import torch.nn.functional as F


class CvBlock(nn.Module):
    '''(Conv2d => BN => ReLU) x 2'''

    def __init__(self, in_ch, out_ch):
        super(CvBlock, self).__init__()
        self.convblock = nn.Sequential(
            nn.Conv2d(in_ch, out_ch, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_ch, out_ch, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True)
        )

    def forward(self, x):
        return self.convblock(x)


class InputCvBlock(nn.Module):
    '''(Conv with num_in_frames groups => BN => ReLU) + (Conv => BN => ReLU)'''

    def __init__(self, num_in_frames, out_ch):
        super(InputCvBlock, self).__init__()
        self.interm_ch = 30
        self.convblock = nn.Sequential(
            nn.Conv2d(num_in_frames*(3+1), num_in_frames*self.interm_ch,
                      kernel_size=3, padding=1, groups=num_in_frames, bias=False),
            nn.BatchNorm2d(num_in_frames*self.interm_ch),
            nn.ReLU(inplace=True),
            nn.Conv2d(num_in_frames*self.interm_ch, out_ch,
                      kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True)
        )

    def forward(self, x):
        return self.convblock(x)


class DownBlock(nn.Module):
    '''Downscale + (Conv2d => BN => ReLU)*2'''

    def __init__(self, in_ch, out_ch):
        super(DownBlock, self).__init__()
        self.convblock = nn.Sequential(
            nn.Conv2d(in_ch, out_ch, kernel_size=3,
                      padding=1, stride=2, bias=False),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
            CvBlock(out_ch, out_ch)
        )

    def forward(self, x):
        return self.convblock(x)


class UpBlock(nn.Module):
    '''(Conv2d => BN => ReLU)*2 + Upscale'''

    def __init__(self, in_ch, out_ch):
        super(UpBlock, self).__init__()
        self.convblock = nn.Sequential(
            CvBlock(in_ch, in_ch),
            nn.Conv2d(in_ch, out_ch*4, kernel_size=3, padding=1, bias=False),
            nn.PixelShuffle(2)
        )

    def forward(self, x):
        return self.convblock(x)


class OutputCvBlock(nn.Module):
    '''Conv2d => BN => ReLU => Conv2d'''

    def __init__(self, in_ch, out_ch):
        super(OutputCvBlock, self).__init__()
        self.convblock = nn.Sequential(
            nn.Conv2d(in_ch, in_ch, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(in_ch),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_ch, out_ch, kernel_size=3, padding=1, bias=False)
        )

    def forward(self, x):
        return self.convblock(x)


class DenBlock(nn.Module):
    """ Definition of the denosing block of FastDVDnet.
    Inputs of constructor:
            num_input_frames: int. number of input frames
    Inputs of forward():
            xn: input frames of dim [N, C, H, W], (C=3 RGB)
            noise_map: array with noise map of dim [N, 1, H, W]
    """

    def __init__(self, num_input_frames=3):
        super(DenBlock, self).__init__()
        self.chs_lyr0 = 32
        self.chs_lyr1 = 64
        self.chs_lyr2 = 128

        self.inc = InputCvBlock(
            num_in_frames=num_input_frames, out_ch=self.chs_lyr0)
        self.downc0 = DownBlock(in_ch=self.chs_lyr0, out_ch=self.chs_lyr1)
        self.downc1 = DownBlock(in_ch=self.chs_lyr1, out_ch=self.chs_lyr2)
        self.upc2 = UpBlock(in_ch=self.chs_lyr2, out_ch=self.chs_lyr1)
        self.upc1 = UpBlock(in_ch=self.chs_lyr1, out_ch=self.chs_lyr0)
        self.outc = OutputCvBlock(in_ch=self.chs_lyr0, out_ch=3)

        self.reset_params()

    @staticmethod
    def weight_init(m):
        if isinstance(m, nn.Conv2d):
            nn.init.kaiming_normal_(m.weight, nonlinearity='relu')

    def reset_params(self):
        for _, m in enumerate(self.modules()):
            self.weight_init(m)

    def forward(self, in0, in1, in2, noise_map):
        '''Args:
                inX: Tensor, [N, C, H, W] in the [0., 1.] range
                noise_map: Tensor [N, 1, H, W] in the [0., 1.] range
        '''
        # Input convolution block
        x0 = self.inc(
            torch.cat((in0, noise_map, in1, noise_map, in2, noise_map), dim=1))
        # Downsampling
        x1 = self.downc0(x0)
        x2 = self.downc1(x1)
        # Upsampling
        x2 = self.upc2(x2)
        x1 = self.upc1(x1+x2)
        # Estimation
        x = self.outc(x0+x1)

        # Residual
        x = in1 - x

        return x


class FastDVDnet(nn.Module):
    """ Definition of the FastDVDnet model.
    Inputs of forward():
            xn: input frames of dim [N, C, H, W], (C=3 RGB)
            noise_map: array with noise map of dim [N, 1, H, W]
    """

    def __init__(self, num_input_frames=5):
        super(FastDVDnet, self).__init__()
        self.num_input_frames = num_input_frames
        # Define models of each denoising stage
        self.temp1 = DenBlock(num_input_frames=3)
        self.temp2 = DenBlock(num_input_frames=3)
        # Init weights
        self.reset_params()

    @staticmethod
    def weight_init(m):
        if isinstance(m, nn.Conv2d):
            nn.init.kaiming_normal_(m.weight, nonlinearity='relu')

    def reset_params(self):
        for _, m in enumerate(self.modules()):
            self.weight_init(m)

    def forward(self, xs, noise_map):
        '''Args:
                x: Tensor, [N, num_frames*C, H, W] in the [0., 1.] range
                noise_map: Tensor [N, 1, H, W] in the [0., 1.] range
        '''
        # First stage
        x20 = self.temp1(xs[0], xs[1], xs[2], noise_map)
        x21 = self.temp1(xs[1], xs[2], xs[3], noise_map)
        x22 = self.temp1(xs[2], xs[3], xs[4], noise_map)

        # Second stage
        x = self.temp2(x20, x21, x22, noise_map)

        return x


def remove_dataparallel_wrapper(state_dict):
    r"""Converts a DataParallel model to a normal one by removing the "module."
    wrapper in the module dictionary


    Args:
            state_dict: a torch.nn.DataParallel state dictionary
    """
    from collections import OrderedDict

    new_state_dict = OrderedDict()
    for k, v in state_dict.items():
        name = k[7:]  # remove 'module.' of DataParallel
        new_state_dict[name] = v

    return new_state_dict


def load_model(NUM_IN_FR_EXT=5, model_file='djangoapp/model.pth'):
    cuda = torch.cuda.is_available()
    if cuda:
        device = torch.device('cuda')
    else:
        device = torch.device('cpu')
    model_temp = FastDVDnet(num_input_frames=NUM_IN_FR_EXT)
    # Load saved weights
    state_temp_dict = torch.load(model_file, map_location=device)
    if cuda:
        device_ids = [0]
        model_temp = nn.DataParallel(model_temp, device_ids=device_ids).cuda()
    else:
        # CPU mode: remove the DataParallel wrapper
        state_temp_dict = remove_dataparallel_wrapper(state_temp_dict)
    model_temp.load_state_dict(state_temp_dict)
    model_temp.eval()
    return model_temp, device


def denoise(model, device, vid, noise_sigma=30):
    noise_sigma = noise_sigma / 255.
    with torch.no_grad():
        stp = 100 / vid.get(7)
        seq = video_to_imgs(vid)
        fFlag = True
        i = 0
        for img in seq:
            i += stp
            if fFlag:
                fFlag = False
                sh_im = img.shape
                expanded_h = sh_im[0] % 4
                if expanded_h:
                    expanded_h = 4-expanded_h
                expanded_w = sh_im[1] % 4
                if expanded_w:
                    expanded_w = 4-expanded_w
                padexp = (0, expanded_w, 0, expanded_h)
                sigma_noise = F.pad(input=torch.FloatTensor([noise_sigma]).to(device).expand(
                    (1, 1, sh_im[0], sh_im[1])), pad=padexp, mode='reflect')
                img2 = F.pad(input=torch.from_numpy(np.expand_dims(
                    next(seq).transpose(2, 0, 1), axis=0)), pad=padexp, mode='reflect')
                img3 = F.pad(input=torch.from_numpy(np.expand_dims(
                    next(seq).transpose(2, 0, 1), axis=0)), pad=padexp, mode='reflect')
                tmpimg = F.pad(input=torch.from_numpy(np.expand_dims(img.transpose(
                    2, 0, 1), axis=0)), pad=padexp, mode='reflect')
                inp = torch.stack([img3, img2, tmpimg, img2, img3]).to(device)
            else:
                inp[0] = inp[1]
                inp[1] = inp[2]
                inp[2] = inp[3]
                inp[3] = inp[4]
                inp[4] = F.pad(input=torch.from_numpy(
                    np.expand_dims(img.transpose(2, 0, 1), axis=0)), pad=padexp, mode='reflect')
            #inp = F.pad(input=inp, pad=(0, 0, 0, 0), mode='reflect')
            ot = model(inp, sigma_noise)
            if expanded_h:
                ot = ot[:, :, :-expanded_h, :]
            if expanded_w:
                ot = ot[:, :, :, :-expanded_w]
            yield (fin_img_proc(torch.clamp(torch.squeeze(ot), 0., 1.).cpu().numpy().transpose(1, 2, 0)), i)
        inp[0] = inp[1]
        inp[1] = inp[2]
        inp[2] = inp[3]
        inp[3] = inp[4]
        inp[4] = inp[2]
        yield (fin_img_proc(torch.clamp(torch.squeeze(model(inp, sigma_noise)), 0., 1.)
                                 .cpu().numpy().transpose(1, 2, 0)), i + stp)
        inp[0] = inp[1]
        inp[1] = inp[2]
        inp[2] = inp[3]
        inp[3] = inp[4]
        inp[4] = inp[0]
        yield (fin_img_proc(torch.clamp(torch.squeeze(model(inp, sigma_noise)), 0., 1.)
                                 .cpu().numpy().transpose(1, 2, 0)), 100)
    return
