from django.conf.urls import url
from api.views import OCR, UploadImage, Segment,OcrInSavedImage

urlpatterns = [
    url(r'^tesseract|kraken|ocropy|crnn/', OCR.as_view(), name='ocr'),
    url(r'^part/tesseract/', OcrInSavedImage.as_view(), name='ocr_part_of_image_tesseract'),
    url(r'^part/rnn/', OcrInSavedImage.as_view(), name='ocr_part_of_image_crnn'),
    url(r'^segment',Segment.as_view(), name='segment'),
    url(r'^upload/',UploadImage.as_view(), name='upload'),

]
