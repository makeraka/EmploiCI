import datetime
import json
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from EmploiApp.models import HourRange, ProfDispoWeek, Seance, Semestre, Teacher
from account.views import signin
from django.utils import timezone
# Create your views here.
login_required(login_url=signin)

def home(request):
    return render(request,'home.html')



#***********************creation de la vue des professeurs*****************************
from django.utils import timezone
import calendar
import locale

def teacher(request):
    # Définir la locale en français pour que les jours de la semaine et les mois soient affichés en français
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')  # ou 'fr_FR' selon le système

    # Obtenir le semestre sélectionné depuis les paramètres de la requête, ou utiliser un semestre par défaut
    semestre_id = request.GET.get('semestre', None)
    
    if semestre_id:
        try:
            semestre = Semestre.objects.get(id=semestre_id)
        except Semestre.DoesNotExist:
            semestre = None
    else:
        semestre = None

    # Filtrer les séances en fonction du semestre sélectionné
    if semestre:
        seances = Seance.objects.filter(course__semestre=semestre)
    else:
        seances = Seance.objects.all()

    # Obtenir la date et l'heure actuelles avec fuseau horaire
    now = timezone.now()

    # Créer un dictionnaire pour stocker les séances par jour
    days = {calendar.day_name[i]: [] for i in range(7)}  # Jours de la semaine en français
    for seance in seances:
        # Assurer que les datetime de la base de données sont "aware"
        start_time = timezone.make_aware(seance.start_time) if timezone.is_naive(seance.start_time) else seance.start_time
        end_time = timezone.make_aware(seance.end_time) if timezone.is_naive(seance.end_time) else seance.end_time

        # Utiliser le jour de la semaine (en français) pour organiser les séances
        day_name = start_time.strftime('%A')  # %A donne le nom du jour en français
        # Vérifier si la séance est en cours
        if start_time <= now <= end_time:
            seance.is_active = True
        else:
            seance.is_active = False
        days[day_name].append(seance)

    context = {
        'days': days,
        'current_day': now.strftime('%A'),  # Jour actuel en français
        'month': now.strftime('%B'),  # Mois actuel en français
        'year': now.year,
        'semestres': Semestre.objects.all(),  # Pour le sélecteur de semestre dans le template
        'selected_semestre': semestre
    }
    return render(request, 'teacher/teacher.html', context)


#*********************vue pour la disponibilité des professeurs *********************
from django.core.paginator import Paginator

def dispo(request):
    # Récupérer toutes les disponibilités actuelles et trier par jour de la semaine
    dispo_list = ProfDispoWeek.objects.all().order_by('day_week')
    
    # Récupérer tous les enseignants
    teachers = Teacher.objects.all()
    
    # Récupérer les semestres disponibles
    semestres = Semestre.objects.all()
    
    # Liste des jours de la semaine pour la liste déroulante
    DAYS_OF_WEEK = [
        (0, 'Lundi'),
        (1, 'Mardi'),
        (2, 'Mercredi'),
        (3, 'Jeudi'),
        (4, 'Vendredi'),
        (5, 'Samedi'),
        (6, 'Dimanche'),
    ]
    
    # Récupérer les paramètres GET : jour et semestre sélectionnés
    day_selected = request.GET.get('day', None)
    semestre_selected = request.GET.get('semestre', None)

    if day_selected and semestre_selected:
        try:
            semestre = Semestre.objects.get(id=semestre_selected)
        except Semestre.DoesNotExist:
            semestre = None

        if semestre:
            reserved_hours = ProfDispoWeek.objects.filter(
                day_week=day_selected,
                teacher__course__semestre=semestre
            ).values_list('hourRange', flat=True)
            
            available_hours = HourRange.objects.filter(course__semestre=semestre).exclude(id__in=reserved_hours)
        else:
            available_hours = HourRange.objects.none()
    else:
        available_hours = HourRange.objects.all()

    # Pagination
    paginator = Paginator(dispo_list, 8)  # Afficher 10 disponibilités par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Rendre le template avec les données contextuelles
    return render(request, "teacher/dispo.html", {
        "dispos": page_obj,
        "teachers": teachers,
        "hourRanges": available_hours,
        "semestres": semestres,
        "days_of_week": DAYS_OF_WEEK,
        "selected_day": day_selected,
        "selected_semestre": semestre_selected
    })


# **************************** ajax disponibilité de prof ******************************
from django.http import JsonResponse

# views.py
# views.py
from django.http import JsonResponse
from .models import ProfDispoWeek, HourRange

def get_available_hours(request):
    semestre = request.GET.get('semestre')
    day = request.GET.get('day')

    # Récupérer toutes les plages horaires déjà réservées pour le semestre et le jour choisis
    reserved_hours = ProfDispoWeek.objects.filter(day_week=day, teacher__course__semestre=semestre)

    # Récupérer toutes les plages horaires disponibles
    all_hours = HourRange.objects.all()

    # Exclure les plages horaires déjà prises
    available_hours = all_hours.exclude(id__in=reserved_hours.values('hourRange'))

    # Préparer les données pour le frontend
    response = {
        'available_hours': list(available_hours.values('id', 'start_time', 'end_time')),
        'reserved_hours': list(reserved_hours.values('teacher__username', 'hourRange__start_time', 'hourRange__end_time')),
    }
    return JsonResponse(response)


#**********************traitement d'ajout de la disponibilité**********************

def add_dispoWeek(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        try:
            # Récupérer l'enseignant
            teacher_username = request.POST.get("teacher")
            teacher = Teacher.objects.get(username=teacher_username)

            # Récupérer le jour de la semaine
            day = request.POST.get("day")

            # Récupérer la plage horaire
            rangetime_id = request.POST.get("rangetime")
            rangetime = HourRange.objects.get(id=rangetime_id)

            # Récupérer le semestre
            semestre_id = request.POST.get("semestre")
            semestre = Semestre.objects.get(id=semestre_id)

            # Vérifier si la plage horaire est déjà prise pour ce jour et ce semestre
            existing_dispo = ProfDispoWeek.objects.filter(day_week=day, hourRange=rangetime, teacher__course__semestre=semestre)
            
            if existing_dispo.exists():
                # Si une disponibilité existe déjà pour ce jour, cette plage horaire et ce semestre
                messages.error(request, "Cette plage horaire est déjà réservée pour ce jour dans ce semestre.")
                return HttpResponseRedirect(reverse("dispo"))

            # Si aucune disponibilité n'existe, on enregistre la nouvelle
            dispo = ProfDispoWeek(teacher=teacher, day_week=day, hourRange=rangetime)
            dispo.save()

            messages.success(request, "Disponibilité ajoutée avec succès.")
            return HttpResponseRedirect(reverse("dispo"))

        except Exception as e:
            messages.error(request, f"Échec de l'ajout de la disponibilité. Erreur : {str(e)}")
            return HttpResponseRedirect(reverse("dispo"))





#************************* profil**********************************
def profil(request):
     teacher = Teacher.objects.all()
    #  print(teacher)
     return render(request, "teacher/profil.html",{"teacher":teacher})


#************************* **********************************

from django.http import JsonResponse
from .models import Course, ProfDispoWeek

def get_prof_dispo(request):
    course_id = request.GET.get('course_id')
    try:
        course = Course.objects.get(id=course_id)
        prof_dispos = ProfDispoWeek.objects.filter(teacher=course.Teacher)
        data = [{'id': dispo.id, 'text': str(dispo.hourRange)} for dispo in prof_dispos]
    except Course.DoesNotExist:
        data = []

    return JsonResponse(data, safe=False)
