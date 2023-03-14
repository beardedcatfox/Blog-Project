from celery import shared_task

from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse

from .models import Comment, Post


@shared_task
def send_user_email(post_id, comment_id):
    post = Post.objects.get(id=post_id)
    comment = Comment.objects.get(id=comment_id)
    if comment.is_published:
        post_owner_email = post.owner.email
        post_url = reverse('post_detail', args=[post.id])
        subject = f'New comment on your post "{post.title}"'
        message = f'Hi, {post.owner.username}! You have a new comment on your post "{post.title}".\n\n'
        message += f'Author: {comment.author}\n'
        message += f'Text: {comment.text}\n'
        message += f'Link: {post_url}#comment-{comment_id}'
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [post_owner_email], fail_silently=False)


@shared_task
def send_new_post_notification(post_id):
    post_url = reverse('post_detail', args=[post_id])
    post_absolute_url = post_url
    message = f"New post added: {post_absolute_url}"
    send_mail(
        subject="New post added",
        message=message,
        from_email="notifications@blog.com",
        recipient_list=["admin@noreply.com"],
        fail_silently=False,
    )


@shared_task
def send_new_comment_notification(comment_id):
    comment = Comment.objects.get(pk=comment_id)
    post_url = reverse('post_detail', args=[comment.post.id])
    post_absolute_url = post_url
    message = f"New comment to post ({post_absolute_url})"
    send_mail(
            'New comment created',
            message,
            'noreply@example.com',
            ['admin@noreply.com'],
            fail_silently=False,
        )


@shared_task
def send_contact_email(name, from_email, message):
    subject = 'Feedback from {}'.format(name)
    body = 'You have new feedback from {} ({})\n\n{}'.format(name, from_email, message)
    send_mail(subject, body, 'notifications@blog.com', ['admin@noreply.com'], fail_silently=False)
