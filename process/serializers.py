import base64
import uuid

from rest_framework import serializers
from django.core.files.base import ContentFile
from process.models import Process


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            # base64 encoded image - decode
            format, imgstr = data.split(';base64,') # format ~= data:image/X,
            ext = format.split('/')[-1] # guess file extension
            id = uuid.uuid4()
            data = ContentFile(base64.b64decode(imgstr), name=id.urn[9:] + '.' + ext)
        return super(Base64ImageField, self).to_internal_value(data)


class UploadImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Process
        fields = ('image',)