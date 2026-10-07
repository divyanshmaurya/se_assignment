import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Question


def create_question(question_text, days=0):
    """Create a question published the given number of `days` from now."""
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionModelTests(TestCase):
    def test_was_published_recently_with_recent_question(self):
        question = create_question("Recent question.", days=0)
        self.assertIs(question.was_published_recently(), True)

    def test_was_published_recently_with_old_question(self):
        question = create_question("Old question.", days=-2)
        self.assertIs(question.was_published_recently(), False)


class PollsViewTests(TestCase):
    def setUp(self):
        self.question = create_question("What's up?", days=-1)
        self.choice = self.question.choice_set.create(choice_text="Not much")

    def test_root_redirects_to_polls_index(self):
        response = self.client.get("/")
        self.assertRedirects(response, reverse("polls:index"))

    def test_index_lists_questions(self):
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "What&#x27;s up?")

    def test_index_without_questions(self):
        Question.objects.all().delete()
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available.")

    def test_detail_shows_choices(self):
        response = self.client.get(reverse("polls:detail", args=(self.question.id,)))
        self.assertContains(response, "Not much")

    def test_detail_unknown_question_404(self):
        response = self.client.get(reverse("polls:detail", args=(999,)))
        self.assertEqual(response.status_code, 404)

    def test_vote_counts_and_redirects_to_results(self):
        response = self.client.post(
            reverse("polls:vote", args=(self.question.id,)),
            {"choice": self.choice.id},
        )
        self.assertRedirects(response, reverse("polls:results", args=(self.question.id,)))
        self.choice.refresh_from_db()
        self.assertEqual(self.choice.votes, 1)
        response = self.client.get(reverse("polls:results", args=(self.question.id,)))
        self.assertContains(response, "Not much -- 1 vote")

    def test_vote_without_choice_shows_error(self):
        response = self.client.post(reverse("polls:vote", args=(self.question.id,)))
        self.assertContains(response, "You didn&#x27;t select a choice.")
