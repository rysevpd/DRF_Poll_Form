from rest_framework import serializers
from rest_framework.serializers import Serializer
from rest_framework.serializers import ValidationError


def type_qestion(val):
    types = ['text', 'one_answer', 'multiple_answer']
    if val not in types:
        raise ValidationError('Данного типа не существует')


class PollSerializer(Serializer):
    id = serializers.IntegerField(required=False)
    name_test = serializers.CharField(max_length=50)
    about_test = serializers.CharField(max_length=225)
    date_start = serializers.CharField()
    date_finish = serializers.CharField()


class QuestionSerializer(Serializer):
    id = serializers.IntegerField(required=False)
    type = serializers.CharField(max_length=30, validators=[type_qestion])
    text = serializers.CharField(max_length=500)


class AnswerOptionSerializer(Serializer):
    id = serializers.IntegerField(required=False)
    index = serializers.IntegerField(required=False)
    text = serializers.CharField(max_length=150)


class OptionSerializer(Serializer):
    id = serializers.IntegerField()
    text = serializers.CharField(max_length=100)


class CompletedTestSerializer(Serializer):
    id = serializers.IntegerField()
    time_end = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S')