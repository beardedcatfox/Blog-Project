from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import Author, Comment, Post


class AuthorRegisterForm(UserCreationForm):
    profile_photo = forms.ImageField(required=False)

    class Meta:
        model = Author
        fields = ['username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'profile_photo']


class AuthorChangeForm(UserChangeForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = Author
        fields = ('username', 'email', 'first_name', 'last_name')


class AuthorProfileForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ('profile_photo', 'bio', 'birth_date', 'location',)
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }


class ContactForm(forms.Form):
    name = forms.CharField(label='Name', max_length=100)
    email = forms.EmailField(label='Email', max_length=100)
    message = forms.CharField(label='Message', widget=forms.Textarea)


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'short_description', 'full_description', 'image', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'short_description': forms.TextInput(attrs={'class': 'form-control'}),
            'full_description': forms.Textarea(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control-file'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CommentForm(forms.ModelForm):
    author = forms.CharField(max_length=200, required=False)
    text = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Comment
        fields = ['author', 'text']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user and self.user.is_authenticated:
            self.fields['author'].widget = forms.HiddenInput()
            self.fields['author'].initial = 'comment as ' + self.user.username
        else:
            self.fields['author'].required = True

    def clean_author(self):
        author = self.cleaned_data['author']
        if not self.user or not self.user.is_authenticated:
            author = 'Guest ' + author
        return author

    def save(self, commit=True):
        comment = super().save(commit=False)
        if not comment.author:
            if self.user and self.user.is_authenticated:
                comment.author = self.user.username
            else:
                comment.author = 'Anonymous'
        if commit:
            comment.save()
        return comment


class PostEditForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'short_description', 'full_description', 'image', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'short_description': forms.TextInput(attrs={'class': 'form-control'}),
            'full_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class UnPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'is_published']
