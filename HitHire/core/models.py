# core/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    company = models.CharField(max_length=255, blank=True, null=True)

    # Override the groups and user_permissions fields with unique related_names
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name="custom_user_set",  # Unique related_name
        related_query_name="user"
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="custom_user_set",  # Unique related_name
        related_query_name="user"
    )

class JobDescription(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_descriptions')
    created_at = models.DateTimeField(auto_now_add=True)

class CV(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    gender = models.CharField(max_length=50, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    nationality = models.CharField(max_length=100, blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    degrees = models.CharField(max_length=255, blank=True, null=True)
    college_name = models.CharField(max_length=255, blank=True, null=True)
    designation = models.CharField(max_length=255, blank=True, null=True)
    last_company = models.CharField(max_length=255, blank=True, null=True)
    skills = models.JSONField(default=list, blank=True, null=True)
    total_experience_years = models.IntegerField(default=0)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cvs')
    created_at = models.DateTimeField(auto_now_add=True)

class CandidateRanking(models.Model):
    job_description = models.ForeignKey(JobDescription, on_delete=models.CASCADE, related_name='rankings')
    cv = models.ForeignKey(CV, on_delete=models.CASCADE, related_name='rankings')
    overall_score = models.FloatField(default=0.0)
    recommendation = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class CustomScoring(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    education_weight = models.FloatField(default=0.3)
    experience_weight = models.FloatField(default=0.3)
    skills_weight = models.FloatField(default=0.4)