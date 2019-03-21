from django.conf.urls import url
from api.views import OCR, UploadImage, Segment, Test

urlpatterns = [
    url(r'^tesseract|kraken|ocropy/',OCR.as_view(), name='ocr'),
    url(r'^segment',Segment.as_view(), name='ocr'),
    url(r'^upload/',UploadImage.as_view(), name='upload'),
    url(r'^test/',Test.as_view(), name='test'),
]
