from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone


from .models import Booking, Table

class UserForm(UserCreationForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)

    class Meta:
      model = User
      fields = (
          'first_name', 
          'last_name',
          'username',
          'email',
          'password1',
          'password2',
        )

    def save(self, commit=True):
        user = super(UserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
          user.save()
        return user



class BookingForm(forms.ModelForm):
    date = forms.DateTimeField(
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(
          attrs={"type": "datetime-local", "class": "form-control"},
          format="%Y-%m-%dT%H:%M",
        ),
    )

    def __init__(self, lounge, *args, **kwargs):
        super(BookingForm, self).__init__(*args, **kwargs)
        self.fields["table"].queryset = Table.objects.filter(
            lounge_id=lounge.id
        )
        self.lounge = lounge



    class Meta:
        model = Booking
        fields = (
          'table',
          'date',
          'total_guests'
        )

    def clean(self):
        cleaned_data = super().clean()

        date = cleaned_data.get("date")
        total_guests = cleaned_data.get("total_guests") 
        table = cleaned_data.get("table")
        min_guest = self.lounge.setting.min_guest


        if total_guests is not None:
            if total_guests > table.capacity:
                raise ValidationError({"total_guests": [f"The maximum table capacity is {table.capacity}"]})

            if total_guests < 1:
                raise ValidationError({"total_guests": ["Please choose a valid number of guests for your order."]})

            if total_guests < min_guest:
                raise ValidationError({"total_guests": [f"The minimum guests per booking is: {min_guest}"]})



        if date:
            if date < timezone.now():
                raise ValidationError({"date": ["Please choose a date and time that is in the future, thank you."]})
