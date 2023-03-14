from blog.forms import AuthorChangeForm, AuthorProfileForm, AuthorRegisterForm, CommentForm, ContactForm, PostForm
from blog.models import Author, Comment, Post

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, ListView

from .tasks import send_contact_email, send_new_comment_notification, send_new_post_notification


def register(request):
    if request.method == 'POST':
        form = AuthorRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = AuthorRegisterForm()
    return render(request, 'blog/register.html', {'form': form})


class CustomLoginView(LoginView):
    template_name = 'blog/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse('post_list')


def logout_view(request):
    logout(request)
    return redirect('post_list')


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.owner = request.user
            post.save()
            if post.is_published:
                send_new_post_notification.delay(post.pk)
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_form.html', {'form': form})


@login_required
def update_post(request, pk):
    post = get_object_or_404(Post, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.owner = request.user
            post.save()
            if post.is_published:
                send_new_post_notification.delay(post.pk)
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_form.html', {'form': form})


@login_required
def unpublished_posts(request):
    post_list = Post.objects.filter(owner=request.user, is_published=False).order_by('-published_date')
    paginator = Paginator(post_list, 10)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    return render(request, 'blog/unpublished_posts.html', {'posts': posts})


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comments = Comment.objects.filter(post=self.object, is_published=True).order_by('-published_date')
        paginator = Paginator(comments, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        context['comment_form'] = CommentForm()
        if self.object.owner == self.request.user:
            context['is_owner'] = True
        return context

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        if request.user.is_authenticated:
            form = CommentForm(request.POST, user=request.user)
        else:
            form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            send_new_comment_notification.delay(comment.id)
            return redirect('post_detail', pk=post.pk)
        context = {'comment_form': form, 'post': post}
        return render(request, 'blog/post_detail.html', context)


class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10
    queryset = Post.objects.filter(is_published=True).order_by('-published_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.request.GET.get('page')
        paginator = Paginator(self.queryset, self.paginate_by)
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        context['posts'] = posts
        return context


class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_post_list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        user = get_object_or_404(Author, username=self.kwargs.get('username'))
        return Post.objects.filter(owner=user, is_published=True).order_by('-published_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_profile'] = get_object_or_404(Author, username=self.kwargs.get('username'))
        return context


def user_profile(request, username):
    user = get_object_or_404(Author, username=username)
    return render(request, 'blog/user_profile.html', {'user': user})


@login_required
def edit_profile(request):
    if request.method == 'POST':
        user_form = AuthorChangeForm(request.POST, instance=request.user)
        profile_form = AuthorProfileForm(request.POST, request.FILES, instance=request.user)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            if not request.user.is_superuser and user.is_superuser:
                messages.error(request, 'Good try)')
                return redirect('edit_profile')
            user.save()
            profile_form.save()
            messages.success(request, 'Your profile was updated successfully!')
            return redirect('edit_profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        user_form = AuthorChangeForm(instance=request.user)
        profile_form = AuthorProfileForm(instance=request.user)
    return render(request, 'blog/edit_profile.html', {'user_form': user_form, 'profile_form': profile_form})


class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'blog/password.html'
    success_url = reverse_lazy('edit_profile')


@csrf_exempt
def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            from_email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            send_contact_email.delay(name, from_email, message)
            return JsonResponse({'form_is_valid': True})
        else:
            html_form = render_to_string('blog/contact.html', {'form': form}, request=request)
            return JsonResponse({'form_is_valid': False, 'html_form': html_form})
    else:
        form = ContactForm()
        html_form = render_to_string('blog/contact.html', {'form': form}, request=request)
        return JsonResponse({'html_form': html_form})
