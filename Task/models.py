from django.db import models
from django.contrib.auth.models import User, auth
from django_resized import ResizedImageField
import uuid
from datetime import timedelta
from django.utils import timezone
from django.conf import settings


# Create your models here.

class UserInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to="profile_image/", null=True, blank=True)
    email_verified = models.BooleanField(default=False)
    display_name = models.CharField(max_length=150, blank=True)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    timezone = models.CharField(max_length=50, default='UTC', blank=True)
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    task_reminders = models.BooleanField(default=True)
    mention_notifications = models.BooleanField(default=True)
    weekly_digest = models.BooleanField(default=False)
    two_factor_enabled = models.BooleanField(default=False)
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)
    theme = models.CharField(max_length=20, default='light')
    accent_color = models.CharField(max_length=7, default='#3b82f6')
    font_size = models.CharField(max_length=10, default='medium')
    compact_mode = models.BooleanField(default=False)
    show_animations = models.BooleanField(default=True)
    profile_visibility = models.BooleanField(default=True)
    activity_status = models.BooleanField(default=True)
    search_indexing = models.BooleanField(default=True)
    webhook_url = models.URLField(blank=True)
    webhook_events = models.TextField(blank=True, default='Task Created,Task Completed')
    allow_invitations = models.BooleanField(default=False)
    public_team_profile = models.BooleanField(default=True)
    
    class Meta:
        managed = True
        db_table = 'userinfo'

    def __str__(self):
        return self.display_name or self.user.username


class EmailVerificationToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = 'email_verification_token'

    def save(self, *args, **kwargs):
        if not self.expires_at:
            expiry_hours = getattr(settings, 'VERIFICATION_TOKEN_EXPIRY_HOURS', 24)
            self.expires_at = timezone.now() + timedelta(hours=expiry_hours)
        super().save(*args, **kwargs)

    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at

    def __str__(self):
        return f"Verification token for {self.user.email}"


class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = 'password_reset_token'

    def save(self, *args, **kwargs):
        if not self.expires_at:
            expiry_hours = getattr(settings, 'PASSWORD_RESET_TOKEN_EXPIRY_HOURS', 1)
            self.expires_at = timezone.now() + timedelta(hours=expiry_hours)
        super().save(*args, **kwargs)

    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at

    def __str__(self):
        return f"Password reset token for {self.user.email}"

    
class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    # status = models.CharField(max_length=100, default="progress")
    completed = models.BooleanField(default=False)
    in_progress = models.BooleanField(default=True)
    overdue = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)
    assigned_members = models.TextField(blank=True, help_text='Comma-separated member IDs')

    def __str__(self):
        return self.title

    @property
    def assigned_members_list(self):
        """Return list of member IDs assigned to this task"""
        return [m.strip() for m in self.assigned_members.split(',') if m.strip()] if self.assigned_members else []

    def get_assigned_members(self):
        """Return actual Member objects assigned to this task"""
        member_ids = self.assigned_members_list
        if member_ids:
            return Member.objects.filter(id__in=member_ids)
        return Member.objects.none()


class Project(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
        ('at_risk', 'At Risk'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    color = models.CharField(max_length=7, default='#3b82f6')  # hex color
    progress = models.IntegerField(default=0)  # 0-100
    team_members = models.TextField(blank=True)  # comma-separated names
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Member(models.Model):
    ROLE_CHOICES = [
        ('developer', 'Developer'),
        ('designer', 'Designer'),
        ('manager', 'Manager'),
        ('tester', 'Tester'),
        ('analyst', 'Analyst'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('on_leave', 'On Leave'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team_members', null=True, blank=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='developer')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='member_avatars/', null=True, blank=True)
    bio = models.TextField(blank=True)
    joined_date = models.DateField(null=True, blank=True)
    projects = models.TextField(blank=True, help_text='Comma-separated project IDs')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'member'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def project_list(self):
        """Return list of project IDs this member is assigned to"""
        return [p.strip() for p in self.projects.split(',') if p.strip()] if self.projects else []


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('task_created', 'Task Created'),
        ('task_completed', 'Task Completed'),
        ('task_due_soon', 'Task Due Soon'),
        ('task_overdue', 'Task Overdue'),
        ('project_created', 'Project Created'),
        ('project_updated', 'Project Updated'),
        ('mention', 'Mention'),
        ('team_invite', 'Team Invite'),
        ('general', 'General'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    link = models.URLField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    task = models.ForeignKey('Task', on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    project = models.ForeignKey('Project', on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')

    class Meta:
        managed = True
        db_table = 'notification'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"

    def mark_as_read(self):
        self.is_read = True
        self.save()

    @classmethod
    def create_notification(cls, user, notification_type, title, message, link=None, task=None, project=None):
        """Helper method to create a notification"""
        return cls.objects.create(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            link=link,
            task=task,
            project=project
        )

