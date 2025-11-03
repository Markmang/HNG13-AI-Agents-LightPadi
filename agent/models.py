from django.db import models

from django.db import models

class PowerReport(models.Model):
    location = models.CharField(max_length=100)
    status = models.CharField(max_length=10)  # "on" or "off"
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.location} - {self.status} ({self.timestamp})"
