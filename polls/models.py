"""Model for django poll."""
from django.db import models
# from django.db.models.base import Model
import datetime
from django.utils import timezone
from django.contrib.auth.models import User


class Question(models.Model):
    """Class that contain question of the user."""

    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    end_date = models.DateTimeField('date expired')

    def __str__(self):
        """Return question text in string."""
        return self.question_text

    def was_published_recently(self):
        """Return how long has the question published."""
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    def is_published(self):
        """Return True if current date is on or after question publication date."""
        if self.pub_date <= timezone.now():
            return True

    def can_vote(self):
        """Return True if voting is currently allowed for the question."""
        if self.pub_date <= timezone.now() < self.end_date:
            return True

    was_published_recently.admin_order_field = 'pub_date'
    was_published_recently.boolean = True
    was_published_recently.short_description = 'Published recently?'


class Choice(models.Model):
    """Class that contain choice for user to choose to answer the question."""

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    # votes = models.IntegerField(default=0)

    def __str__(self):
        """Return choice text in string."""
        return self.choice_text

    # we want to be able to  write 'choice.votes' in our views
    # and templates to get the number of votes for a Choice.
    # We want the existing code to still work.
    @property
    def votes(self):
        count = Vote.objects.filter(choice=self).count()
        return count


class Vote(models.Model):
    """Specify id."""
    user = models.ForeignKey(
        User,
        null=False,
        blank=False,
        on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)

    def __str__(self):
        return f"Vote by {self.user} for {self.choice.choice_text} on question {self.choice.question}."

