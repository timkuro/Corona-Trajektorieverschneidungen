from django.forms import forms


class CoronaForm(forms.Form):
        your_name = forms.CharField(label='Your name', max_length=100)