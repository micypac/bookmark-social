from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

from .forms import LoginForm


def user_login(req):
    if req.method == "POST":
        form = LoginForm(req.POST)

        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(
                req,
                username=cd["username"],
                password=cd["password"],
            )

            if user is not None:
                if user.is_active:
                    login(req, user)
                    return HttpResponse("Authenticated Successfully")
                else:
                    return HttpResponse("Disabled Account")
            else:
                return HttpResponse("Invalid Login")
    else:
        form = LoginForm()

    return render(req, "account/login.html", {"form": form})


@login_required
def dashboard(req):
    return render(req, "account/dashboard.html", {"section": "dashboard"})
