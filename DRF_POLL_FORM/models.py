from django.db import models
from django.db.models import Model
from django.core.exceptions import ValidationError


def type_question(val):
    types = ['text', 'one_answer', 'multiple_answer']
    if val not in types:
        raise ValidationError('Данного типа не существует')


type_choice = ['one_answer', 'multiple_answer']


class Poll(Model):
    name_test = models.CharField(max_length=50)
    about_test = models.CharField(max_length=225)
    date_start = models.DateField()
    date_finish = models.DateField()


class Question(Model):
    question = models.ForeignKey('Poll', on_delete=models.CASCADE)
    type = models.CharField(max_length=25, validators=[type_question])
    text = models.CharField(max_length=500)

    @property
    def type_choices(self):
        return self.type in type_choice


class AnswerOption(Model):
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    uuid = models.PositiveIntegerField()
    text = models.CharField(max_length=150)


class CompletedTest(Model):
    id_user = models.IntegerField(db_index=True)
    poll = models.ForeignKey('Poll', on_delete=models.CASCADE)
    time_end = models.DateTimeField(auto_now_add=True)


class Answer(Model):
    completed = models.ForeignKey('CompletedTest', on_delete=models.CASCADE)
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    text_question = models.CharField(max_length=500)
    type_question = models.CharField(max_length=25, validators=[type_question])
    user_answer = models.CharField(max_length=150)