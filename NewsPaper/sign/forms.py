from allauth.account.forms import SignupForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from django import forms


class BasicSignupForm(SignupForm):

    def save(self, request):
        user = super(BasicSignupForm, self).save(request)
        print(user)
        common_group = Group.objects.get(name='common')
        print(common_group)
        common_group.user_set.add(user)

        return user


class BaseRegisterForm(UserCreationForm):
    email = forms.EmailField(label="Email")
    first_name = forms.CharField(label="Имя")
    last_name = forms.CharField(label="Фамилия")

    class Meta:
        model = User
        fields = ("username",
                  "first_name",
                  "last_name",
                  "email",
                  "password1",
                  "password2", )

    def save(self, commit=True):
        user = super(BaseRegisterForm, self).save()
        common_group = Group.objects.get(name='common')
        common_group.user_set.add(user)

        return user

