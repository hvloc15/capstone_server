from core.renderers import ConduitJSONRenderer
import json


class ApiJSONRenderer(ConduitJSONRenderer):
    object_label = "data"
