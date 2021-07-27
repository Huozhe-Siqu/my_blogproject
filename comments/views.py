from django.shortcuts import render,get_object_or_404,redirect
from blog.models import Post
from django.views.decorators.http import require_POST
from .forms import CommentForm
from django.contrib import messages
# Create your views here.
@require_POST
def comment(request,post_pk):
    # 先获取被评论的文章，因为后面需要吧评论和被评论的文章关联起来
    # 这里我们使用django提供的一个快捷函数get_object_or_404
    post = get_object_or_404(Post,pk=post_pk)

    # django将用户提交的数据封装在request.POST中，这是一个类字典对象
    # 我们利用这些数据构造了CommentForm的实例，这样就生成了一个绑定了用户提交数据的表单
    form = CommentForm(request.POST)

    # 当调用form.is_valid()方法时，django自动帮我们检查表单是否符合格式要求
    if form.is_valid():
        # 检查到数据是合法的，调用表单的save方法保存数据到数据库
        # commit=False的作用是仅仅利用表单的数据生成Comment模型类的实例，但还不保存评论数据到数据库
        comment = form.save(commit=False)

        # 将评论和被评论的文章关联起来
        comment.post = post

        # 最终将评论数据保存到数据库中，调用模型实例的save方法
        comment.save()

        # 当数据陈工保存到数据库之后，评论发表成功
        messages.add_message(request,messages.SUCCESS,"发表评论成功！",extra_tags="success")

        # 重定向到post的详情页，实际上当redirect函数接受一个模型的实例时，它会调用这个模型实例的get_absolute_url方法
        # 然后充定向到get_absolute_url方法返回的url
        return redirect(post)

    # 检查到数据不合法，我们渲染一个预览页面，用于展示表单错误
    # 注意这个被评论的文章post也传给了模板，因为我们需要根据post来生成表单的提交地址
    context = {
        "post":post,
        "form":form,
    }
    # 评论失败，发送失败消息
    messages.add_message(request,messages.ERROR,"评论发表失败！请修改表单中的错误后重新提交。",extra_tags="danger")
    return render(request,"comments/preview.html",context=context)