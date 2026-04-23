from django.utils import timezone
from datetime import timedelta
from Task.models import Notification, UserInfo, Task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings as django_settings


def create_task_notification(user, task, notification_type='task_created'):
    """Create notifications for task-related events"""
    try:
        userinfo = UserInfo.objects.get(user=user)
    except UserInfo.DoesNotExist:
        userinfo = None

    # Check user preferences
    if userinfo and not userinfo.task_reminders:
        return

    if notification_type == 'task_created':
        title = 'Task Created'
        message = f'Your task "{task.title}" has been created.'
        link = f'/Dash'
    elif notification_type == 'task_completed':
        title = 'Task Completed'
        message = f'Great job! You completed "{task.title}".'
        link = f'/Dash'
    elif notification_type == 'task_due_soon':
        title = 'Task Due Soon'
        message = f'Your task "{task.title}" is due soon.'
        link = f'/allpage'
    elif notification_type == 'task_overdue':
        title = 'Task Overdue'
        message = f'Your task "{task.title}" is overdue.'
        link = f'/allpage'
    else:
        return

    Notification.create_notification(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message,
        link=link,
        task=task
    )

    # Send email notification if enabled
    if userinfo and userinfo.email_notifications:
        send_notification_email(user, title, message, notification_type)


def create_project_notification(user, project, notification_type='project_created'):
    """Create notifications for project-related events"""
    try:
        userinfo = UserInfo.objects.get(user=user)
    except UserInfo.DoesNotExist:
        userinfo = None

    if notification_type == 'project_created':
        title = 'Project Created'
        message = f'Your project "{project.title}" has been created.'
        link = f'/projects'
    elif notification_type == 'project_updated':
        title = 'Project Updated'
        message = f'Your project "{project.title}" has been updated.'
        link = f'/projects'
    else:
        return

    Notification.create_notification(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message,
        link=link,
        project=project
    )


def send_notification_email(user, title, message, notification_type):
    """Send email notification to user"""
    context = {
        'username': user.username,
        'title': title,
        'message': message,
        'notification_type': notification_type,
    }

    try:
        html_content = render_to_string('emails/notification_email.html', context)
        text_content = render_to_string('emails/notification_email.txt', context)
    except Exception:
        # Fallback if template doesn't exist
        html_content = f'<h3>{title}</h3><p>{message}</p>'
        text_content = f'{title}\n\n{message}'

    subject = f'{title} - TaskFlow'
    from_email = f"{getattr(django_settings, 'DEFAULT_FROM_NAME', 'TaskFlow')} <{django_settings.DEFAULT_FROM_EMAIL}>"
    to_email = user.email

    email = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    email.attach_alternative(html_content, "text/html")
    
    try:
        email.send()
    except Exception:
        # Silently fail - email service might not be configured
        pass


def check_due_tasks():
    """Check for tasks due soon and create notifications"""
    now = timezone.now()
    tomorrow = now + timedelta(days=1)
    
    # Tasks due in next 24 hours
    tasks_due_soon = Task.objects.filter(
        due_date__range=[now, tomorrow],
        completed=False,
        overdue=False
    )
    
    for task in tasks_due_soon:
        create_task_notification(task.user, task, 'task_due_soon')


def check_overdue_tasks():
    """Check for overdue tasks and create notifications"""
    now = timezone.now()
    
    overdue_tasks = Task.objects.filter(
        due_date__lt=now,
        completed=False,
        overdue=False
    )
    
    for task in overdue_tasks:
        task.overdue = True
        task.save()
        create_task_notification(task.user, task, 'task_overdue')


def get_unread_count(user):
    """Get count of unread notifications for user"""
    return Notification.objects.filter(user=user, is_read=False).count()


def get_user_notifications(user, unread_only=False, limit=20):
    """Get notifications for user with optional filtering"""
    queryset = Notification.objects.filter(user=user)
    if unread_only:
        queryset = queryset.filter(is_read=False)
    return queryset[:limit]
