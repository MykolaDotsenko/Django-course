from __future__ import annotations

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_http_methods

from apps.accounts.forms import DeleteAccountForm, SignUpForm


def _safe_next(request: HttpRequest) -> str:
    candidate = request.POST.get("next") or request.GET.get("next") or ""
    if not candidate:
        return ""
    allowed = {request.get_host()}
    return (
        candidate
        if url_has_allowed_host_and_scheme(
            candidate,
            allowed_hosts=allowed,
            require_https=request.is_secure(),
        )
        else ""
    )


@require_http_methods(["GET", "POST"])
def signup(request: HttpRequest) -> HttpResponse:
    next_url = _safe_next(request)
    if request.user.is_authenticated:
        return redirect(next_url or reverse("profile"))

    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(
            request,
            "Account created. Saved pairs can now sync across signed-in devices.",
        )
        return redirect(next_url or reverse("saved_state"))

    return render(
        request,
        "accounts/signup.html",
        {"form": form, "next": next_url},
    )


@login_required
@require_http_methods(["GET"])
def profile(request: HttpRequest) -> HttpResponse:
    return render(request, "accounts/profile.html")


@login_required
@require_http_methods(["GET", "POST"])
def delete_account(request: HttpRequest) -> HttpResponse:
    form = DeleteAccountForm(request.POST or None, user=request.user)
    if request.method == "POST" and form.is_valid():
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, "Your account and account-owned saved data were deleted.")
        return redirect("converter")

    return render(request, "accounts/delete_account.html", {"form": form})
