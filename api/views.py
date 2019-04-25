from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from api.serializers import ImageSerializer
from rest_framework.response import Response
from rest_framework import status
from api.renderer import ApiJSONRenderer
from algorithms.ocr_algorithms import run_ocr_tesseract, run_ocr_kraken, run_ocr_ocropy, run_ocr_crnn
from algorithms.utils import (read_inmemory_image_to_opencv,
							  preprocess_image,
							  save_image,
							  read_image,
							  perform_imgtxtenh_preprocess,
							  read_small_part_of_image,
							  modify_image_and_detect_bounding_boxes)
import uuid
import threading,time


class OCR(APIView):
	parser_classes = (MultiPartParser, FormParser)
	renderer_classes = (ApiJSONRenderer,)

	def post(self, request):
		file_serializer = ImageSerializer(data=request.data)
		file_serializer.is_valid(raise_exception=True)
		image = read_inmemory_image_to_opencv(file_serializer.validated_data.get("image"))

		function_name = request.path.split('/')[2]
		func = getattr(self, function_name)
		text = func(image=image)

		return Response({"message": text}, status=status.HTTP_200_OK)

	def tesseract(self, image):
		return run_ocr_tesseract(image)

	def kraken(self, image):
		image = preprocess_image(image)
		return run_ocr_kraken(image)

	def crnn(self, image):
		return run_ocr_crnn(image)

	def ocropy(self, image):
		return run_ocr_ocropy(image)

	def get(self, request):
		return Response({"message": "OK"}, status=status.HTTP_200_OK)


class Segment(APIView):
	parser_classes = (MultiPartParser, FormParser)
	renderer_classes = (ApiJSONRenderer,)

	def post(self, request):
		file_serializer = ImageSerializer(data=request.data)
		file_serializer.is_valid(raise_exception=True)
		image = read_inmemory_image_to_opencv(file_serializer.validated_data.get("image"))

		saved_image_name = save_image(image, str(uuid.uuid4()))  # /media/abc.jpg

		perform_imgtxtenh_preprocess(saved_image_name)

		image = read_image(saved_image_name)
		lowers, uppers, image = modify_image_and_detect_bounding_boxes(image)

		saved_image_name = save_image(image, saved_image_name, True)


		# lowers, uppers, image = modify_image_and_detect_bounding_boxes(image)
		# saved_image_name = save_image(image, str(uuid.uuid4()))

		message = {"url": saved_image_name,
				   "lowers_len": len(lowers),
				   "lowers": lowers,
				   "uppers_len": len(uppers),
				   "uppers": uppers}

		return Response({"message": message}, status=status.HTTP_200_OK)


class OcrInSavedImage(APIView):
	renderer_classes = (ApiJSONRenderer,)

	def post(self, request):
		data = request.data
		image_name, lower, upper = data.get('image'),data.get('lower'),data.get('upper')

		image = read_small_part_of_image(image_name, lower, upper)

		function_name = request.path.split('/')[3]
		func = getattr(self, function_name)
		text = func(image=image)

		return Response({"message": text}, status=status.HTTP_200_OK)

	def rnn(self, image): #rnn
		return run_ocr_crnn(image)

	def tesseract(self, image):
		return run_ocr_tesseract(image)


class UploadImage(APIView):
	parser_classes = (MultiPartParser, FormParser)
	renderer_classes = (ApiJSONRenderer,)

	def post(self, request):
		file_serializer = ImageSerializer(data=request.data)
		file_serializer.is_valid(raise_exception=True)
		file_serializer.save()
		return Response({"message": file_serializer.data}, status=status.HTTP_200_OK)

	def get(self, request):
		return Response({"message": "OK"}, status=status.HTTP_200_OK)
