from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Task', '0005_project'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinfo',
            name='display_name',
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AddField(
            model_name='userinfo',
            name='bio',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='userinfo',
            name='location',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='userinfo',
            name='timezone',
            field=models.CharField(blank=True, default='UTC', max_length=50),
        ),
        migrations.AddField(
            model_name='userinfo',
            name='email_notifications',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='userinfo',
            name='push_notifications',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='userinfo',
            name='task_reminders',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='userinfo',
            name='mention_notifications',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='userinfo',
            name='weekly_digest',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='userinfo',
            name='two_factor_enabled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='userinfo',
            name='quiet_hours_start',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userinfo',
            name='quiet_hours_end',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userinfo',
            name='theme',
            field=models.CharField(default='light', max_length=20),
        ),
        migrations.AddField(
            model_name='userinfo',
            name='accent_color',
            field=models.CharField(default='#3b82f6', max_length=7),
        ),
        migrations.AddField(
            model_name='userinfo',
            name='font_size',
            field=models.CharField(default='medium', max_length=10),
        ),
        migrations.AddField(
            model_name='userinfo',
            name='compact_mode',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='userinfo',
            name='show_animations',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='userinfo',
            name='profile_visibility',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='userinfo',
            name='activity_status',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='userinfo',
            name='search_indexing',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='userinfo',
            name='webhook_url',
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name='userinfo',
            name='webhook_events',
            field=models.TextField(blank=True, default='Task Created,Task Completed'),
        ),
        migrations.AddField(
            model_name='userinfo',
            name='allow_invitations',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='userinfo',
            name='public_team_profile',
            field=models.BooleanField(default=True),
        ),
    ]
