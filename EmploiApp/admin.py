from django.contrib import admin
from .models import (Etudiant, Department,
                    Group, Semestre,
                    Teacher, ProfDispoWeek,
                    Course, Classroom,
                    Seance, HourRange,
                    )
from .forms import SeanceForm

# Register your models here.

@admin.register(Etudiant)
class EtudiantAdmin(admin.ModelAdmin):
    pass

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    pass

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    pass

@admin.register(Semestre)
class SemestreAdmin(admin.ModelAdmin):
    pass

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    pass

@admin.register(ProfDispoWeek)
class ProfDispoWeekAdmin(admin.ModelAdmin):
    pass

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    pass

@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    pass

@admin.register(Seance)
class SeanceAdmin(admin.ModelAdmin):
    form = SeanceForm
    list_display = ['course', 'group', 'classroom', 'start_time', 'end_time']
    class Media:
        js = ('assets/js/seance_form.js',)  # Lien vers un fichier JavaScript personnalisé



@admin.register(HourRange)
class HourRangeAdmin(admin.ModelAdmin):
    pass
