from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ParseError
from rest_framework import authentication, permissions
from django.http import Http404

from datetime import date

from .models import Poll, Question, AnswerOption, type_question
from .serializers import PollSerializer, QuestionSerializer, OptionSerializer


class AdminAPIView(APIView):
    authentication_classes = [authentication.BasicAuthentication]
    permission_classes = [permissions.IsAdminUser]


class AdminPolls(AdminAPIView):
    def get(self, request):
        return Response(PollSerializer(Poll.objects.all(), many=True).data)

    def post(self, request):
        try:
            s = PollSerializer(data=request.data)
            s.is_valid(raise_exception=True)
            d = s.validated_data
            if d['date_start'] > d['date_finish']:
                raise Exception('Invalid finishDate')

            new_poll = Poll(**d)
            new_poll.save()
            return Response(PollSerializer(new_poll).data)
        except Exception as ex:
            raise ParseError(ex)


class AdminPollById(AdminAPIView):
    def get(self, request, id):
        try:
            poll = Poll.objects.get(id=id)
            result = PollSerializer(poll).data
            result['questions'] = []
            for question in poll.question_set.all():
                questionDict = QuestionSerializer(question).data
                if question.hasOptionType:
                    questionDict['answeroptions'] = OptionSerializer(question.option_set.all(), many=True).data
                result['questions'].append(questionDict)

            return Response(result)

        except Poll.DoesNotExist:
            raise Http404()
        except Exception as ex:
            raise ParseError(ex)

    def delete(self, request, id):
        try:
            Poll.objects.get(id=id).delete()
            return Response('Deleted')
        except Poll.DoesNotExist:
            raise Http404()
        except Exception as ex:
            raise ParseError(ex)

    def patch(self, request, id):
        try:
            poll = Poll.objects.get(id=id)
            d = request.data
            if 'name_test' in d:
                poll.name = d['name_test']
            if 'about_test' in d:
                poll.description = d['about_test']
            if 'date_finish' in d:
                poll.finishDate = date.fromisoformat(d['date_finish'])

            if poll.startDate > poll.finishDate:
                raise Exception('Invalid finishDate')

            poll.save()
            return Response(PollSerializer(poll).data)

        except Poll.DoesNotExist:
            raise Http404()
        except Exception as ex:
            raise ParseError(ex)


class AdminQuestions(AdminAPIView):
    def post(self, request, id):
        try:
            poll = Poll.objects.get(id=id)
            qs = QuestionSerializer(data=request.data)
            qs.is_valid(raise_exception=True)
            pd = dict(qs.validated_data)
            pd['poll'] = poll
            newQuestion = Question(**pd)

            requireOptions = newQuestion.type_choices
            newOptionList = []
            if requireOptions:
                if not 'answeroptions' in request.data:
                    raise Exception('options are missing')
                if type(request.data['answeroptions']) != list or len(request.data['options']) < 2:
                    raise Exception('Invalid options')

                index = 1
                for optionText in request.data['answeroptions']:
                    newOptionList.append(AnswerOption(
                        text=optionText,
                        index=index
                    ))
                    index += 1

            newQuestion.save()
            if requireOptions:
                for newOption in newOptionList:
                    newOption.question = newQuestion
                    newOption.save()

            result = QuestionSerializer(newQuestion).data
            if requireOptions:
                result['answeroptions'] = [OptionSerializer(o).data for o in newOptionList]

            return Response(result)

        except Poll.DoesNotExist:
            raise Http404()
        except Exception as ex:
            raise ParseError(ex)


class AdminQuestionById(AdminAPIView):
    def get(self, request, pollId, questionId):
        try:
            question = Question.objects.get(id=questionId)
            result = QuestionSerializer(question).data
            if question.hasOptionType:
                result['answeroptions'] = OptionSerializer(question.option_set.all(), many=True)
            return Response(result)

        except Question.DoesNotExist:
            raise Http404()
        except Exception as ex:
            raise ParseError(ex)

    def delete(self, request, pollId, questionId):
        try:
            Question.objects.get(id=questionId).delete()
            return Response('Deleted')
        except Question.DoesNotExist:
            raise Http404()
        except Exception as ex:
            raise ParseError(ex)

    def patch(self, request, pollId, questionId):
        try:
            deleteExistingOptions = False
            requireNewOptions = False
            prevQuestion = Question.objects.get(id=questionId)
            nextQuestion = Question.objects.get(id=questionId)
            d = request.data
            if 'text' in d:
                nextQuestion.text = d['text']
            if 'type' in d:
                type_question(d['type'])
                nextQuestion.type = d['type']

            if prevQuestion.hasOptionType and not nextQuestion.hasOptionType:
                deleteExistingOptions = True
            if not prevQuestion.hasOptionType and nextQuestion.hasOptionType:
                requireNewOptions = True
            if prevQuestion.hasOptionType and nextQuestion.hasOptionType and 'answeroptions' in d:
                deleteExistingOptions = requireNewOptions = True

            if requireNewOptions:
                if not 'answeroptions' in d:
                    raise Exception('options are missing')
                if type(d['answeroptions']) != list or len(d['answeroptions']) < 2:
                    raise Exception('Invalid options')

            if deleteExistingOptions:
                AnswerOption.objects.filter(question=nextQuestion).delete()

            if requireNewOptions:
                index = 1
                for optionText in d['answeroptions']:
                    AnswerOption(text=optionText, index=index, question=nextQuestion).save()
                    index += 1

            nextQuestion.save()

            result = QuestionSerializer(nextQuestion).data
            if nextQuestion.hasOptionType:
                result['answeroptions'] = OptionSerializer(nextQuestion.option_set.all(), many=True).data

            return Response(result)

        except Question.DoesNotExist:
            raise Http404()
        except Exception as ex:
            raise ParseError(ex)