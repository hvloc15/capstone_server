import pytesseract
import torch
from torchvision.transforms import Compose
from algorithms.data_transform import Resize
from algorithms.model_loader import load_model
from algorithms import config


def run_ocr_crnn(image):
    assert image is not None
    input_size = [int(x) for x in config.input_size.split('x')]
    sample = {"img": image}
    transform = Compose([
        Resize(size=(input_size[0], input_size[1]))
    ])
    sample = transform(sample)
    image = torch.from_numpy(sample["img"].transpose((2, 0, 1))).float()

    net = load_model(input_size, config.abc, None, config.backend, config.snapshot, cuda=False)
    # assert not net.is_cuda
    assert not next(net.parameters()).is_cuda
    net = net.eval()
    with torch.no_grad():
        image = image.unsqueeze(0)
        assert image.size()[0] == 1 and image.size()[1] == 3 and image.size()[2] < image.size()[3]
        out = net(image, decode=True)
        result = out[0]
        return result


def run_ocr_tesseract(image):
    return pytesseract.image_to_string(image, lang="vie8")


def run_ocr_kraken(image):
    return pytesseract.image_to_string(image, lang="eng")


def run_ocr_ocropy(image):
    return pytesseract.image_to_string(image, lang="vie")
