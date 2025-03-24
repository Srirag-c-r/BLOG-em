from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Max, Count, Sum, Q
from .models import User, BlogPost, Comment
from django.utils import timezone
from datetime import timedelta
from .forms import BlogPostForm

# Create your views here.

def home(request):
    # Get latest 3 blog posts
    latest_posts = BlogPost.objects.all()[:3]
    
    # Get active bloggers (users who have posted in the last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    active_bloggers = User.objects.filter(
        blog_posts__created_at__gte=thirty_days_ago
    ).annotate(
        latest_post_date=Max('blog_posts__created_at')
    ).distinct().order_by('-latest_post_date')[:5]
    
    return render(request, 'index.html', {
        'latest_posts': latest_posts,
        'active_bloggers': active_bloggers
    })

def about(request):
    return render(request, 'about.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        email = request.POST['email']
        full_name = request.POST['full_name']
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('register')
        
        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return redirect('register')
        
        user = User.objects.create_user(
            username=username,
            password=password1,
            email=email,
            full_name=full_name
        )
        login(request, user)
        messages.success(request, 'Registration successful!')
        return redirect('home')
    
    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            # Set session variable to show welcome toast
            request.session['show_welcome_toast'] = True
            messages.success(request, 'Login successful!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out')
    return redirect('home')

@require_POST
def clear_welcome_toast(request):
    if 'show_welcome_toast' in request.session:
        del request.session['show_welcome_toast']
    return JsonResponse({'status': 'success'})

def blog_list(request):
    posts = BlogPost.objects.all()
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    return render(request, 'blog_list.html', {'posts': posts})

def blog_detail(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)
    comments = post.comments.all()  # Comments are already ordered by created_at due to model Meta
    return render(request, 'blog_detail.html', {
        'post': post,
        'comments': comments
    })

@login_required
@require_POST
def like_post(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        liked = False
        message = "Post unliked successfully"
    else:
        post.likes.add(request.user)
        liked = True
        message = "Post liked successfully"
    
    return JsonResponse({
        'liked': liked,
        'total_likes': post.total_likes,
        'message': message,
        'status': 'success'
    })

@login_required
@require_POST
def like_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.likes.filter(id=request.user.id).exists():
        comment.likes.remove(request.user)
        liked = False
        message = "Comment unliked successfully"
    else:
        comment.likes.add(request.user)
        liked = True
        message = "Comment liked successfully"
    
    return JsonResponse({
        'liked': liked,
        'total_likes': comment.total_likes,
        'message': message,
        'status': 'success'
    })

@login_required
@require_POST
def add_comment(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            comment = Comment.objects.create(
                content=content,
                author=request.user,
                post=post
            )
            return JsonResponse({
                'status': 'success',
                'message': 'Comment added successfully!',
                'comment_id': comment.id,
                'author': comment.author.username,
                'content': comment.content,
                'created_at': comment.created_at.strftime('%B %d, %Y %I:%M %p')
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Comment cannot be empty.'
            }, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

def author_detail(request, author_id):
    author = get_object_or_404(User, id=author_id)
    posts = BlogPost.objects.filter(author=author)
    return render(request, 'author_detail.html', {'author': author, 'posts': posts})

def blogger_detail(request, author_id):
    author = get_object_or_404(User, id=author_id)
    posts = BlogPost.objects.filter(author=author).order_by('-created_at')
    return render(request, 'blogger_detail.html', {
        'author': author,
        'posts': posts
    })

def blogger_list(request):
    # Get all users who have published at least one blog post
    bloggers = User.objects.filter(blog_posts__isnull=False).distinct().order_by('username')
    return render(request, 'blogger_list.html', {'bloggers': bloggers})

@login_required
def post_create(request):
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Blog post created successfully!')
            return JsonResponse({
                'status': 'success',
                'message': 'Blog post created successfully!',
                'redirect_url': f'/blog/{post.id}/'
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Please correct the errors in the form.',
                'errors': form.errors
            }, status=400)
    else:
        form = BlogPostForm()
    
    return render(request, 'blog_form.html', {
        'form': form,
        'title': 'Create New Blog Post',
        'button_text': 'Create Post'
    })

@login_required
def post_edit(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)
    
    if request.user != post.author:
        return JsonResponse({
            'status': 'error',
            'message': 'You can only edit your own posts!'
        }, status=403)
    
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return JsonResponse({
                'status': 'success',
                'message': 'Blog post updated successfully!',
                'redirect_url': f'/blog/{post.id}/'
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Please correct the errors in the form.',
                'errors': form.errors
            }, status=400)
    else:
        form = BlogPostForm(instance=post)
    
    return render(request, 'blog_form.html', {
        'form': form,
        'title': 'Edit Blog Post',
        'button_text': 'Update Post',
        'post': post
    })

@login_required
def post_delete(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)
    
    # Check if user is the author
    if request.user != post.author:
        messages.error(request, 'You can only delete your own posts!')
        return redirect('blog_detail', post_id=post_id)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Blog post deleted successfully!')
        return redirect('my_profile')
    
    return render(request, 'post_delete_confirm.html', {
        'post': post
    })

@login_required
def my_profile(request):
    user = request.user
    posts = BlogPost.objects.filter(author=user).order_by('-created_at')
    
    # Calculate statistics using efficient database queries
    total_posts = posts.count()
    total_comments = Comment.objects.filter(author=user).count()
    total_likes_received = BlogPost.objects.filter(author=user).annotate(
        like_count=Count('likes')
    ).aggregate(total_likes=Sum('like_count'))['total_likes'] or 0

    # Handle profile picture upload
    if request.method == 'POST' and 'profile_picture' in request.FILES:
        user.profile_picture = request.FILES['profile_picture']
        user.save()
        return JsonResponse({
            'status': 'success',
            'message': 'Profile picture updated successfully!'
        })

    # Paginate posts
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)

    return render(request, 'my_profile.html', {
        'posts': posts,
        'total_posts': total_posts,
        'total_comments': total_comments,
        'total_likes_received': total_likes_received,
    })

@login_required
@require_POST
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    
    # Check if user is either comment author or blog post author
    if request.user == comment.author or request.user == comment.post.author:
        comment.delete()
        return JsonResponse({
            'status': 'success',
            'message': 'Comment deleted successfully!'
        })
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'You do not have permission to delete this comment.'
        }, status=403)

def search(request):
    query = request.GET.get('q', '')
    
    if query:
        # Search in blog posts
        blog_results = BlogPost.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(author__username__icontains=query)
        ).distinct()
        
        # Search in user profiles
        user_results = User.objects.filter(
            Q(username__icontains=query) |
            Q(full_name__icontains=query) |
            Q(email__icontains=query)
        ).distinct()
    else:
        blog_results = BlogPost.objects.none()
        user_results = User.objects.none()
    
    context = {
        'query': query,
        'blog_results': blog_results,
        'user_results': user_results,
        'total_results': len(blog_results) + len(user_results)
    }
    
    return render(request, 'search_results.html', context)

@login_required
@require_POST
def save_post(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)
    if post in request.user.saved_posts.all():
        request.user.saved_posts.remove(post)
        saved = False
        message = 'Post removed from bookmarks'
    else:
        request.user.saved_posts.add(post)
        saved = True
        message = 'Post saved to bookmarks'
    
    return JsonResponse({
        'status': 'success',
        'message': message,
        'saved': saved
    })

@login_required
def saved_posts(request):
    saved = request.user.saved_posts.all().order_by('-created_at')
    return render(request, 'saved_posts.html', {
        'saved_posts': saved,
        'title': 'Saved Posts'
    })
