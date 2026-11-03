from django import forms
from .models import ParkingSlot  , Rate,Location

class ParkingSlotForm(forms.ModelForm):
    class Meta:
        model = ParkingSlot
        fields = ['slot_number', 'vehicle_type', 'location', 'is_reserved']
        labels = {
            'slot_number': 'Parking Slot Number',
            'vehicle_type': 'Type of Vehicle',
            'location': 'Parking Location',
            'is_reserved': 'Is Reserved for Handicapped ?',
        }
        widgets = {
            'slot_number': forms.TextInput(attrs={'class': 'form-control','style': 'color: white;'}),
            'vehicle_type': forms.Select(attrs={'class': 'form-control' ,'style': 'color: white;' }),
            'location': forms.NumberInput(attrs={'class': 'form-control' ,'style': 'color: white;' }),
            'is_reserved': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
               


class RateForm(forms.ModelForm):
    class Meta:
        model = Rate
        fields = ['vehicle_type', 'rate_per_hour', 'rate_per_day']
        labels = {
            'vehicle_type': 'Vehicle Type',
            'rate_per_hour': 'Rate Per Hour',
            'rate_per_day': 'Rate Per Day',
        }
        widgets = {
            'vehicle_type': forms.Select(attrs={'class': 'form-control','style': 'color: white;'}),
            'rate_per_hour': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01','style': 'color: white;'}),
            'rate_per_day': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01','style': 'color: white;'}),
        }        
        
        
        

class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['location']
        labels = {
            'location': 'Location Name',            
        }
        widgets = {
            'location': forms.TextInput(attrs={'class': 'form-control'}),           
        }          