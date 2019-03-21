from rest_framework.decorators import renderer_classes, api_view
from rest_framework_swagger.renderers import OpenAPIRenderer, SwaggerUIRenderer
import coreapi
from rest_framework import response
from rest_framework.schemas import SchemaGenerator
import coreapi
import coreschema
from rest_framework.renderers import CoreJSONRenderer


@api_view()
@renderer_classes([SwaggerUIRenderer, OpenAPIRenderer])
def schema_view(request):
    schema = coreapi.Document(
        title='Text recognition API',
        content={
            'api': {
                'run_tesseract': coreapi.Link(
                    title='Image',
                    url='/api/ocr/',
                    action='post',
                    fields=[
                        coreapi.Field(
                            name='image',
                            required=True,
                            location="form",
                            description='Upload image',
                            type='file',
                        )
                    ],
                    encoding="multipart/form-data",
                    description='Run tesseract algorithm'
                )
            }
        },
        description='API document'
    )

    return response.Response(schema)
