from django.urls import path
from . import views
urlpatterns = [
    path('',views.home, name="home"),
    path('teacher',views.teacher, name="teacher"),
    path('dispo',views.dispo, name="dispo"),
    path('add_dispoWeek',views.add_dispoWeek, name="add_dispoWeek"),
    path('get_available_hours',views.get_available_hours, name="get_available_hours"),
    path('admin/get_prof_dispo/',views.get_prof_dispo, name="get_prof_dispo"),
    
    path('profil',views.profil, name="profil"),
    # path('download_schedule_pdf',views.download_schedule_pdf, name="download_schedule_pdf"),
    # path('add_teacher',views.add_teacher, name="add_teacher")

]

