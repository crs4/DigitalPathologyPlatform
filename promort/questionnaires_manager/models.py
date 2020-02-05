#  Copyright (c) 2019, CRS4
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of
#  this software and associated documentation files (the "Software"), to deal in
#  the Software without restriction, including without limitation the rights to
#  use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
#  the Software, and to permit persons to whom the Software is furnished to do so,
#  subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
#  FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
#  COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
#  IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
#  CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from slides_manager.models import SlidesSet


class QuestionsSet(models.Model):
    label = models.CharField(max_length=20, blank=False, unique=True)
    questions_json = models.TextField(blank=False)
    creation_date = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.PROTECT, blank=False)


class Questionnaire(models.Model):
    label = models.CharField(max_length=20, blank=False, unique=True)
    creation_date = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.PROTECT, blank=False)

    @property
    def steps_count(self):
        return self.steps.count()

    def get_step(self, step_index):
        try:
            return self.steps.get(step_index=step_index)
        except QuestionnaireStep.DoesNotExist:
            return None

    def get_last_used_index(self):
        last_step = self.steps.order_by('-creation_date').first()
        try:
            return last_step.step_index
        except AttributeError:
            return -1


class QuestionnaireStep(models.Model):
    questions = models.ForeignKey(QuestionsSet, on_delete=models.PROTECT, blank=False)
    slides_set_a = models.ForeignKey(SlidesSet, on_delete=models.PROTECT, blank=True, null=True,
                                     default=None, related_name='slides_set_a')
    slides_set_a_label = models.CharField(max_length=20, blank=True, null=True, default=None)
    slides_set_b = models.ForeignKey(SlidesSet, on_delete=models.PROTECT, blank=True, null=True,
                                     default=None, related_name='slides_set_b')
    slides_set_b_label = models.CharField(max_length=20, blank=True, null=True, default=None)
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.PROTECT, blank=False,
                                      related_name='steps')
    step_index = models.IntegerField(blank=False)
    creation_date = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('questionnaire', 'step_index')


class QuestionnaireRequest(models.Model):
    label = models.CharField(unique=True, blank=False, null=False, max_length=40)
    questionnaire_panel_a = models.ForeignKey(Questionnaire, on_delete=models.PROTECT, blank=False,
                                              null=False, related_name='panel_a_steps')
    questionnaire_panel_b = models.ForeignKey(Questionnaire, on_delete=models.PROTECT, blank=True,
                                              null=True, default=None, related_name='panel_b_steps')
    reviewer = models.ForeignKey(User, on_delete=models.PROTECT, blank=False, null=False)
    creation_date = models.DateTimeField(default=timezone.now)
    start_date = models.DateTimeField(blank=True, null=True, default=None)
    completion_date = models.DateTimeField(blank=True, null=True, default=None)

    def is_started(self):
        return not(self.start_date is None)

    def is_completed(self):
        return not(self.completion_date is None)

    def can_be_closed(self):
        close = True
        for a in self.answers.all():
            if not a.is_completed():
                close = False
        return close


class QuestionnaireAnswers(models.Model):
    questionnaire_request = models.ForeignKey(QuestionnaireRequest, on_delete=models.PROTECT, blank=False,
                                              related_name='answers')
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.PROTECT, blank=False, null=False,
                                      related_name='answers')
    reviewer = models.ForeignKey(User, on_delete=models.PROTECT, blank=False, null=False, default=None)
    creation_date = models.DateTimeField(auto_now_add=True)
    completion_date = models.DateTimeField(blank=True, null=True, default=None)

    class Meta:
        unique_together = ('questionnaire_request', 'questionnaire')

    def is_started(self):
        return self.questionnaire_request.is_started()

    def is_completed(self):
        return not(self.completion_date is None)

    def can_be_closed(self):
        return self.steps_count == self.completed_steps_count

    def get_questionnaire_step(self, step_index):
        return self.questionnaire.get_step(step_index)

    def get_last_completed_step_index(self):
        last_step = self.steps.order_by('-creation_date').first()
        try:
            return last_step.step_index
        except AttributeError:
            return -1

    @property
    def steps_count(self):
        return self.questionnaire.steps_count

    @property
    def completed_steps_count(self):
        return self.steps.count()


class QuestionnaireStepAnswers(models.Model):
    questionnaire_answers = models.ForeignKey(QuestionnaireAnswers, on_delete=models.PROTECT, blank=False,
                                              null=False, related_name='steps')
    questionnaire_step = models.ForeignKey(QuestionnaireStep, on_delete=models.PROTECT, blank=False,
                                           null=False, related_name='answers')
    answers_json = models.TextField(blank=False)
    creation_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('questionnaire_answers', 'questionnaire_step')

    @property
    def step_index(self):
        return self.questionnaire_step.step_index
