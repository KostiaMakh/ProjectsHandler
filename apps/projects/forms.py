from django import forms

from config.constants import EQUIPMENT_TYPES
from projects.models import Position, Location, TechnologicalNode, Manufacture, Equipment, Complectation


class CreatePositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = ('name', 'quantity', 'technological_node', )


class CreateNodeForm(forms.ModelForm):
    class Meta:
        model = TechnologicalNode
        fields = ('name', 'node_number', 'location', )


class CreateLocationForm(forms.ModelForm):
    country = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control mb-3'}))
    city = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control mb-3'}))
    customer = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control mb-3'}))
    logo = forms.ImageField(max_length=255, widget=forms.FileInput(attrs={'class': 'form-control mb-3'}))

    class Meta:
        model = Location
        fields = ('country', 'city', 'customer', 'logo', )


class CreateEquipmentForm(forms.ModelForm):
    name = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control mb-3'}))
    price = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control mb-3'}))
    weight = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control mb-3'}))
    power = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control mb-3'}))
    type = forms.CharField(max_length=255,
                           widget=forms.Select(
                               choices=EQUIPMENT_TYPES,
                               attrs={'class': 'form-control mb-3'}
                           ))
    manufacture = forms.ModelChoiceField(
        queryset=Manufacture.objects.all(),
        empty_label="----------",
        widget=forms.Select(
            attrs={'class': 'form-control mb-3'}
        ))

    class Meta:
        model = Equipment
        fields = ('name', 'price', 'type', 'weight', 'power', 'manufacture', )


class CreateManufactureForm(forms.ModelForm):
    country = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control mb-3'}))
    name = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control mb-3'}))

    class Meta:
        model = Manufacture
        fields = ('country', 'name', )


class UpdateCompensationForm(forms.ModelForm):
    class Meta:
        model = Complectation
        fields = ('control_panel', 'local_control_panel', 'startup_works', 'mounting_kit', )
