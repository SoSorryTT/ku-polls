"""Unittest for the poll."""
from django.test import TestCase
import datetime
from django.utils import timezone
from polls.models import Question
from django.urls import reverse


class QuestionModelTests(TestCase):
    """Unittest that test question."""

    def test_was_published_recently_with_future_question(self):
        """was_published_recently() returns False for questions whose pub_date is in the future."""
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """was_published_recently() returns False for questions whose pub_date is older than 1 day."""
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """was_published_recently() returns True for questions whose pub_date is within the last day."""
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

    def test_is_published_work_correctly(self):
        """is_published() return True for current date is on or after question publication date."""
        question = create_question(question_text='Test question.', days=0, ends_date=30)
        self.assertEqual(True, question.is_published())

    def test_is_published_with_old_question(self):
        """is_published() return True for the question which already create."""
        question = create_question(question_text='Test question.', days=-1, ends_date=30)
        self.assertEqual(True, question.is_published())

    def test_is_published_with_future_question(self):
        """is_published() return None for the question which create in the future."""
        question = create_question(question_text='Test question.', days=1, ends_date=30)
        self.assertEqual(None, question.is_published())

    def test_can_vote_work_correctly(self):
        """can_vote() return True if voting is currently allowed for the question."""
        question = create_question(question_text='Test question.', days=0, ends_date=30)
        self.assertEqual(True, question.can_vote())

    def test_can_vote_with_not_published_question(self):
        """can_vote() return None for not published question."""
        question = create_question(question_text='Test question.', days=1, ends_date=30)
        self.assertEqual(None, question.can_vote())
        question = create_question(question_text='Test question.', days=10, ends_date=30)
        self.assertEqual(None, question.can_vote())

    def test_can_vote_with_ended_question(self):
        """can_vote() return None for ended question."""
        question = create_question(question_text='Test question.', days=1, ends_date=0)
        self.assertEqual(None, question.can_vote())
        question = create_question(question_text='Test question.', days=10, ends_date=-1)
        self.assertEqual(None, question.can_vote())


def create_question(question_text, days, ends_date=30):
    """Create a question.

    With the given `question_text` and published the given number of `days`
    offset to now (negative for questions published in the past, positive for questions
    that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    ends = timezone.now() + datetime.timedelta(days=ends_date)
    return Question.objects.create(question_text=question_text, pub_date=time, end_date=ends)


class QuestionIndexViewTests(TestCase):
    """Test question view."""

    def test_no_questions(self):
        """If no questions exist, an appropriate message is displayed."""
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """Questions with a pub_date in the past are displayed on the index page."""
        create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_future_question(self):
        """Questions with a pub_date in the future aren't displayed on the index page."""
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        """Even if both past and future questions exist, only past questions are displayed."""
        create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_two_past_questions(self):
        """The questions index page may display multiple questions."""
        create_question(question_text="Past question 1.", days=-30)
        create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question 2.>', '<Question: Past question 1.>']
        )


class QuestionDetailViewTests(TestCase):
    """Test question that make in the future and past."""

    def test_future_question(self):
        """The detail view of a question with a pub_date in the future returns a 404 not found."""
        future_question = create_question(question_text='Future question.', days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """The detail view of a question with a pub_date in the past displays the question's text."""
        past_question = create_question(question_text='Past Question.', days=-5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
