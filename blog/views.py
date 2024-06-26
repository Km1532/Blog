from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView
from django.core.mail import send_mail, BadHeaderError
from .forms import ContactForm, AddPostForm, CustomUserCreationForm, RegisterUserForm, LoginUserForm, CommentForm, EditProfileForm
from .models import Blog, Comment, Like, Category, CustomUser
from .utils import menu

class BlogHome(ListView):
    model = Blog
    template_name = 'index.html'
    context_object_name = 'posts'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = {'title': "Головна сторінка"}
        context = {**context, **c_def, **menu(self.request)}
        return context

    def get_queryset(self):
        return Blog.objects.filter(is_published=True).select_related('cat')

def about(request):
    contact_list = Blog.objects.all()
    paginator = Paginator(contact_list, 3)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'about.html', {'page_obj': page_obj, 'menu': menu(request), 'title': 'Про сайт'})

class AddPage(CreateView):
    form_class = AddPostForm
    template_name = 'addpage.html'

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            sender = form.cleaned_data['sender']
            cc_myself = form.cleaned_data['cc_myself']

            recipients = ['admin@example.com']
            if cc_myself:
                recipients.append(sender)

            try:
                send_mail(subject, message, sender, recipients)
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return redirect('home')
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form, 'menu': menu(request), 'title': 'Зворотній зв\'язок'})

class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('home')

class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'login.html'

    def get_success_url(self):
        return reverse_lazy('home')

def logout_user(request):
    logout(request)
    return redirect('login')

class ShowPost(DetailView):
    model = Blog
    template_name = 'post.html'
    slug_url_kwarg = 'post_slug'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.select_related('user')
        context['form'] = CommentForm()
        return context

class WomenCategory(ListView):
    model = Blog
    template_name = 'index.html'
    context_object_name = 'posts'
    allow_empty = False

    def get_queryset(self):
        return Blog.objects.filter(cat__slug=self.kwargs['cat_slug'], is_published=True).select_related('cat')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = {'title': 'Категорія - ' + str(context['posts'][0].cat), 'cat_selected': context['posts'][0].cat_id}
        context = {**context, **c_def, **menu(self.request)}
        return context

@login_required
def add_comment(request, post_slug):
    post = get_object_or_404(Blog, slug=post_slug)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            return redirect(post.get_absolute_url())
    else:
        form = CommentForm()
    return render(request, 'add_comment.html', {'form': form, 'post': post})

@login_required
def add_like(request, post_slug):
    post = get_object_or_404(Blog, slug=post_slug)
    Like.objects.get_or_create(post=post, user=request.user)
    return redirect(post.get_absolute_url())

@login_required
def add_like_comment(request, post_slug, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, post__slug=post_slug)
    comment.likes.add(request.user)
    return redirect(comment.post.get_absolute_url())

@login_required
def edit_comment(request, post_slug, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, post__slug=post_slug, user=request.user)
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect(comment.post.get_absolute_url())
    else:
        form = CommentForm(instance=comment)
    return render(request, 'edit_comment.html', {'form': form, 'post': comment.post})

@login_required
def delete_comment(request, post_slug, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, post__slug=post_slug, user=request.user)
    if request.method == 'POST':
        comment.delete()
        return redirect(comment.post.get_absolute_url())
    return render(request, 'delete_comment.html', {'comment': comment})

def soon_page(request):
    return render(request, 'soon.html', {'menu': menu(request), 'title': 'Скоро'})

@login_required
def profile(request):
    return render(request, 'profile.html', {'menu': menu(request), 'title': 'Профіль'})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            # Додаткова перевірка наявності профілю
            if hasattr(request.user, 'profile'):
                request.user.profile.save()
            return redirect('profile')
    else:
        form = EditProfileForm(instance=request.user)
    return render(request, 'edit_profile.html', {'form': form, 'menu': menu(request), 'title': 'Редагувати профіль'})

class UserProfile(DetailView):
    model = CustomUser
    template_name = 'profile.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    context_object_name = 'user_profile'

def pageNotFound(request, exception):
    return HttpResponseNotFound('<h1>Сторінку не знайдено</h1>')
