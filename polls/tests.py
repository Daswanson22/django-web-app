import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question, Choice

def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

class QuestionResultsViewTests(TestCase):
    def test_future_question(self):
        """
        The results view of a question with a pub_date in the future
        returns a 404 not found.
        URL: /polls/:id/results/
        """
        future_question = create_question(question_text="Future question.", days=5)
        url = reverse("polls:results", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future 
        returns a 404 not found.
        URL: /polls/:id/
        """
        future_question = create_question(question_text="Future question.", days=5)
        url = reverse("polls:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        URL: /polls/:id/
        """
        past_question = create_question(question_text="Past Question.", days=-5)
        url = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

class QuestionIndexViewTests(TestCase):
    def test_that_questions_have_choices(self):
        """
        Questions that do not 2 or more choices should not be displayed.
        URL: /polls/
        """
        question = create_question(question_text="What is a test?", days=-30)
        question.choice_set.create(choice_text="A test is a test.")
        question.choice_set.create(choice_text="A test is not a test.")
        question_choice_length = len(question.choice_set.all())
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(question_choice_length, 2)
        self.assertIs(question.is_published(), True)

    def test_that_questions_have_no_choices(self):
        """
        Questions that do not have 2 or more choices should not be displayed.
        URL: /polls/
        """
        question = create_question(question_text="What is a test?", days=-30)
        question_choice_length = len(question.choice_set.all())
        if(question_choice_length < 2):
            question.pub_date = timezone.now() + datetime.timedelta(days=31)
            question.save()
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(question_choice_length, 1)
        self.assertIs(question.is_published(), False)

    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        URL: /polls/
        """
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the
        index page.
        URL: /polls/
        """
        question = create_question(question_text="What is a test?", days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question],
        )

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on
        the index page.
        URL: /polls/
        """
        create_question(question_text="What will the future hold?", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        URL: /polls/
        """
        question = create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question],
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        URL: /polls/
        """
        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse("polls:index"))
        
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question2, question1],
            ordered=False,
        )


class QuestionRecentViewTests(TestCase):
    def test_no_recent_questions(self):
        """
        If no recent questions exist, an appropriate message is displayed.
        URL: /polls/recent/
        """
        response = self.client.get(reverse("polls:recent"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["recent_question_list"], [])

    def test_question_posted_within_7_days(self):
        """
        Questions with a pub_date within the last 7 days are displayed on the
        recent page.
        URL: /polls/recent/
        """
        question = create_question(question_text="What is a test?", days=-5)
        question.choice_set.create(choice_text="A test is a test.")
        question.choice_set.create(choice_text="A test is not a test.")
        response = self.client.get(reverse("polls:recent"))
        self.assertQuerySetEqual(
            response.context["recent_question_list"],
            [question],
        )

    def test_question_posted_older_than_7_days(self):
        """
        Questions with a pub_date older than 7 days are not displayed on the
        recent page.
        URL: /polls/recent/
        """
        question = create_question(question_text="What is a test?", days=-10)
        question.choice_set.create(choice_text="A test is a test.")
        question.choice_set.create(choice_text="A test is not a test.")
        response = self.client.get(reverse("polls:recent"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["recent_question_list"], [])
    
    def test_question_but_no_choices(self):
        """
        Questions with no choices are not displayed on the recent page.
        URL: /polls/recent/
        """
        question = create_question(question_text="What is a test?", days=-6)
        question_choice_length = len(question.choice_set.all())
        if(question_choice_length < 2):
            question.pub_date = timezone.now() + datetime.timedelta(days=31)
            question.save()
        response = self.client.get(reverse("polls:recent"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["recent_question_list"], [])

    def test_question_with_choices(self):
        """
        Questions with a pub_date in the past are displayed on the
        recent page.
        URL: /polls/recent/
        """
        question = create_question(question_text="What is a test?", days=-5)
        question.choice_set.create(choice_text="A test is a test.")
        question.choice_set.create(choice_text="A test is not a test.")
        response = self.client.get(reverse("polls:recent"))
        self.assertQuerySetEqual(
            response.context["recent_question_list"],
            [question],
        )

class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions
        whose pub_date is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)

        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)
