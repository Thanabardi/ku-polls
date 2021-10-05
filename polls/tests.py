"""Test case for polls app."""
import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question


def create_question(question_text, pub_days, end_days):
    """
    Create a question.

    Args:
        question_text: question text.
        pub_days: publish day of the question.
        end_days: end day of the question.

    Returns:
        question object.
    """
    pub_time = timezone.now() + datetime.timedelta(days=pub_days)
    end_time = timezone.now() + datetime.timedelta(days=end_days)
    return Question.objects.create(question_text=question_text, pub_date=pub_time, end_date=end_time)


class ViewTests(TestCase):
    """Test case in view."""

    def test_no_questions(self):
        """If no questions exist, an appropriate message is displayed."""
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['question_list'], [])

    def test_past_question(self):
        """Questions with a pub_date in the past are displayed on the index page."""
        question = create_question(question_text="Past question.", pub_days=-1, end_days=1)
        question.save()
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['question_list'],
            ['<Question: Past question.>']
        )

    def test_future_question(self):
        """Questions with a pub_date in the future aren't displayed on the index page."""
        question = create_question(question_text="Future question.", pub_days=1, end_days=2)
        question.save()
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['question_list'], [])

    def test_future_question_and_past_question(self):
        """Even if both past and future questions exist, only past questions are displayed."""
        past_question = create_question(question_text="Past question.", pub_days=-1, end_days=1)
        past_question.save()
        future_question = create_question(question_text="Future question.", pub_days=1, end_days=2)
        future_question.save()
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['question_list'],
            ['<Question: Past question.>']
        )

    def test_two_past_questions(self):
        """The questions index page may display multiple questions."""
        past_question_1 = create_question(question_text="Past question 1.", pub_days=-2, end_days=1)
        past_question_1.save()
        past_question_2 = create_question(question_text="Past question 2.", pub_days=-1, end_days=1)
        past_question_2.save()
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['question_list'],
            ['<Question: Past question 2.>', '<Question: Past question 1.>']
        )


class QuestionDetailViewTests(TestCase):
    """Test for question detail view."""

    def test_future_question(self):
        """The detail view of a question with a pub_date in the future returns a 404 not found."""
        future_question = create_question(question_text="Future question 2.", pub_days=1, end_days=2)
        future_question.save()
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """The detail view of a question with a pub_date in the past displays the question's text."""
        past_question = create_question(question_text="Past question 2.", pub_days=-2, end_days=1)
        past_question.save()
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)


class QuestionTests(TestCase):
    """Test for question."""

    def test_was_published_recently(self):
        """Test was_published_recently medthod."""
        time = timezone.now() + datetime.timedelta(days=1)
        question = Question(question_text="the day after pub date.", pub_date=time)
        self.assertFalse(question.was_published_recently())
        # current date is 1 day before publication date

        time = timezone.now()
        question = Question(question_text="the day within pub date.", pub_date=time)
        self.assertTrue(question.was_published_recently())
        # current date is on publication date

        time = timezone.now() + datetime.timedelta(minutes=-1)
        question = Question(question_text="1 minute before pub date.", pub_date=time)
        self.assertTrue(question.was_published_recently())
        # current time is 1 minure after publication date

        time = timezone.now() + datetime.timedelta(days=-1)
        question = Question(question_text="the day before pub date.", pub_date=time)
        self.assertTrue(question.was_published_recently())
        # current date is 1 day after publication date

        time = timezone.now() + datetime.timedelta(days=-5)
        question = Question(question_text="5 days before pub date.", pub_date=time)
        self.assertFalse(question.was_published_recently())
        # current date is 5 days after publication date

    def test_is_published(self):
        """Test is_published medthod."""
        time = timezone.now() + datetime.timedelta(days=1)
        question = Question(question_text='the day before pub date.', pub_date=time)
        self.assertFalse(question.is_published())
        # current date is before publication date

        time = timezone.now()
        question = Question(question_text='the day within pub date.', pub_date=time)
        self.assertTrue(question.is_published())
        # current date is on publication date

        time = timezone.now() + datetime.timedelta(days=-1)
        question = Question(question_text='the day after pub date.', pub_date=time)
        self.assertTrue(question.is_published())
        # current date is after publication date

    def test_can_vote(self):
        """Test can_vote medthod."""
        pub_time = timezone.now() + datetime.timedelta(days=1)
        end_time = timezone.now() + datetime.timedelta(days=2)
        question = Question(question_text="the day before pub date.", pub_date=pub_time, end_date=end_time)
        self.assertFalse(question.can_vote())
        # current date is 1 days before publication date

        pub_time = timezone.now() + datetime.timedelta(days=-1)
        end_time = timezone.now() + datetime.timedelta(days=1)
        question = Question(question_text="the day between pub date and end date.",
                            pub_date=pub_time, end_date=end_time)
        self.assertTrue(question.can_vote())
        # current date is between pub date and end date

        pub_time = timezone.now() + datetime.timedelta(days=-2)
        end_time = timezone.now() + datetime.timedelta(days=-1)
        question = Question(question_text="the day after end date.", pub_date=pub_time, end_date=end_time)
        self.assertFalse(question.can_vote())
        # current time is 1 day after end date

        pub_time = timezone.now() + datetime.timedelta(days=-1)
        question = Question(question_text="the day after pub date without end date.", pub_date=pub_time)
        self.assertTrue(question.can_vote())
        # current time is pass pub date without end date
