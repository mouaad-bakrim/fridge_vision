
from process.models import Process
from django import forms







class FridgeForm(forms.ModelForm):
    class Meta:
        model = Process
        fields = ['image']



