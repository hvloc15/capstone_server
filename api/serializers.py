from rest_framework import serializers
from .models import Image, Book


class ImageSerializer(serializers.ModelSerializer):
    separator = serializers.CharField(max_length=1, required=False)

    def validate_image(self, data):
        image = data
        if image is None:
            return serializers.ValidationError(
                "An image should be provided",
            )
        if image.size > 15 * 1024 * 1024:
            raise serializers.ValidationError(
                "Image file is too large ( > 15mb )."
            )
        if image.content_type not in ['image/jpeg', 'image/ajpeg','image/apng','image/ajpg','image/png', 'image/jpg']:
            print(image.content_type)
            raise serializers.ValidationError(
                "Sorry, we do not support that image type. Please try uploading a jpeg, jpg or png file.",
            )

        return data

    class Meta:
        model = Image
        fields = ('image','separator')


class BookSerializer(serializers.ModelSerializer):

    class Meta:
        model = Book
        fields = ('name',)
