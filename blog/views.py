from django.db import models
from django.shortcuts import get_object_or_404, render

# Create your views here.
from django.http import HttpResponse
from .models import Category, Post, Tag
import markdown
import re
from markdown.extensions.toc import TocExtension
from django.utils.text import slugify

# def index(requset):
#     return HttpResponse("欢迎访问我的博客首页")

# def index(request):
#     return render(request,"blog/index.html",context={
#         "title":"我的博客首页",
#         "welcome":"欢迎访问我的博客首页"
#     })

def index(request):
    post_list = Post.objects.all().order_by("-created_time")
    return render(request,"blog/index.html",context={"post_list":post_list})

def detail(request,pk):
    post = get_object_or_404(Post,pk=pk)
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

    return render(request,"blog/detail.html",context={"post":post})

def archive(request,year,month):
    post_list = Post.objects.filter(created_time__year=year,
                                    created_time__month=month
    ).order_by("-created_time")
    return render(request,"blog/index.html",context={"post_list":post_list})

def category(request,pk):
    cate = get_object_or_404(Category,pk=pk)
    post_list = Post.objects.filter(category=cate).order_by("-created_time")
    return render(request,"blog/index.html",context={"post_list":post_list})

def tag(request,pk):
    t = get_object_or_404(Tag,pk=pk)
    post_list = Post.objects.filter(tags=t).order_by("-created_time")
    return render(request,"blog/index.html",context={"post_list":post_list})