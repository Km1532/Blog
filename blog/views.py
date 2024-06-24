from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail, BadHeaderError
from .forms import ContactForm, AddPostForm, RegisterUserForm, LoginUserForm,CommentForm
from .models import Blog, Comment, Like, Category
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
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = {'title': "Додавання статті"}
        context = {**context, **c_def, **menu(self.request)}
        return context


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            sender = form.cleaned_data['sender']
            cc_myself = form.cleaned_data['cc_myself']

            recipients = ['sandy.tuor.2024@gmail.com']

            try:
                send_mail(subject, message, sender, recipients, cc_myself)
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return HttpResponse('Дякуємо за ваше повідомлення! Очікуйте на відповідь.')

    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form, 'menu': menu(request), 'title': 'Зворотній зв\'язок'})


def pageNotFound(request, exception):
    return HttpResponseNotFound('<h1>Сторінка не знайдена</h1>')


class ShowPost(DetailView):
    model = Blog
    template_name = 'post.html'
    slug_url_kwarg = 'post_slug'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = {'title': str(context['post'])}
        context = {**context, **c_def, **menu(self.request)}
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
        c = Category.objects.get(slug=self.kwargs['cat_slug'])
        c_def = {'title': 'Категорія - ' + str(c.name), 'cat_selected': c.pk}
        context = {**context, **c_def, **menu(self.request)}
        return context


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'register.html'
    success_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = {'title': "Реєстрація"}
        context = {**context, **c_def, **menu(self.request)}
        return context

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('home')


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = {'title': "Авторизація"}
        context = {**context, **c_def, **menu(self.request)}
        return context

    def get_success_url(self):
        return reverse_lazy('home')


@login_required
def logout_user(request):
    logout(request)
    return redirect('login')


@login_required
def add_comment(request, post_slug):
    post = Blog.objects.get(slug=post_slug)
    if request.method == 'POST':
        content = request.POST['content']
        Comment.objects.create(post=post, user=request.user, content=content)
    return redirect('post', post_slug=post_slug)


@login_required
def add_like(request, post_slug):
    post = get_object_or_404(Blog, slug=post_slug)

    if request.method == 'POST':
        if post.likes.filter(user=request.user).exists():
            post.likes.filter(user=request.user).delete()
        else:
            Like.objects.create(post=post, user=request.user)

    return redirect('post', post_slug=post.slug)

@login_required
def add_like_comment(request, post_slug, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.likes.filter(id=request.user.id).exists():
        comment.likes.remove(request.user)
    else:
        comment.likes.add(request.user)
    return redirect('post', post_slug=post_slug)

@login_required
def edit_comment(request, post_slug, comment_id):
    post = get_object_or_404(Blog, slug=post_slug)
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('post', post_slug=post_slug)
    else:
        form = CommentForm(instance=comment)

    return render(request, 'edit_comment.html', {'form': form, 'post': post, 'comment': comment})

@login_required
def delete_comment(request, post_slug, comment_id):
    post = get_object_or_404(Blog, slug=post_slug)
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)

    if request.method == 'POST':
        comment.delete()
        return redirect('post', post_slug=post_slug)

    return render(request, 'delete_comment.html', {'post': post, 'comment': comment})   


def soon_page(request):
    return render(request, 'soon_page.html')