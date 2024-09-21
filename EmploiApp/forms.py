from django import forms
from .models import Seance, ProfDispoWeek, Course

class SeanceForm(forms.ModelForm):
    class Meta:
        model = Seance
        fields = ['group', 'course', 'classroom', 'prof_dispo']

    # On surcharge l'initialisation du formulaire
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Si un cours est sélectionné, on filtre les plages horaires en fonction du professeur de ce cours
        if 'course' in self.data:
            try:
                course_id = int(self.data.get('course'))
                course = Course.objects.get(id=course_id)
                self.fields['prof_dispo'].queryset = ProfDispoWeek.objects.filter(teacher=course.Teacher)
            except (ValueError, TypeError, Course.DoesNotExist):
                self.fields['prof_dispo'].queryset = ProfDispoWeek.objects.none()
        elif self.instance.pk:
            # Si c'est une modification d'une instance existante, on filtre également en fonction du professeur du cours
            self.fields['prof_dispo'].queryset = ProfDispoWeek.objects.filter(teacher=self.instance.course.teacher)
        else:
            # Par défaut, aucune plage horaire n'est affichée
            self.fields['prof_dispo'].queryset = ProfDispoWeek.objects.none()
