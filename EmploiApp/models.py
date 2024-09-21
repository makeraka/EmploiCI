from django.db import models

# Create your models here.


class Department(models.Model):
    
    label = models.CharField(max_length = 150, unique=True)
    deleted = models.BooleanField(default=False)  # Using to control the deleting objects (true= Deleted, False = no deleted), to avoid real deleting in database
    
    def __str__(self):
        return self.label


class Group(models.Model):
    number = models.IntegerField()
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.number}-{self.department.label}'



class Semestre(models.Model):
    number = models.IntegerField()
    deleted = models.BooleanField(default=False)
    
    def __str__(self):
        return f'{self.number}'
    

class Etudiant(models.Model):
    username = models.CharField(max_length=50, primary_key=True)
    last_name = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    semestre = models.ForeignKey(Semestre, on_delete=models.CASCADE)
    deleted = models.BooleanField(default=False)
    def __str__(self):
        return self.username


class Teacher(models.Model):
    username = models.CharField(max_length=50, primary_key=True)
    last_name = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    telephone = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    deleted = models.BooleanField(default=False)
    def __str__(self): 
        return self.username
      
class Course(models.Model):
    label = models.CharField(max_length=50)
    semestre = models.ForeignKey(Semestre, on_delete=models.CASCADE)
    Teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.label}-Sem:{self.semestre}'


class Classroom(models.Model):
    label = models.CharField(max_length=50)
    busy = models.BooleanField()
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.label




class HourRange(models.Model):
    start_time = models.DateTimeField(auto_now=False, auto_now_add=False)
    end_time = models.DateTimeField(auto_now=False, auto_now_add=False)
    
    def __str__(self):
        return f'{self.start_time}-{self.end_time}'
    

from django.db import models

class ProfDispoWeek(models.Model):
    DAYS_OF_WEEK = [
        (0, 'Lundi'),
        (1, 'Mardi'),
        (2, 'Mercredi'),
        (3, 'Jeudi'),
        (4, 'Vendredi'),
        (5, 'Samedi'),
        (6, 'Dimanche'),
    ]
    
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    day_week = models.IntegerField(choices=DAYS_OF_WEEK)
    hourRange = models.ForeignKey(HourRange, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('teacher', 'day_week', 'hourRange')
        # Assure que la combinaison de ces champs est unique dans la base de données
        
        
class Seance(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    
    # Ajouter la relation avec ProfDispoWeek pour lier les séances aux disponibilités
    prof_dispo = models.ForeignKey(ProfDispoWeek, on_delete=models.CASCADE)
    
    def __str__(self):
        return f'Seance: {self.course.label} - {self.group.number}'

    # Méthode pour récupérer les heures de début et de fin de la disponibilité du professeur
    @property
    def start_time(self):
        return self.prof_dispo.hourRange.start_time

    @property
    def end_time(self):
        return self.prof_dispo.hourRange.end_time
    
