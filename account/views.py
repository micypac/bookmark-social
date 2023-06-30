from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Profile, Contact
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


@login_required
def user_list(req):
    users = User.objects.filter(is_active=True)

    return render(
        req,
        "account/user/list.html",
        {"section": "people", "users": users},
    )


@login_required
def user_detail(req, username):
    user = get_object_or_404(
        User,
        username=username,
        is_active=True,
    )

    return render(
        req,
        "account/user/detail.html",
        {"section": "people", "user": user},
    )


@require_POST
@login_required
def user_follow(req):
    user_id = req.POST.get("id")
    action = req.POST.get("action")

    if user_id and action:
        try:
            user = User.objects.get(id=user_id)
            if action == "follow":
                Contact.objects.get_or_create(
                    user_from=req.user,
                    user_to=user,
                )
            else:
                Contact.objects.filter(user_from=req.user, user_to=user).delete()

            return JsonResponse({"status": "ok"})
        except User.DoesNotExist:
            return JsonResponse({"status": "error"})

    return JsonResponse({"status": "error"})
