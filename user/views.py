from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView, PasswordResetView, PasswordResetDoneView, \
    PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm
from django.contrib.auth.mixins import LoginRequiredMixin


class ChangePwView(LoginRequiredMixin, PasswordChangeView):
    form_class = PasswordChangeForm
    success_url = reverse_lazy('home')
    template_name = 'registration/change_password.html'


class PwResetView(PasswordResetView):
    form_class = PasswordResetForm
    success_url = reverse_lazy('pw_reset_done')
    template_name = 'registration/pw_reset.html'


class PwResetDoneView(PasswordResetDoneView):
    template_name = 'registration/pw_reset_done.html'


class PwResetConfirmView(PasswordResetConfirmView):
    success_url = reverse_lazy('pw_reset_complete')
    template_name = 'registration/pw_reset_confirm.html'


class PwResetCompleteView(PasswordResetCompleteView):
    template_name = 'registration/pw_reset_complete.html'
