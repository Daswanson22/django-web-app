import datetime

from django.db import models
from django.utils import timezone
from django.contrib import admin

class Question(models.Model):
    def __str__(self):
        return self.question_text + self.pub_date.strftime("%Y-%m-%d %H:%M:%S") + str(self.total_votes)
    
    @admin.display(
        boolean=True,
        ordering="pub_date",
        description="Published recently?",
    )
    def was_published_recently(self):
        now = timezone.now()
        # Check if the published date is within the last day
        return now - datetime.timedelta(days=1) <= self.pub_date <= now
    
    @admin.display(
            boolean=True,
            ordering="pub_date",
            description="Published?",
    )
    def is_published(self):
        now = timezone.now()
        return self.pub_date <= now
    
    def update_votes(self):
        self.total_votes = self.choice_set.aggregate(total_votes=models.Sum("votes"))["total_votes"]
        self.save()

    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")
    total_votes = models.IntegerField(default=0)


class Choice(models.Model):
    def __str__(self):
        return self.choice_text
    
    def votes_count(self):
        return self.votes

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)