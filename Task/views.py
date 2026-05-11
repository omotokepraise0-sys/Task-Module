from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime
timepackage = datetime.now()
from Task.models import * # this is to import entire table from DB
from django.contrib import messages # user output messages
from django.contrib.auth.hashers import make_password # encrypt password
from django.contrib.auth.decorators import login_required # login required
from django.contrib.auth import login, authenticate, logout, get_user_model, update_session_auth_hash
import json
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings as django_settings
from django.urls import reverse
from django.utils.html import strip_tags
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.utils import OperationalError, ProgrammingError
from types import SimpleNamespace
from Task.utils import create_task_notification, create_project_notification


# Create your views here.
def homepage(request):
      return render(request, 'index.html')

def allpage(request):
    all_tasks = Task.objects.filter(user=request.user).order_by('-created_at')
    search_query = request.GET.get('search', '')
    filter_type = request.GET.get('filter', 'all')

    if search_query:
        all_tasks = all_tasks.filter(title__icontains=search_query)

    for task in all_tasks:
        if task.due_date and task.due_date < timezone.now() and not task.completed and not task.overdue:
            task.overdue = True
            task.save()

    if filter_type == 'completed':
        all_tasks = all_tasks.filter(completed=True)
    elif filter_type == 'overdue':
        all_tasks = all_tasks.filter(overdue=True)
    elif filter_type == 'today':
        from datetime import timedelta
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)
        all_tasks = all_tasks.filter(due_date__date=today, completed=False)
    elif filter_type == 'upcoming':
        from datetime import timedelta
        today = timezone.now().date()
        all_tasks = all_tasks.filter(due_date__date__gt=today, completed=False)

    total_tasks = all_tasks.count()
    completed_count = all_tasks.filter(completed=True).count()
    overdue_count = all_tasks.filter(overdue=True).count()

    # Get all members for assignment
    all_members = Member.objects.filter(status='active').order_by('name')

    paginator = Paginator(all_tasks, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'allpage.html', {
        'all_tasks': page_obj,
        'page_obj': page_obj,
        'total_tasks': total_tasks,
        'completed_count': completed_count,
        'overdue_count': overdue_count,
        'search_query': search_query,
        'filter_type': filter_type,
        'paginator': paginator,
        'all_members': all_members,
    })



@login_required
def settings(request):
    active_section = request.GET.get('section', 'profile')

    def parse_time_value(value):
        if not value:
            return None
        try:
            return datetime.strptime(value, '%H:%M').time()
        except ValueError:
            return None

    default_userinfo = {
        'profile_image': None,
        'display_name': request.user.username,
        'bio': '',
        'location': '',
        'timezone': 'UTC',
        'email_notifications': True,
        'push_notifications': True,
        'task_reminders': True,
        'mention_notifications': True,
        'weekly_digest': False,
        'two_factor_enabled': False,
        'quiet_hours_start': None,
        'quiet_hours_end': None,
        'theme': 'light',
        'accent_color': '#3b82f6',
        'font_size': 'medium',
        'compact_mode': False,
        'show_animations': True,
        'profile_visibility': True,
        'activity_status': True,
        'search_indexing': True,
        'webhook_url': '',
        'webhook_events': 'Task Created,Task Completed',
        'allow_invitations': False,
        'public_team_profile': True,
    }

    using_database = True
    try:
        userinfo, _ = UserInfo.objects.get_or_create(user=request.user)
    except (OperationalError, ProgrammingError):
        using_database = False
        session_values = request.session.get('settings_fallback', {}).copy()
        session_values['quiet_hours_start'] = parse_time_value(session_values.get('quiet_hours_start'))
        session_values['quiet_hours_end'] = parse_time_value(session_values.get('quiet_hours_end'))
        userinfo = SimpleNamespace(**{**default_userinfo, **session_values})

    def save_userinfo():
        if using_database:
            userinfo.save()
        else:
            request.session['settings_fallback'] = {
                'display_name': getattr(userinfo, 'display_name', ''),
                'bio': getattr(userinfo, 'bio', ''),
                'location': getattr(userinfo, 'location', ''),
                'timezone': getattr(userinfo, 'timezone', 'UTC'),
                'email_notifications': getattr(userinfo, 'email_notifications', True),
                'push_notifications': getattr(userinfo, 'push_notifications', True),
                'task_reminders': getattr(userinfo, 'task_reminders', True),
                'mention_notifications': getattr(userinfo, 'mention_notifications', True),
                'weekly_digest': getattr(userinfo, 'weekly_digest', False),
                'two_factor_enabled': getattr(userinfo, 'two_factor_enabled', False),
                'quiet_hours_start': userinfo.quiet_hours_start.strftime('%H:%M') if getattr(userinfo, 'quiet_hours_start', None) else '',
                'quiet_hours_end': userinfo.quiet_hours_end.strftime('%H:%M') if getattr(userinfo, 'quiet_hours_end', None) else '',
                'theme': getattr(userinfo, 'theme', 'light'),
                'accent_color': getattr(userinfo, 'accent_color', '#3b82f6'),
                'font_size': getattr(userinfo, 'font_size', 'medium'),
                'compact_mode': getattr(userinfo, 'compact_mode', False),
                'show_animations': getattr(userinfo, 'show_animations', True),
                'profile_visibility': getattr(userinfo, 'profile_visibility', True),
                'activity_status': getattr(userinfo, 'activity_status', True),
                'search_indexing': getattr(userinfo, 'search_indexing', True),
                'webhook_url': getattr(userinfo, 'webhook_url', ''),
                'webhook_events': getattr(userinfo, 'webhook_events', 'Task Created,Task Completed'),
                'allow_invitations': getattr(userinfo, 'allow_invitations', False),
                'public_team_profile': getattr(userinfo, 'public_team_profile', True),
            }
            request.session.modified = True

    if request.method == 'POST':
        action = request.POST.get('action', 'profile')
        active_section = request.POST.get('current_section', action)

        if action == 'profile':
            full_name = request.POST.get('full_name', '').strip()
            display_name = request.POST.get('display_name', '').strip()
            email = request.POST.get('email', '').strip()
            bio = request.POST.get('bio', '').strip()
            location = request.POST.get('location', '').strip()
            timezone_value = request.POST.get('timezone', 'UTC').strip()

            if email and User.objects.exclude(pk=request.user.pk).filter(email=email).exists():
                messages.error(request, 'That email address is already in use.')
                return redirect(f"{reverse('settings')}?section=profile")

            name_parts = full_name.split(maxsplit=1)
            request.user.first_name = name_parts[0] if name_parts else ''
            request.user.last_name = name_parts[1] if len(name_parts) > 1 else ''
            request.user.email = email
            request.user.save()

            userinfo.display_name = display_name
            userinfo.bio = bio
            userinfo.location = location
            userinfo.timezone = timezone_value or 'UTC'
            if 'profile_image' in request.FILES and using_database:
                userinfo.profile_image = request.FILES['profile_image']
            elif 'profile_image' in request.FILES and not using_database:
                messages.warning(request, 'Profile image upload will be available after running migrations.')
            save_userinfo()
            messages.success(request, 'Profile settings updated successfully.')

        elif action == 'password':
            current_password = request.POST.get('current_password', '')
            new_password = request.POST.get('new_password', '')
            confirm_password = request.POST.get('confirm_password', '')
            userinfo.two_factor_enabled = 'two_factor_enabled' in request.POST

            if not any([current_password, new_password, confirm_password]):
                save_userinfo()
                messages.success(request, 'Security settings updated.')
            elif not request.user.check_password(current_password):
                messages.error(request, 'Current password is incorrect.')
            elif new_password != confirm_password:
                messages.error(request, 'New password and confirmation do not match.')
            elif len(new_password) < 8:
                messages.error(request, 'New password must be at least 8 characters long.')
            else:
                save_userinfo()
                request.user.set_password(new_password)
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, 'Password updated successfully.')

        elif action == 'notifications':
            userinfo.email_notifications = 'email_notifications' in request.POST
            userinfo.push_notifications = 'push_notifications' in request.POST
            userinfo.task_reminders = 'task_reminders' in request.POST
            userinfo.mention_notifications = 'mention_notifications' in request.POST
            userinfo.weekly_digest = 'weekly_digest' in request.POST
            userinfo.quiet_hours_start = parse_time_value(request.POST.get('quiet_hours_start'))
            userinfo.quiet_hours_end = parse_time_value(request.POST.get('quiet_hours_end'))
            save_userinfo()
            messages.success(request, 'Notification preferences saved.')

        elif action == 'appearance':
            userinfo.theme = request.POST.get('theme', 'light')
            userinfo.accent_color = request.POST.get('accent_color', '#3b82f6')
            userinfo.font_size = request.POST.get('font_size', 'medium')
            userinfo.compact_mode = 'compact_mode' in request.POST
            userinfo.show_animations = 'show_animations' in request.POST
            save_userinfo()
            messages.success(request, 'Appearance settings applied.')

        elif action == 'privacy':
            if 'request_export' in request.POST:
                export_payload = {
                    'user': {
                        'username': request.user.username,
                        'full_name': request.user.get_full_name(),
                        'email': request.user.email,
                    },
                    'settings': {
                        'display_name': userinfo.display_name,
                        'bio': userinfo.bio,
                        'location': userinfo.location,
                        'timezone': userinfo.timezone,
                        'profile_visibility': userinfo.profile_visibility,
                        'activity_status': userinfo.activity_status,
                        'search_indexing': userinfo.search_indexing,
                    },
                    'projects': list(Project.objects.filter(user=request.user).values()),
                    'tasks': list(Task.objects.filter(user=request.user).values()),
                }
                response = HttpResponse(json.dumps(export_payload, indent=2, default=str), content_type='application/json')
                response['Content-Disposition'] = 'attachment; filename="taskflow-export.json"'
                return response

            if 'delete_account' in request.POST:
                if request.POST.get('delete_confirmation', '').strip().upper() == 'DELETE':
                    user = request.user
                    logout(request)
                    user.delete()
                    messages.success(request, 'Your account has been deleted.')
                    return redirect('home')
                messages.error(request, 'Type DELETE to confirm account deletion.')
                return redirect(f"{reverse('settings')}?section=privacy")

            userinfo.profile_visibility = 'profile_visibility' in request.POST
            userinfo.activity_status = 'activity_status' in request.POST
            userinfo.search_indexing = 'search_indexing' in request.POST
            save_userinfo()
            messages.success(request, 'Privacy settings saved.')

        elif action == 'integrations':
            userinfo.webhook_url = request.POST.get('webhook_url', '').strip()
            userinfo.webhook_events = ','.join(request.POST.getlist('webhook_events'))
            save_userinfo()
            messages.success(request, 'Webhook settings saved.')

        elif action == 'team':
            userinfo.allow_invitations = 'allow_invitations' in request.POST
            userinfo.public_team_profile = 'public_team_profile' in request.POST
            save_userinfo()
            messages.success(request, 'Team settings updated.')

        return redirect(f"{reverse('settings')}?section={active_section}")

    context = {
        'userinfo': userinfo,
        'active_section': active_section,
        'webhook_events_selected': [event.strip() for event in userinfo.webhook_events.split(',') if event.strip()],
    }
    return render(request, 'settings.html', context)

def projects(request):
    # Get all projects for user
    projects = Project.objects.filter(user=request.user)
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        projects = projects.filter(title__icontains=search_query) | projects.filter(description__icontains=search_query)
    
    # Filter
    filter_type = request.GET.get('filter', 'all')
    if filter_type != 'all':
        projects = projects.filter(status=filter_type)
    
    # View type
    view_type = request.GET.get('view', 'grid')
    
    # Stats
    total_projects = Project.objects.filter(user=request.user).count()
    active_count = Project.objects.filter(user=request.user, status='active').count()
    completed_count = Project.objects.filter(user=request.user, status='completed').count()
    at_risk_count = Project.objects.filter(user=request.user, status='at_risk').count()
    
    # Process projects to add team_members_list and member objects
    projects_list = []
    for project in projects:
        project.team_members_list = project.team_members.split(',') if project.team_members else []
        # Get actual member objects
        member_ids = [mid.strip() for mid in project.team_members_list if mid.strip()]
        project.members = Member.objects.filter(id__in=member_ids) if member_ids else []
        projects_list.append(project)

    # Get all active members for dropdown
    all_members = Member.objects.filter(status='active').order_by('name')

    context = {
        'projects': projects_list,
        'search_query': search_query,
        'filter_type': filter_type,
        'view_type': view_type,
        'total_projects': total_projects,
        'active_count': active_count,
        'completed_count': completed_count,
        'at_risk_count': at_risk_count,
        'all_members': all_members,
    }
    return render(request, 'projects.html', context)

def Dash(request):
    # Prevent AnonymousUser from reaching task queries
    if not request.user.is_authenticated:
        return redirect('login')

    tasks = Task.objects.filter(user=request.user).count()
    completed = Task.objects.filter(user=request.user, completed=True).count()
    in_progress = Task.objects.filter(user=request.user, in_progress=True).count()
    overdue = Task.objects.filter(user=request.user, overdue=True).count()


    completed_tasks = Task.objects.filter(
            user=request.user,
            completed=True
    )[:5]

    progress_tasks = Task.objects.filter(
            user=request.user,
            in_progress=True
    )[:5]
    # currentdate = timepackage.strftime('%Y-%m-%d')
    daily_task = Task.objects.filter(user=request.user).order_by('-created_at')[:5]

    from django.utils import timezone
    for task in daily_task:
        if task.due_date and task.due_date < timezone.now() and not task.completed and not task.overdue:
            task.overdue = True
            task.save()
    latest_completed = Task.objects.filter(user=user, completed=True).order_by('-created_at')[:5]


    return render(request, 'Dash.html',
        {
            'total_tasks': tasks,
            'completed_task': completed,
            'progress_Task': in_progress,
            'overdue_Task': overdue,
            'daily_task': daily_task,
            'latest_completed': latest_completed,
            'all_completed': completed_tasks,
            'progress_tasks': progress_tasks,
        }
    )



@login_required
def create_task(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        due_date = request.POST.get('due_date')
        assigned_members = request.POST.get('assigned_members', '')

        if not title:
            return JsonResponse({'success': False, 'error': 'Task title cannot be empty!'})

        if Task.objects.filter(title=title, user=request.user).exists():
            return JsonResponse({'success': False, 'error': 'Task already exists!'})

        new_task = Task.objects.create(
            user=request.user,
            title=title,
            due_date=due_date if due_date else None,
            assigned_members=assigned_members
        )
        create_task_notification(request.user, new_task, 'task_created')
        return JsonResponse({'success': True, 'task_id': new_task.id})
    return JsonResponse({'success': False, 'error': 'Invalid request'})


@login_required
def update_task_status(request):
    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        checked = request.POST.get('checked') == 'true'
        try:
            task = Task.objects.get(id=task_id, user=request.user)
            if checked:
                task.completed = True
                task.in_progress = False
                task.overdue = False
                task.save()
                create_task_notification(request.user, task, 'task_completed')
            else:
                task.completed = False
                task.in_progress = True
                task.overdue = False
                task.save()
            return JsonResponse({'success': True})
        except Task.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Task not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})


@login_required
def delete_task(request):
    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        try:
            task = Task.objects.get(id=task_id, user=request.user)
            task.delete()
            return JsonResponse({'success': True})
        except Task.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Task not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})


@login_required
def edit_task(request, task_id):
    try:
        task = Task.objects.get(id=task_id, user=request.user)
        if request.method == 'POST':
            task.title = request.POST.get('title', task.title)
            task.due_date = request.POST.get('due_date') if request.POST.get('due_date') else task.due_date
            task.assigned_members = request.POST.get('assigned_members', task.assigned_members)
            task.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({
                'success': True,
                'task': {
                    'id': task.id,
                    'title': task.title,
                    'due_date': task.due_date.strftime('%Y-%m-%dT%H:%M') if task.due_date else '',
                    'assigned_members': task.assigned_members,
                }
            })
    except Task.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Task not found'})


@login_required
def create_project(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        status = request.POST.get('status', 'active')
        progress = request.POST.get('progress', '0')
        color = request.POST.get('color', '#3b82f6')
        team_members = request.POST.get('team_members')

        try:
            progress = int(progress)
            if progress < 0:
                progress = 0
            if progress > 100:
                progress = 100
        except (ValueError, TypeError):
            progress = 0

        if title:
            new_project = Project.objects.create(
                user=request.user,
                title=title,
                description=description,
                start_date=start_date if start_date else None,
                end_date=end_date if end_date else None,
                status=status,
                progress=progress,
                color=color,
                team_members=team_members,
            )
            # Create notification for project creation
            create_project_notification(request.user, new_project, 'project_created')
        return redirect('projects')
    return redirect('projects')


@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    if request.method == 'POST':
        project.title = request.POST.get('title', project.title)
        project.description = request.POST.get('description', project.description)
        project.start_date = request.POST.get('start_date') if request.POST.get('start_date') else project.start_date
        project.end_date = request.POST.get('end_date') if request.POST.get('end_date') else project.end_date
        project.status = request.POST.get('status', project.status)
        project.color = request.POST.get('color', project.color)
        project.progress = int(request.POST.get('progress', project.progress))
        project.team_members = request.POST.get('team_members', project.team_members)
        project.save()
        # Create notification for project update
        create_project_notification(request.user, project, 'project_updated')
        return redirect('projects')
    # For simplicity, redirect to projects with edit_id
    return redirect(f'/projects?edit={project_id}')


@login_required
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    if request.method == 'POST':
        project.delete()
    return redirect('projects')


def send_verification_email(user, request):
    """Send verification email to user"""
    # Delete any existing unused tokens for this user
    EmailVerificationToken.objects.filter(user=user, is_used=False).delete()
    
    # Create new verification token
    token = EmailVerificationToken.objects.create(user=user)
    
    # Build verification link
    verification_link = request.build_absolute_uri(
        reverse('verify_email', kwargs={'token': str(token.token)})
    ) if 'request' in dir() else f"http://localhost:8000/verify-email/{str(token.token)}/"
    
    # Context for email template
    context = {
        'username': user.username,
        'verification_link': verification_link,
        'expiry_hours': getattr(django_settings, 'VERIFICATION_TOKEN_EXPIRY_HOURS', 24),
    }
    
    # Render email templates
    html_content = render_to_string('emails/verification_email.html', context)
    text_content = render_to_string('emails/verification_email.txt', context)
    
    # Create email
    subject = 'Verify Your Email - TaskFlow'
    from_email = f"{getattr(django_settings, 'DEFAULT_FROM_NAME', 'TaskFlow')} <{django_settings.DEFAULT_FROM_EMAIL}>"
    to_email = user.email
    
    email = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    email.attach_alternative(html_content, "text/html")
    email.send()
    
    return token


def register(request):
    if request.method == 'POST':
        get_email = request.POST.get('email')
        get_username = request.POST.get('username')
        get_password = request.POST.get('password')

        values = {
             'username': get_username,
             'email': get_email
        }

        if User.objects.filter(username=get_username).exists() or User.objects.filter(email=get_email).exists():
            error = "Email or Username already exists in our database!"
            return render(request, 'register.html', {'error': error, 'values': values})

        if "profile_image" in request.FILES:
            profile_picture = request.FILES['profile_image']
        else:
            profile_picture = ""

        auth_user_submit = User.objects.create_user(password=get_password, is_superuser=0, username=get_username, email=get_email)
        auth_user_submit.save()

        signup_submit = UserInfo.objects.create(user=auth_user_submit, profile_image=profile_picture)
        signup_submit.save()

        # Send verification email
        try:
            # Build verification link with request
            from Task.models import EmailVerificationToken
            from django.utils import timezone
            from datetime import timedelta
            import uuid
            
            # Delete any existing unused tokens
            EmailVerificationToken.objects.filter(user=auth_user_submit, is_used=False).delete()
            
            # Create new token
            expiry_hours = getattr(django_settings, 'VERIFICATION_TOKEN_EXPIRY_HOURS', 24)
            token = EmailVerificationToken.objects.create(
                user=auth_user_submit,
                expires_at=timezone.now() + timedelta(hours=expiry_hours)
            )
            
            # Build verification link
            verification_link = request.build_absolute_uri(
                reverse('verify_email', kwargs={'token': str(token.token)})
            )
            
            # Context for email template
            context = {
                'username': get_username,
                'verification_link': verification_link,
                'expiry_hours': expiry_hours,
            }
            
            # Render email templates
            html_content = render_to_string('emails/verification_email.html', context)
            text_content = render_to_string('emails/verification_email.txt', context)
            
            # Create and send email
            subject = 'Verify Your Email - TaskFlow'
            from_email = f"{getattr(django_settings, 'DEFAULT_FROM_NAME', 'TaskFlow')} <{django_settings.DEFAULT_FROM_EMAIL}>"
            
            email = EmailMultiAlternatives(subject, text_content, from_email, [get_email])
            email.attach_alternative(html_content, "text/html")
            email.send()
            
            messages.success(request, f"Account created successfully! Please check your email at {get_email} to verify your account.")
        except Exception as e:
            # If email fails, still allow registration but show warning
            messages.warning(request, f"Account created but verification email could not be sent. Please contact support.")

        return redirect('/login')

    else:
        return render(request, 'register.html')
    

def loginpage(request):
    if request.method == 'POST':
        email = request.POST.get("email")
        get_password = request.POST.get("password")

        try:
            user_obj = User.objects.get(email=email)
            get_username = user_obj.username
        except User.DoesNotExist:
            messages.error(request, "Invalid email or password")
            return redirect("/login")

        # Check if email is verified (only if UserInfo exists)
        try:
            user_info = UserInfo.objects.get(user=user_obj)
            if not user_info.email_verified:
                # Auto-verify for development/debugging purposes
                # In production, uncomment the lines below to enforce email verification
                # messages.warning(request, "Please verify your email before logging in. Check your inbox for the verification link.")
                # return redirect("/login")
                user_info.email_verified = True
                user_info.save()
        except UserInfo.DoesNotExist:
            pass

        user = authenticate(username=get_username, password=get_password)

        if user is None:
            messages.error(request, "Invalid email or password")
            return redirect("/login")
        else:
            login(request, user)
            current_user = request.user
            get_superuser = current_user.is_superuser

            if get_superuser == 1:
                return redirect("/admin_dashboard")
            else:
                return redirect("Dash")
    else:
        return render(request, 'login.html')


def verify_email(request, token):
    """Verify user email using token"""
    try:
        from Task.models import EmailVerificationToken
        
        # Get the verification token
        verification_token = EmailVerificationToken.objects.get(token=token)
        
        # Check if token is valid
        if not verification_token.is_valid():
            if verification_token.is_used:
                messages.error(request, "This verification link has already been used.")
            else:
                messages.error(request, "This verification link has expired. Please request a new one.")
            return redirect('/login')
        
        # Mark token as used
        verification_token.is_used = True
        verification_token.save()
        
        # Mark user's email as verified
        user_info = UserInfo.objects.get(user=verification_token.user)
        user_info.email_verified = True
        user_info.save()
        
        messages.success(request, f"Email verified successfully! You can now log in as {verification_token.user.username}.")
        return redirect('/login')
    
    except EmailVerificationToken.DoesNotExist:
        messages.error(request, "Invalid verification link.")
        return redirect('/login')
    except Exception as e:
        messages.error(request, "An error occurred during verification. Please try again.")
        return redirect('/login')


def resend_verification(request):
    """Resend verification email"""
    if request.method == 'POST':
        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)
            user_info = UserInfo.objects.get(user=user)

            if user_info.email_verified:
                messages.info(request, "Your email is already verified. You can log in.")
                return redirect('/login')

            # Send new verification email
            from django.utils import timezone
            from datetime import timedelta

            # Delete existing unused tokens
            EmailVerificationToken.objects.filter(user=user, is_used=False).delete()

            # Create new token
            expiry_hours = getattr(django_settings, 'VERIFICATION_TOKEN_EXPIRY_HOURS', 24)
            token = EmailVerificationToken.objects.create(
                user=user,
                expires_at=timezone.now() + timedelta(hours=expiry_hours)
            )

            # Build verification link
            verification_link = request.build_absolute_uri(
                reverse('verify_email', kwargs={'token': str(token.token)})
            )

            # Context for email template
            context = {
                'username': user.username,
                'verification_link': verification_link,
                'expiry_hours': expiry_hours,
            }

            # Render and send email
            html_content = render_to_string('emails/verification_email.html', context)
            text_content = render_to_string('emails/verification_email.txt', context)

            subject = 'Verify Your Email - TaskFlow'
            from_email = f"{getattr(django_settings, 'DEFAULT_FROM_NAME', 'TaskFlow')} <{django_settings.DEFAULT_FROM_EMAIL}>"

            email_msg = EmailMultiAlternatives(subject, text_content, from_email, [email])
            email_msg.attach_alternative(html_content, "text/html")
            email_msg.send()

            messages.success(request, f"Verification email sent to {email}. Please check your inbox.")
            return redirect('/login')

        except User.DoesNotExist:
            messages.error(request, "No account found with this email address.")
            return redirect('/login')
        except Exception as e:
            messages.error(request, "Failed to send verification email. Please try again.")
            return redirect('/login')

    return render(request, 'resend_verification.html')


def password_reset_request(request):
    """Handle password reset request"""
    if request.method == 'POST':
        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)

            # Delete any existing unused tokens
            PasswordResetToken.objects.filter(user=user, is_used=False).delete()

            # Create new token
            from django.utils import timezone
            from datetime import timedelta
            expiry_hours = getattr(django_settings, 'PASSWORD_RESET_TOKEN_EXPIRY_HOURS', 1)
            token = PasswordResetToken.objects.create(
                user=user,
                expires_at=timezone.now() + timedelta(hours=expiry_hours)
            )

            # Build reset link
            reset_link = request.build_absolute_uri(
                reverse('password_reset_confirm', kwargs={'token': str(token.token)})
            )

            # Context for email template
            context = {
                'username': user.username,
                'reset_link': reset_link,
                'expiry_hours': expiry_hours,
            }

            # Render email templates
            html_content = render_to_string('emails/password_reset_email.html', context)
            text_content = render_to_string('emails/password_reset_email.txt', context)

            # Create email
            subject = 'Password Reset Request - TaskFlow'
            from_email = f"{getattr(django_settings, 'DEFAULT_FROM_NAME', 'TaskFlow')} <{django_settings.DEFAULT_FROM_EMAIL}>"

            email_msg = EmailMultiAlternatives(subject, text_content, from_email, [email])
            email_msg.attach_alternative(html_content, "text/html")
            email_msg.send()

            messages.success(request, f"Password reset instructions sent to {email}. Please check your inbox.")
            return redirect('/login')

        except User.DoesNotExist:
            # For security, show same message whether email exists or not
            messages.success(request, "If an account exists with this email, you will receive password reset instructions.")
            return redirect('/login')
        except Exception as e:
            messages.error(request, "Failed to send reset email. Please try again.")
            return redirect('/login')

    return render(request, 'password_reset_request.html')


def password_reset_confirm(request, token):
    """Handle password reset with token"""
    try:
        # Get the verification token
        reset_token = PasswordResetToken.objects.get(token=token)

        # Check if token is valid
        if not reset_token.is_valid():
            if reset_token.is_used:
                messages.error(request, "This reset link has already been used. Please request a new one.")
            else:
                messages.error(request, "This reset link has expired. Please request a new one.")
            return redirect('/login')

        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if not new_password or len(new_password) < 8:
                messages.error(request, "Password must be at least 8 characters long.")
                return render(request, 'password_reset_confirm.html', {'token': token})

            if new_password != confirm_password:
                messages.error(request, "Passwords do not match.")
                return render(request, 'password_reset_confirm.html', {'token': token})

            # Set new password
            user = reset_token.user
            user.set_password(new_password)
            user.save()

            # Mark token as used
            reset_token.is_used = True
            reset_token.save()

            messages.success(request, "Password reset successfully! You can now log in with your new password.")
            return redirect('/login')

        return render(request, 'password_reset_confirm.html', {'token': token})

    except PasswordResetToken.DoesNotExist:
        messages.error(request, "Invalid reset link.")
        return redirect('/login')
    except Exception as e:
        messages.error(request, "An error occurred. Please try again.")
        return redirect('/login')

@login_required(login_url='/login')        
def user_dashboardpage(request):
    return render(request, 'user_dashboard.html')


@login_required(login_url='/login')    
def edit_profilepage(request, id):
    if request.method == 'POST':
        name = request.POST.get('name') 
        old_image = request.POST.get('old_image') 
        get_email = request.POST.get('email')
        phone = request.POST.get('phone')
        dob1 = request.POST.get('dob')
        # dob = parse(dob1)
        ph = request.POST.get('ph')
        gender = request.POST.get('gender')
        location = request.POST.get('location')
        get_username = request.POST.get('username')
        get_password = request.POST.get('password')

        if "fileToUpload" in request.FILES:
            get_passport = request.FILES['fileToUpload'] # if the user select a new image
        else:
            get_passport = old_image.replace('/media/', '') # still use the old image if no new image
        
        # Get the user identity from the database to update
        user_identity = User.objects.get(id=id) # this implies the database id is the first, while the second id is from the request def via the url
        user_identity.password = make_password(get_password)
        user_identity.username = get_username
        user_identity.first_name = name
        user_identity.email = get_email
        user_identity.save()

        signup_identity = UserInfo.objects.get(user_id=id)
        #  signup_submit = Signup.objects.create(name=name, email=get_email, phone=phone, dob=dob, ph=ph, gender=gender, location=location, username=get_username, is_superuser = 0, passport=get_passport, user=auth_user_submit)
        signup_identity.name = name
        signup_identity.email = get_email
        signup_identity.phone = phone
        signup_identity.ph = ph
        signup_identity.gender = gender
        signup_identity.location = location
        signup_identity.username = get_username
        signup_identity.passport = get_passport
        signup_identity.save()
        messages.info(request, "Your profile has been updated")
        return redirect('/login')

    
    else:
        get_id = User.objects.get(id=id) 
        user_identity = UserInfo.objects.get(user_id=get_id)
        return render(request, 'edit_profile.html', {'get_id':get_id})


def logoutpage(request):
    logout(request)
    return redirect('/login')


@login_required
def notifications(request):
    """Display user notifications"""
    filter_type = request.GET.get('filter', 'all')
    
    if filter_type == 'unread':
        user_notifications = Notification.objects.filter(user=request.user, is_read=False)
    elif filter_type == 'read':
        user_notifications = Notification.objects.filter(user=request.user, is_read=True)
    else:
        user_notifications = Notification.objects.filter(user=request.user)
    
    # Get stats
    total_count = Notification.objects.filter(user=request.user).count()
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    read_count = total_count - unread_count
    
    # Pagination
    paginator = Paginator(user_notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'notifications': page_obj,
        'page_obj': page_obj,
        'paginator': paginator,
        'total_count': total_count,
        'unread_count': unread_count,
        'read_count': read_count,
        'filter_type': filter_type,
    }
    return render(request, 'notifications.html', context)


@login_required
def mark_notification_read(request, notification_id):
    """Mark a single notification as read"""
    if request.method == 'POST':
        try:
            notification = Notification.objects.get(id=notification_id, user=request.user)
            notification.is_read = True
            notification.save()
            return JsonResponse({'success': True})
        except Notification.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Notification not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})


@login_required
def mark_all_notifications_read(request):
    """Mark all user notifications as read"""
    if request.method == 'POST':
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request'})


@login_required
def delete_notification(request, notification_id):
    """Delete a single notification"""
    if request.method == 'POST':
        try:
            notification = Notification.objects.get(id=notification_id, user=request.user)
            notification.delete()
            return JsonResponse({'success': True})
        except Notification.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Notification not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})


@login_required
def delete_all_notifications(request):
    """Delete all user notifications"""
    if request.method == 'POST':
        Notification.objects.filter(user=request.user).delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request'})


@login_required
def get_notification_count(request):
    """Get unread notification count - for AJAX polling"""
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'unread_count': unread_count})


@login_required
def get_notifications_list(request):
    """Get list of recent notifications - for AJAX/dropdown"""
    limit = int(request.GET.get('limit', 10))
    notifications = Notification.objects.filter(user=request.user)[:limit]

    data = {
        'notifications': [
            {
                'id': n.id,
                'title': n.title,
                'message': n.message,
                'type': n.notification_type,
                'is_read': n.is_read,
                'created_at': n.created_at.strftime('%Y-%m-%d %H:%M'),
                'link': n.link,
            }
            for n in notifications
        ],
        'unread_count': Notification.objects.filter(user=request.user, is_read=False).count(),
    }
    return JsonResponse(data)


@login_required
def members(request):
    """Display all team members with search and filter"""
    from django.db.models import Q

    all_members = Member.objects.all()
    search_query = request.GET.get('search', '')
    filter_role = request.GET.get('role', 'all')
    filter_status = request.GET.get('status', 'all')

    if search_query:
        all_members = all_members.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )

    if filter_role != 'all':
        all_members = all_members.filter(role=filter_role)

    if filter_status != 'all':
        all_members = all_members.filter(status=filter_status)

    all_members = all_members.order_by('-created_at')

    # Stats
    total_members = Member.objects.count()
    active_count = Member.objects.filter(status='active').count()
    roles_count = Member.objects.values('role').distinct().count()

    # Pagination
    paginator = Paginator(all_members, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'members': page_obj,
        'page_obj': page_obj,
        'paginator': paginator,
        'total_members': total_members,
        'active_count': active_count,
        'roles_count': roles_count,
        'search_query': search_query,
        'filter_role': filter_role,
        'filter_status': filter_status,
        'role_choices': Member.ROLE_CHOICES,
        'status_choices': Member.STATUS_CHOICES,
    }
    return render(request, 'members.html', context)


@login_required
def add_member(request):
    """Add a new team member"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        role = request.POST.get('role', 'developer')
        status = request.POST.get('status', 'active')
        phone = request.POST.get('phone', '').strip()
        bio = request.POST.get('bio', '').strip()
        joined_date = request.POST.get('joined_date')
        projects = request.POST.get('projects', '').strip()

        if not name or not email:
            messages.error(request, 'Name and email are required.')
            return redirect('members')

        if Member.objects.filter(email=email).exists():
            messages.error(request, 'A member with this email already exists.')
            return redirect('members')

        member = Member.objects.create(
            name=name,
            email=email,
            role=role,
            status=status,
            phone=phone,
            bio=bio,
            joined_date=joined_date if joined_date else None,
            projects=projects,
        )

        if 'avatar' in request.FILES:
            member.avatar = request.FILES['avatar']
            member.save()

        messages.success(request, f'Member "{name}" added successfully.')
        return redirect('members')

    return redirect('members')


@login_required
def edit_member(request, member_id):
    """Edit an existing team member"""
    member = get_object_or_404(Member, id=member_id)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        role = request.POST.get('role', 'developer')
        status = request.POST.get('status', 'active')
        phone = request.POST.get('phone', '').strip()
        bio = request.POST.get('bio', '').strip()
        joined_date = request.POST.get('joined_date')
        projects = request.POST.get('projects', '').strip()

        if not name or not email:
            messages.error(request, 'Name and email are required.')
            return redirect('members')

        # Check email uniqueness excluding current member
        if Member.objects.filter(email=email).exclude(id=member_id).exists():
            messages.error(request, 'A member with this email already exists.')
            return redirect('members')

        member.name = name
        member.email = email
        member.role = role
        member.status = status
        member.phone = phone
        member.bio = bio
        member.joined_date = joined_date if joined_date else None
        member.projects = projects

        if 'avatar' in request.FILES:
            member.avatar = request.FILES['avatar']

        member.save()
        messages.success(request, f'Member "{name}" updated successfully.')
        return redirect('members')

    return redirect('members')


@login_required
def delete_member(request, member_id):
    """Delete a team member"""
    if request.method == 'POST':
        try:
            member = Member.objects.get(id=member_id)
            member_name = member.name
            member.delete()
            return JsonResponse({
                'success': True,
                'message': f'Member "{member_name}" deleted successfully.'
            })
        except Member.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Member not found'
            })
    return JsonResponse({
        'success': False,
        'error': 'Invalid request'
    })


@login_required
def get_member_details(request, member_id):
    """Get member details via AJAX"""
    try:
        member = Member.objects.get(id=member_id)
        return JsonResponse({
            'success': True,
            'member': {
                'id': member.id,
                'name': member.name,
                'email': member.email,
                'role': member.role,
                'status': member.status,
                'phone': member.phone,
                'bio': member.bio,
                'joined_date': member.joined_date.strftime('%Y-%m-%d') if member.joined_date else '',
                'projects': member.projects,
                'avatar_url': member.avatar.url if member.avatar else '',
            }
        })
    except Member.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Member not found'
        })



