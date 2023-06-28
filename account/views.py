from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Profile
from .forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm


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


def register(req):
    if req.method == "POST":
        user_form = UserRegistrationForm(req.POST)

        if user_form.is_valid():
            # create a new user object buy dont save it yet
            new_user = user_form.save(commit=False)
            # set the chosen password
            new_user.set_password(user_form.cleaned_data["password"])
            # save the user object
            new_user.save()

            # create the user profile
            Profile.objects.create(user=new_user)

            return render(req, "account/register_done.html", {"new_user": new_user})
    else:
        user_form = UserRegistrationForm()

    return render(req, "account/register.html", {"user_form": user_form})


@login_required
def edit(req):
    if req.method == "POST":
        user_form = UserEditForm(instance=req.user, data=req.POST)
        prof_form = ProfileEditForm(
            instance=req.user.profile, data=req.POST, files=req.FILES
        )

        if user_form.is_valid() and prof_form.is_valid():
            user_form.save()
            prof_form.save()
            messages.success(req, "Profile updated successfully")
        else:
            messages.error(req, "Error updating your profile")

    else:  # this is GET
        user_form = UserEditForm(instance=req.user)
        prof_form = ProfileEditForm(instance=req.user.profile)

    return render(
        req,
        "account/edit.html",
        {"user_form": user_form, "prof_form": prof_form},
    )
