from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import CustomUserSignupForm


def home(request):
    return render(request, 'accounts/home.html')


def signup_view(request):
    if request.method == 'POST':
        form = CustomUserSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserSignupForm()

    return render(request, 'accounts/signup.html', {'form': form})


@login_required
def dashboard(request):
    return render(request, 'accounts/dashboard.html')