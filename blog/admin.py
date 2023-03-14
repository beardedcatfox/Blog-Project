import csv

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.http import HttpResponse
from django.urls import reverse

from .models import Author, Comment, Post
from .tasks import send_user_email


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_superuser', 'birth_date', 'location')
    list_filter = ('is_staff', 'date_joined', 'last_login', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'profile_photo', 'bio', 'birth_date',
                                      'location')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    actions = ['make_inactive', 'make_active']

    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)

    make_inactive.short_description = "Make selected authors inactive"

    def make_active(self, request, queryset):
        queryset.update(is_active=True)

    make_active.short_description = "Make selected authors active"


admin.site.register(Author, CustomUserAdmin)


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'is_published', 'published_date')
    list_filter = ('is_published', 'published_date', 'owner')
    search_fields = ('title', 'short_description', 'full_description')
    actions = ['make_published', 'make_unpublished', 'export_selected_posts']

    def make_published(self, request, queryset):
        queryset.update(is_published=True)

    def make_unpublished(self, request, queryset):
        queryset.update(is_published=False)

    def export_selected_posts(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="posts.csv"'
        writer = csv.writer(response)
        writer.writerow(['Published Date', 'Owner', 'Title', 'short_description', 'full_description'])
        for post in queryset:
            writer.writerow([post.published_date, post.owner.username, post.title, post.short_description,
                             post.full_description])
        return response


admin.site.register(Post, PostAdmin)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'is_published', 'published_date')
    list_filter = ('is_published', 'published_date')
    search_fields = ('post__title', 'author', 'text')
    actions = ['make_published', 'make_unpublished', 'export_selected_comments']

    def save_model(self, request, obj, form, change):
        if 'is_published' in form.changed_data:
            if obj.is_published:
                post_owner_email = obj.post.owner.email
                post_url = reverse('post_detail', args=[obj.post.id])
                subject = f'New comment on your post "{obj.post.title}"'
                message = f'Hi, {obj.post.owner.username}! You have a new comment on your post "{obj.post.title}".\n\n'
                message += f'Author: {obj.author}\n'
                message += f'Text: {obj.text}\n'
                message += f'Link: {post_url}#comment-{obj.id}'
                send_user_email.delay(obj.post.id, obj.id)

        super().save_model(request, obj, form, change)

    def make_published(self, request, queryset):
        count = 0
        for comment in queryset:
            if not comment.is_published:
                comment.is_published = True
                comment.save()
                send_user_email.delay(comment.post.id, comment.id)
                count += 1
        self.message_user(request,
                          f'{count} Comments have been marked as published and notifications have been sent')

    make_published.short_description = "Mark selected comments as published and send notifications"

    def make_unpublished(self, request, queryset):
        queryset.update(is_published=False)

    make_unpublished.short_description = "Mark selected comments as unpublished"

    def export_selected_comments(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="comments.csv"'
        writer = csv.writer(response)
        writer.writerow(['Post', 'Author', 'Published Date'])
        for comment in queryset:
            writer.writerow([comment.post.title, comment.author, comment.published_date])
        return response


admin.site.register(Comment, CommentAdmin)
