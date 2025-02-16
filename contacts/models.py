from django.db import models


class Contact(models.Model):
    id = models.BigIntegerField(primary_key=True)  # Use BigIntegerField for large IDs
    name = models.CharField(max_length=100)
    company = models.CharField(max_length=100, blank=True)
    card1 = models.CharField(max_length=100, blank=True)
    card2 = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'contacts'  # Specify the custom table name here

class PendingChange(models.Model):
    query = models.TextField()  # The SQL query to be executed
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pending Change: {self.query[:50]}..."
    
