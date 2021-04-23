from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ParseError
from django.http import Http404
from datetime import date
import json

from .models import Poll, CompletedTest, Answer
from .serializers import PollSerializer, QuestionSerializer, OptionSerializer, CompletedTestSerializer


class Polls(APIView):
    def get(self, request):
        today = date.today()
        pollSet = Poll.objects.filter(date_start__lte=today, date_finish__gt=today)
        return Response(PollSerializer(pollSet, many=True).data)


class PollById(APIView):
    def get(self, request, id):
        try:
            today = date.today()
            poll = Poll.objects.get(id=id)
            if poll.date_start > today or poll.date_finish < today:
                raise Poll.DoesNotExist()

            result = PollSerializer(poll).data
            result['questions'] = []
            for question in poll.question_set.all():
                questionDict = QuestionSerializer(question).data
                if question.type_choices:
                    questionDict['options'] = OptionSerializer(question.answeroption_set.all(), many=True).data
                result['questions'].append(questionDict)

            return Response(result)

        except Poll.DoesNotExist:
            raise Http404()
        except Exception as ex:
            raise ParseError(ex)

    def post(self, request, id):
        try:
            today = date.today()
            poll = Poll.objects.get(id=id)
            if poll.date_start > today or poll.date_finish < today:
                raise Poll.DoesNotExist()

            if not 'id_user' in request.data:
                raise Exception('id_user is missing')
            if not type(request.data['id_user']) is int:
                raise Exception('Invalid id_user')
            if not 'answers' in request.data:
                raise Exception('answers are missing')
            if not type(request.data['answers']) is dict:
                raise Exception('Invalid answers')

            id_user = request.data['id_user']
            answerDict = request.data['answers']

            if CompletedTest.objects.filter(id_user=id_user, poll=poll).count() > 0:
                raise Exception('This user already has submitted to this poll')

            def makeAnswer(question):
                if not str(question.id) in answerDict:
                    raise Exception('Answer to question %d is missing' % question.id)

                answerData = answerDict[str(question.id)]
                answer = Answer(
                    question=question,
                    type_question=question.type,
                    text_question=question.text)

                invalidAnswerException = Exception('Invalid answer to question %d' % question.id)
                invalidIndexException = Exception('Invalid option index in answer to question %d' % question.id)
                if question.type == 'TEXT':
                    if not type(answerData) is str:
                        raise invalidAnswerException
                    answer.user_answer = answerData

                if question.type == 'CHOICE':
                    if not type(answerData) is int:
                        raise invalidAnswerException
                    foundOption = question.answeroption_set.filter(index=answerData).first()
                    if foundOption:
                        answer.user_answer = foundOption.text
                    else:
                        raise invalidIndexException

                if question.type == 'MULTIPLE_CHOICE':
                    if not type(answerData) is list:
                        raise invalidAnswerException
                    optionList = question.answeroption_set.all()
                    resultList = []
                    for index in answerData:
                        foundOption = next((o for o in optionList if o.index == index), None)
                        if foundOption:
                            resultList.append(foundOption.text)
                        else:
                            raise invalidIndexException
                    answer.user_answer = json.dumps(resultList)

                return answer

            answerList = [makeAnswer(question) for question in poll.question_set.all()]
            if len(answerList) != poll.question_set.count():
                raise Exception('Not enough answers')

            submis = CompletedTest(id_user=id_user, poll=poll)
            submis.save()
            for answer in answerList:
                answer.completed = submis
                answer.save()

            return Response('Accepted')

        except Poll.DoesNotExist:
            raise Http404()
        except Exception as ex:
            raise ParseError(ex)


class PollsByUser(APIView):
    def get(self, request, id):
        try:
            result = []
            for completed in CompletedTest.objects.filter(id_user=id).order_by('time_end'):
                completed_list = CompletedTestSerializer(completed).data
                completed_list['pollId'] = completed.poll_id
                completed_list['answers'] = []
                for answer in completed.answer_set.all():
                    user_answer = answer.user_answer
                    if answer.type_question == 'MULTIPLE_CHOICE':
                        user_answer = json.loads(user_answer)

                    completed_list['answers'].append({
                        'question': {
                            'id': answer.question_id,
                            'type': answer.type_question,
                            'text': answer.text_question
                        },
                        'answer': user_answer
                    })

                result.append(completed_list)

            return Response(result)

        except Exception as ex:
            raise ParseError(ex)
