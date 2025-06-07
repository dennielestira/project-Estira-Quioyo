from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

# REST API routing
router = DefaultRouter()
router.register('students', StudentViewSet)
router.register('subjects', SubjectViewSet)
router.register('quizzes', QuizViewSet)
router.register('activities', ActivityViewSet)
router.register('exams', ExamViewSet)
router.register('grades', GradeViewSet)

urlpatterns = [
    # Home page
    path('', base, name='base'),  # Home page URL

    # API endpoints (as before)
    path('api/', include(router.urls)),

    # Template views using REST API
    path('students/', student_list, name='student_list'),
    path('students/add/', student_add, name='student_add'),
    path('students/<int:student_id>/edit/', student_edit, name='student_edit'),
    path('students/<int:student_id>/delete/', student_delete, name='student_delete'),

    path('subjects/', subject_list, name='subject_list'),
    path('subjects/add/', subject_add, name='subject_add'),
    path('subjects/<int:subject_id>/', subject_detail, name='subject_detail'),
    path('subjects/<int:subject_id>/edit/', subject_edit, name='subject_edit'),
    path('subjects/<int:subject_id>/delete/', subject_delete, name='subject_delete'),

    path('subjects/<int:subject_id>/add_quiz/', quiz_add, name='quiz_add'),
    path('subjects/<int:subject_id>/add_activity/', activity_add, name='activity_add'),
    path('subjects/<int:subject_id>/add_exam/', exam_add, name='exam_add'),

    path('grades/<str:assessment_type>/<int:assessment_id>/', grade_insert, name='grade_insert'),
    path('subjects/<int:subject_id>/student/<int:student_id>/insert/', insert_grade, name='insert_grade'),
    path('subjects/<int:subject_id>/student/<int:student_id>/edit/', edit_grade, name='edit_grade'),
]