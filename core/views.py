from multiprocessing import context
import socket
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView
from .models import Student, Subject, Quiz, Activity, Exam, Grade
from .forms import GradeForm
from rest_framework import viewsets
from .serializers import StudentSerializer, SubjectSerializer, QuizSerializer, ActivitySerializer, ExamSerializer, GradeSerializer

def base(request):
    return render(request, 'core/base.html')


# API URL switching based on environment
if 'pythonanywhere' in socket.gethostname():
    API_URL = 'https://danger.pythonanywhere.com/api'
else:
    API_URL = 'http://localhost:8000/api'

HEADERS = {'Content-Type': 'application/json'}



def grade_insert(request, assessment_type, assessment_id):
    if request.method == 'POST':
        # Ensure the assessment type is valid (quiz, activity, or exam)
        if assessment_type == 'quiz':
            assessment_model = Quiz
        elif assessment_type == 'activity':
            assessment_model = Activity
        elif assessment_type == 'exam':
            assessment_model = Exam
        else:
            return redirect('subject_list')  # Redirect if the assessment type is invalid

        # Fetch the corresponding assessment object using the ID
        assessment = assessment_model.objects.get(id=assessment_id)

        # Process grades for all students
        for student in Student.objects.all():
            grade = request.POST.get(f'grade_{assessment_type}_{assessment_id}_student_{student.id}')
            if grade:
                # Create or update the grade record
                Grade.objects.update_or_create(
                    student=student,
                    **{f'{assessment_type}': assessment},  # dynamically set quiz/activity/exam
                    defaults={'score': grade}
                )

        return redirect('subject_detail', subject_id=assessment.subject.id)

    # Handle GET request (e.g., render form with existing grades)
    return render(request, 'core/subject_detail.html', context)

# --------------- STUDENTS -------------------
def student_list(request):
    response = requests.get(f'{API_URL}/students/')
    students = response.json() if response.status_code == 200 else []
    return render(request, 'core/student_list.html', {'students': students})

def student_add(request):
    if request.method == 'POST':
        data = {
            'first_name': request.POST.get('first_name', ''),
            'last_name': request.POST.get('last_name', ''),
            'contact_number': request.POST.get('contact_number', ''),
            'student_number': request.POST.get('student_number', ''),
            'date_of_birth': request.POST.get('date_of_birth', ''),
            'email': request.POST.get('email', ''),
            'course': request.POST.get('course', ''),
            'section': request.POST.get('section', ''),
            'gender': request.POST.get('gender', ''),
            'year_level': request.POST.get('year_level', ''),
        }
        response = requests.post(f'{API_URL}/students/', json=data, headers=HEADERS)
        if response.status_code in [200, 201]:
            return redirect('student_list')
        # Optional: pass error message
        return render(request, 'core/student_form.html', {'student': None, 'error': 'Failed to add student'})
    return render(request, 'core/student_form.html', {'student': None})

def student_edit(request, student_id):
    if request.method == 'POST':
        data = {
            'first_name': request.POST.get('first_name', ''),
            'last_name': request.POST.get('last_name', ''),
            'contact_number': request.POST.get('contact_number', ''),
            'student_number': request.POST.get('student_number', ''),
            'date_of_birth': request.POST.get('date_of_birth', ''),
            'email': request.POST.get('email', ''),
            'course': request.POST.get('course', ''),
            'section': request.POST.get('section', ''),
            'gender': request.POST.get('gender', ''),
            'year_level': request.POST.get('year_level', ''),
        }
        requests.put(f'{API_URL}/students/{student_id}/', json=data, headers=HEADERS)
        return redirect('student_list')

    response = requests.get(f'{API_URL}/students/{student_id}/')
    student = response.json() if response.status_code == 200 else {}
    return render(request, 'core/student_form.html', {'student': student})

def student_delete(request, student_id):
    if request.method == 'POST':
        requests.delete(f'{API_URL}/students/{student_id}/', headers=HEADERS)
    return redirect('student_list')

# --------------- SUBJECTS -------------------

def subject_list(request):
    response = requests.get(f'{API_URL}/subjects/')
    subjects = response.json() if response.status_code == 200 else []
    return render(request, 'core/subject_list.html', {'subjects': subjects})

def subject_add(request):
    students = requests.get(f'{API_URL}/students/').json() if requests.get(f'{API_URL}/students/').status_code == 200 else []
    if request.method == 'POST':
        data = {
            'name': request.POST.get('name', ''),
            'code': request.POST.get('code', ''),
            'students': request.POST.getlist('students')
        }
        response = requests.post(f'{API_URL}/subjects/', json=data, headers=HEADERS)
        if response.status_code in [200, 201]:
            return redirect('subject_list')
        return render(request, 'core/subject_form.html', {'subject': None, 'students': students, 'enrolled_student_ids': [], 'error': 'Failed to add subject'})
    return render(request, 'core/subject_form.html', {
        'subject': None,
        'students': students,
        'enrolled_student_ids': []
    })

def subject_edit(request, subject_id):
    subject_resp = requests.get(f'{API_URL}/subjects/{subject_id}/')
    subject = subject_resp.json() if subject_resp.status_code == 200 else {}
    students_resp = requests.get(f'{API_URL}/students/')
    students = students_resp.json() if students_resp.status_code == 200 else []

    enrolled_ids = subject.get('students', [])

    if request.method == 'POST':
        data = {
            'name': request.POST.get('name', ''),
            'code': request.POST.get('code', ''),
            'students': request.POST.getlist('students')
        }
        response = requests.put(f'{API_URL}/subjects/{subject_id}/', json=data, headers=HEADERS)
        if response.status_code in [200, 204]:
            return redirect('subject_list')
        return render(request, 'core/subject_form.html', {
            'subject': data,
            'students': students,
            'enrolled_student_ids': data['students'],
            'error': 'Failed to update subject'
        })

    return render(request, 'core/subject_form.html', {
        'subject': subject,
        'students': students,
        'enrolled_student_ids': enrolled_ids
    })

def subject_delete(request, subject_id):
    if request.method == 'POST':
        requests.delete(f'{API_URL}/subjects/{subject_id}/', headers=HEADERS)
    return redirect('subject_list')

def subject_detail(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    quizzes = Quiz.objects.filter(subject=subject)
    activities = Activity.objects.filter(subject=subject)
    exams = Exam.objects.filter(subject=subject)

    student_rows = []

    for student in subject.students.all():
        row = {
            'id': student.id,
            'name': f"{student.first_name} {student.last_name}",
            'quiz_scores': [],
            'activity_scores': [],
            'exam_scores': [],
            'has_grades': False,
        }

        # Quizzes
        for quiz in quizzes:
            grade = Grade.objects.filter(student=student, quiz=quiz).first()
            row['quiz_scores'].append(grade.score if grade else '-')
            if grade:
                row['has_grades'] = True

        # Activities
        for activity in activities:
            grade = Grade.objects.filter(student=student, activity=activity).first()
            row['activity_scores'].append(grade.score if grade else '-')
            if grade:
                row['has_grades'] = True

        # Exams
        for exam in exams:
            grade = Grade.objects.filter(student=student, exam=exam).first()
            row['exam_scores'].append(grade.score if grade else '-')
            if grade:
                row['has_grades'] = True

        student_rows.append(row)

    return render(request, 'core/subject_detail.html', {
        'subject': subject,
        'quizzes': quizzes,
        'activities': activities,
        'exams': exams,
        'student_rows': student_rows
    })


def insert_grade(request, subject_id, student_id):
    subject = get_object_or_404(Subject, id=subject_id)
    student = get_object_or_404(Student, id=student_id)

    quizzes = Quiz.objects.filter(subject=subject)
    activities = Activity.objects.filter(subject=subject)
    exams = Exam.objects.filter(subject=subject)

    if request.method == 'POST':
        # Save quizzes
        for quiz in quizzes:
            score = request.POST.get(f'quiz_{quiz.id}')
            if score is not None and score != '':
                # Update or create Grade for quiz
                grade_obj, created = Grade.objects.update_or_create(
                    student=student,
                    quiz=quiz,
                    defaults={'score': score}
                )
            else:
                # Optionally, delete the grade if score is empty
                Grade.objects.filter(student=student, quiz=quiz).delete()

        # Save activities
        for activity in activities:
            score = request.POST.get(f'activity_{activity.id}')
            if score is not None and score != '':
                grade_obj, created = Grade.objects.update_or_create(
                    student=student,
                    activity=activity,
                    defaults={'score': score}
                )
            else:
                Grade.objects.filter(student=student, activity=activity).delete()

        # Save exams
        for exam in exams:
            score = request.POST.get(f'exam_{exam.id}')
            if score is not None and score != '':
                grade_obj, created = Grade.objects.update_or_create(
                    student=student,
                    exam=exam,
                    defaults={'score': score}
                )
            else:
                Grade.objects.filter(student=student, exam=exam).delete()

        return redirect('subject_detail', subject_id=subject_id)

    # For GET request, prepare the current grades as tuples (model_instance, score)
    quiz_grades = []
    for quiz in quizzes:
        grade = Grade.objects.filter(student=student, quiz=quiz).first()
        quiz_grades.append((quiz, grade.score if grade else ''))

    activity_grades = []
    for activity in activities:
        grade = Grade.objects.filter(student=student, activity=activity).first()
        activity_grades.append((activity, grade.score if grade else ''))

    exam_grades = []
    for exam in exams:
        grade = Grade.objects.filter(student=student, exam=exam).first()
        exam_grades.append((exam, grade.score if grade else ''))

    return render(request, 'core/insert_grade.html', {
    'subject': subject,
    'student': student,
    'quiz_grades': quiz_grades,
    'activity_grades': activity_grades,
    'exam_grades': exam_grades,
    'is_editing': False  # 👈 Add this line
})


def edit_grade(request, subject_id, student_id):
    subject = get_object_or_404(Subject, id=subject_id)
    student = get_object_or_404(Student, id=student_id)
    quizzes = Quiz.objects.filter(subject=subject)
    activities = Activity.objects.filter(subject=subject)
    exams = Exam.objects.filter(subject=subject)

    if request.method == 'POST':
        for quiz in quizzes:
            score = request.POST.get(f'quiz_{quiz.id}')
            Grade.objects.update_or_create(
                student=student,
                quiz=quiz,
                defaults={'score': score}
            )

        for activity in activities:
            score = request.POST.get(f'activity_{activity.id}')
            Grade.objects.update_or_create(
                student=student,
                activity=activity,
                defaults={'score': score}
            )

        for exam in exams:
            score = request.POST.get(f'exam_{exam.id}')
            Grade.objects.update_or_create(
                student=student,
                exam=exam,
                defaults={'score': score}
            )

        return redirect('subject_detail', subject_id=subject_id)

    # Prepare grades as tuples like insert_grade does
    quiz_grades = []
    for quiz in quizzes:
        grade = Grade.objects.filter(student=student, quiz=quiz).first()
        quiz_grades.append((quiz, grade.score if grade else ''))

    activity_grades = []
    for activity in activities:
        grade = Grade.objects.filter(student=student, activity=activity).first()
        activity_grades.append((activity, grade.score if grade else ''))

    exam_grades = []
    for exam in exams:
        grade = Grade.objects.filter(student=student, exam=exam).first()
        exam_grades.append((exam, grade.score if grade else ''))

    return render(request, 'core/insert_grade.html', {
    'subject': subject,
    'student': student,
    'quiz_grades': quiz_grades,
    'activity_grades': activity_grades,
    'exam_grades': exam_grades,
    'is_editing': True  # 👈 Add this line
})


def quiz_add(request, subject_id):
    if request.method == 'POST':
        data = {
            'title': request.POST.get('title', ''),
            'subject': subject_id
        }
        response = requests.post(f'{API_URL}/quizzes/', json=data, headers=HEADERS)
        if response.status_code in [200, 201]:
            return redirect('subject_detail', subject_id=subject_id)
        return render(request, 'core/assessment_form.html', {'type': 'Quiz', 'error': 'Failed to add quiz'})
    return render(request, 'core/assessment_form.html', {'type': 'Quiz'})

def activity_add(request, subject_id):
    if request.method == 'POST':
        data = {
            'title': request.POST.get('title', ''),
            'subject': subject_id
        }
        response = requests.post(f'{API_URL}/activities/', json=data, headers=HEADERS)
        if response.status_code in [200, 201]:
            return redirect('subject_detail', subject_id=subject_id)
        return render(request, 'core/assessment_form.html', {'type': 'Activity', 'error': 'Failed to add activity'})
    return render(request, 'core/assessment_form.html', {'type': 'Activity'})

def exam_add(request, subject_id):
    if request.method == 'POST':
        data = {
            'title': request.POST.get('title', ''),
            'subject': subject_id
        }
        response = requests.post(f'{API_URL}/exams/', json=data, headers=HEADERS)
        if response.status_code in [200, 201]:
            return redirect('subject_detail', subject_id=subject_id)
        return render(request, 'core/assessment_form.html', {'type': 'Exam', 'error': 'Failed to add exam'})
    return render(request, 'core/assessment_form.html', {'type': 'Exam'})


class EditGradeView(UpdateView):
    model = Grade
    form_class = GradeForm
    template_name = 'core/edit_grade.html'

    def get_success_url(self):
        return reverse_lazy('subject_list')


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer

class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer

class ActivityViewSet(viewsets.ModelViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer

class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer

class GradeViewSet(viewsets.ModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
