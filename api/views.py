from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from api.serializers import ImageSerializer
from rest_framework.response import Response
from rest_framework import status
from api.renderer import ApiJSONRenderer
from algorithms.ocr_algorithms import run_ocr_tesseract, run_ocr_kraken, run_ocr_ocropy
from algorithms.utils import (read_opencv_image,
							  preprocess_image,
							  extract_line,
							  save_image,
							  modify_image_and_detect_bounding_boxes)
import uuid
import threading,time

class OCR(APIView):
	parser_classes = (MultiPartParser, FormParser)
	renderer_classes = (ApiJSONRenderer,)

	def post(self, request):
		file_serializer = ImageSerializer(data=request.data)
		file_serializer.is_valid(raise_exception=True)
		image = read_opencv_image(file_serializer.validated_data.get("image"))

		function_name = request.path.split('/')[2]
		func = getattr(self, function_name)
		text = func(image=image)

		return Response({"message": text}, status=status.HTTP_200_OK)

	# def segment(self, image, separtor=":"):
	#     text = self.tesseract(image)
	#     dict = {}
	#     text_arr = []
	#     lines = text.split("\n")
	#
	#     for line in lines:
	#         if line == "":
	#             continue
	#         result = extract_line(line, separtor)
	#         if result is None:
	#             text_arr.append(line)
	#         else:
	#             dict = {**dict, **result}
	#     if len(text_arr) >0:
	#         dict["others"] = text_arr
	#     return dict

	def tesseract(self, image):
		image = preprocess_image(image)

		return run_ocr_tesseract(image)

	def kraken(self, image):
		image = preprocess_image(image)
		return run_ocr_kraken(image)

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
		image = read_opencv_image(file_serializer.validated_data.get("image"))

		lowers, uppers, image = modify_image_and_detect_bounding_boxes(image)

		saved_image_name = save_image(image, str(uuid.uuid4()))

		message = {"url": saved_image_name,
				   "lowers_len": len(lowers),
				   "lowers": lowers,
				   "uppers_len": len(uppers),
				   "uppers": uppers}

		return Response({"message": message}, status=status.HTTP_200_OK)


class Test(APIView):

	def target(self,thread_name, index):
		print(thread_name+" "+str(index)+" start")
		time.sleep(5)
		print(thread_name+" "+str(index)+" end")

	def post(self, request):
		for i in range(5):
			threading.Thread(target=self.target, args=(request.data["thread"],i))
		return Response({"message": "OK"}, status=status.HTTP_200_OK)

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
