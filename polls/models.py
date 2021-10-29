"""The Polls app main model."""
import datetime

from django.db import models
from django.utils import timezone

from django.contrib.auth.models import User


class Question(models.Model):
    """Question model class."""

    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    end_date = models.DateTimeField('deadline', null=True)

    def was_published_recently(self):
        """Check if the question was published recently."""
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    def is_published(self):
        """Check if the question is already published."""
        now = timezone.now()
        return self.pub_date <= now

    def can_vote(self):
        """Check if the question is can vote or not."""
        now = timezone.now()
        if self.pub_date <= now and not self.end_date:
            return True
        elif self.pub_date <= now < self.end_date:
            return True
        else:
            return False

    def __str__(self):
        """Return question text."""
        return self.question_text

    was_published_recently.admin_order_field = 'pub_date'
    was_published_recently.boolean = True
    was_published_recently.short_description = 'Published recently?'


class Choice(models.Model):
    """Choice model class."""

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    # votes = models.IntegerField(default=0)

    def __str__(self):
        """Return choice text."""
        return self.choice_text

    @property
    def votes(self) -> int:
        """Return votes count."""
        count = Votes.objects.filter(choice=self).count()
        return count


class Votes(models.Model):
    """Vote one per id."""

    # id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)

    def __str__(self):
        """Display vote by user."""
        return f"Vote by {self.user.username} for {self.choice.choice_text}"
