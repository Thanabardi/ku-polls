"""Site views."""
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages


def signup(request):
    """Register a new user."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # username = form.cleaned_data.get('username')
            # raw_passwd = form.cleaned_data.get('password')
            user = form.save()
            login(request, user)
            return redirect('polls:index')
        else:
            messages.error(request, "username or password is incorrect.")
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})
