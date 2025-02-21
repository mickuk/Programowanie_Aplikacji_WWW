from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from .forms import RegisterForm
from django.contrib.auth import logout

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Dezaktywuj konto do czasu potwierdzenia emaila
            user.save()
            
            # Generowanie tokenu potwierdzającego
            current_site = get_current_site(request)
            subject = 'Aktywuj swoje konto w Bibliotece'
            message = render_to_string('accounts/activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            
            user.email_user(subject, message)
            return render(request, 'accounts/register_done.html')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return render(request, 'accounts/activation_complete.html')
    else:
        return render(request, 'accounts/activation_invalid.html')

@login_required
def profile(request):
    return render(request, 'accounts/profile.html')


def wyloguj(request):
    logout(request)  # Wylogowuje użytkownika
    return redirect('lista_ksiazek')  # Przekierowanie na stronę z książkami


def custom_password_reset_complete(request):
    return render(request, 'accounts/password_reset_complete.html')