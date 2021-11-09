from django.db import models
from django.shortcuts import get_object_or_404, render

# Create your views here.
from django.http import HttpResponse, response
from .models import Category, Post, Tag
import markdown
import re
from markdown.extensions.toc import TocExtension
from django.utils.text import slugify
from django.views.generic import ListView,DetailView

# def index(requset):
#     return HttpResponse("欢迎访问我的博客首页")

# def index(request):
#     return render(request,"blog/index.html",context={
#         "title":"我的博客首页",
#         "welcome":"欢迎访问我的博客首页"
#     })

# def index(request):
#     post_list = Post.objects.all().order_by("-created_time")
#     return render(request,"blog/index.html",context={"post_list":post_list})
class IndexView(ListView):
    model = Post
    template_name = "blog/index.html"
    context_object_name = "post_list"

# def detail(request,pk):
#     post = get_object_or_404(Post,pk=pk)

#     # 阅读量 +1
#     post.increase_views()

#     md = markdown.Markdown(extensions=[
#                                         "markdown.extensions.extra",
#                                         "markdown.extensions.codehilite",
#                                         # "markdown.extensions.toc",
#                                         # "markdown.extensions.fenced_code",
#                                         TocExtension(slugify=slugify),
#                                     ]
#     )
#     post.body = md.convert(post.body)

#     # 空目录的处理
#     m = re.search(r'<div class="toc">\s*<ul>(.*)</ul>\s*</div>', md.toc, re.S)
#     post.toc = m.group(1) if m is not None else ''

#     return render(request,"blog/detail.html",context={"post":post})
class PostDetailView(DetailView):
    # 这些属性的含义和ListView是一样的
    model = Post
    template_name = "blog/detail.html"
    context_object_name = "post"

    def get(self, request, *args, **kwargs) -> HttpResponse:
        # 覆写get方法的目的是因为每当文章被访问一次，就得将文章阅读量 +1
        # get方法返回的是一个HttpResponse实例
        # 之所以需要先调用父类的get方法，是因为只有当get方法被调用后，才有self.object属性，其值为Post模型实例，即被访问的文章post
        response = super(PostDetailView,self).get(request, *args, **kwargs)

        # 将文章阅读量 +1
        # 注意self.object的值就是被访问的post
        self.object.increase_views()

        # 视图必须返回一个HttpResponse对象
        return response

    def get_object(self,queryset=None):
        # 覆写get_object方法的目的是因为需要对post的body值进行渲染
        post = super().get_object(queryset=None)
        md = markdown.Markdown(extensions=[
                                    "markdown.extensions.extra",
                                    "markdown.extensions.codehilite",
                                    # "markdown.extensions.toc",
                                    # "markdown.extensions.fenced_code",
                                    TocExtension(slugify=slugify),
                                ]
        )
        post.body = md.convert(post.body)

        # 空目录的处理
        m = re.search(r'<div class="toc">\s*<ul>(.*)</ul>\s*</div>', md.toc, re.S)
        post.toc = m.group(1) if m is not None else ''

        return post

def archive(request,year,month):
    post_list = Post.objects.filter(created_time__year=year,
                                    created_time__month=month
    ).order_by("-created_time")
    return render(request,"blog/index.html",context={"post_list":post_list})

# def category(request,pk):
#     cate = get_object_or_404(Category,pk=pk)
#     post_list = Post.objects.filter(category=cate).order_by("-created_time")
#     return render(request,"blog/index.html",context={"post_list":post_list})
class CategoryView(ListView):
    model = Post
    template_name = "blog/index.html"
    context_object_name = "post_list"

    # 复写
    def get_queryset(self):
        cate = get_object_or_404(Category,pk=self.kwargs.get("pk"))
        return super(CategoryView,self).get_queryset().filter(category=cate)

def tag(request,pk):
    t = get_object_or_404(Tag,pk=pk)
    post_list = Post.objects.filter(tags=t).order_by("-created_time")
    return render(request,"blog/index.html",context={"post_list":post_list})