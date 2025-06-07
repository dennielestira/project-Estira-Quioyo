from django.db import models


class Student(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    YEAR_LEVEL_CHOICES = [
        ('1', 'First Year'),
        ('2', 'Second Year'),
        ('3', 'Third Year'),
        ('4', 'Fourth Year'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15)
    student_number = models.CharField(max_length=20, unique=True)
    date_of_birth = models.DateField(default='2000-01-01')
    section = models.CharField(max_length=10, default='1')
    year_level = models.CharField(max_length=1, choices=YEAR_LEVEL_CHOICES, default='1')
    course = models.CharField(max_length=100, default='Undeclared')
    email = models.EmailField(default='example@example.com')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='O')


    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, default='ENG101')
    students = models.ManyToManyField(Student, related_name="subjects")

    def __str__(self):
        return f"{self.name} ({self.code})"


class Quiz(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=100)

class Activity(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='activities')
    title = models.CharField(max_length=100)

class Exam(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='exams')
    title = models.CharField(max_length=100)

class Grade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, null=True, blank=True)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, null=True, blank=True)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, null=True, blank=True)
    score = models.FloatField()
