from rest_framework import serializers
from .models import Student, Subject, Quiz, Activity, Exam, Grade

class NestedSubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'code']

class SubjectSerializer(serializers.ModelSerializer):
    students = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Student.objects.all()
    )

    class Meta:
        model = Subject
        fields = ['id', 'name', 'code', 'students']


class StudentSerializer(serializers.ModelSerializer):
    subjects = NestedSubjectSerializer(many=True, read_only=True)

    class Meta:
        model = Student
        fields = '__all__'



class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = '__all__'

class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = '__all__'

class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = '__all__'

class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = '__all__'
