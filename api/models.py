from django.db import models
from django.contrib.auth.models import User

class UserMovie(models.Model):
    STATUS_CHOICES = (
        ('WATCH_LATER', 'Watch Later'),
        ('WATCHED', 'Watched'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='movies')
    movie_id = models.IntegerField()
    title = models.CharField(max_length=255)
    poster_path = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'movie_id')

    def __str__(self):
        return f"{self.user.username} - {self.title} ({self.status})"
