from django.shortcuts import render, redirect
from django.contrib.auth import authenticate,login, logout
from .models import User,Club,Role
from django.contrib import messages
from .forms import LogInForm,SignUpForm
from django.contrib.auth.decorators import login_required
from .helpers import *
from django.core.exceptions import ObjectDoesNotExist


def home(request):
    return render(request, 'home.html')


@login_prohibited
def log_in(request):
    if request.method == 'POST':
        form = LogInForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    redirect_url = request.POST.get('next') or 'profile'
                    return redirect(redirect_url)
        messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
    form = LogInForm()
    next = request.GET.get('next') or ''
    return render(request, 'log_in.html', {'form': form , 'next':next})

def log_out(request):
    logout(request)
    return redirect('home')

@login_required
def profile(request):
    return render(request, 'profile.html')


@login_prohibited
def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request,user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'sign_up.html', {'form': form})

@login_required
@management_login_required_applicant_list
def applicants_list(request,club_name):
        current_club = Club.objects.get(club_name=club_name)
        applicants = User.objects.all().filter(
        club__club_name=current_club.club_name,
        role__club_role='APP')
        return render(request,'applicants_list.html', {'applicants':applicants, 'current_club':current_club})

@login_required
@management_login_required_accept_reject
def accept_applicant(request,club_name,user_id):
        current_club = Club.objects.get(club_name=club_name)
        try:
            applicant = User.objects.get(id=user_id,
            club__club_name=current_club.club_name,
            role__club_role='APP'
            )
            role = Role.objects.get(user=applicant,club=current_club,club_role='APP')
            role.toggle_member()
        except (ObjectDoesNotExist):
            return redirect('applicants_list', club_name=current_club.club_name)

        else:
            return applicants_list(request,current_club.club_name)

@login_required
@management_login_required_accept_reject
def reject_applicant(request,club_name,user_id):
        current_club = Club.objects.get(club_name=club_name)
        try:
            applicant = User.objects.get(id=user_id,
            club__club_name=current_club.club_name,
            role__club_role='APP'
            )
            Role.objects.get(user=applicant,club=current_club,club_role='APP').delete()

        except ObjectDoesNotExist:
            return redirect('applicants_list', club_name=current_club.club_name)
        else:
            return applicants_list(request,current_club.club_name)
