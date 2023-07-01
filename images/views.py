from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .forms import ImageCreateFrom
from .models import Image
from actions.utils import create_action


@login_required
def image_create(req):
    if req.method == "POST":
        form = ImageCreateFrom(data=req.POST)
        if form.is_valid():
            cd = form.cleaned_data
            new_image = form.save(commit=False)

            new_image.user = req.user
            new_image.save()
            create_action(req.user, "bookmarked image", new_image)
            messages.success(req, "Image added successfully")

            return redirect(new_image.get_absolute_url())

    else:
        form = ImageCreateFrom(data=req.GET)

    return render(req, "images/image/create.html", {"section": "images", "form": form})


def image_detail(req, id, slug):
    image = get_object_or_404(Image, id=id, slug=slug)
    return render(
        req,
        "images/image/detail.html",
        {"section": "images", "image": image},
    )


@login_required
@require_POST
def image_like(req):
    image_id = req.POST.get("id")
    action = req.POST.get("action")

    if image_id and action:
        try:
            image = Image.objects.get(id=image_id)
            if action == "like":
                image.users_like.add(req.user)
                create_action(req.user, "likes", image)
            else:
                image.users_like.remove(req.user)

            return JsonResponse({"status": "ok"})

        except Image.DoesNotExist:
            pass

    return JsonResponse({"status": "error"})


@login_required
def image_list(req):
    images = Image.objects.all()
    paginator = Paginator(images, 8)
    page = req.GET.get("page")
    images_only = req.GET.get("images_only")

    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        # if page is not an integer, deliver the first page
        images = paginator.page(1)
    except EmptyPage:
        if images_only:
            # if ajax request and page out of range return an empty page
            return HttpResponse("")

        # if page out of range return last page of results
        images = paginator.page(paginator.num_pages)

    if images_only:
        return render(
            req,
            "images/image/list_images.html",
            {"section": "images", "images": images},
        )

    return render(
        req,
        "images/image/list.html",
        {"section": "images", "images": images},
    )
