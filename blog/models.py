from typing import ContextManager
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
import markdown
from django.utils.html import strip_tags
import re
from markdown.extensions.toc import TocExtension
from django.utils.text import slugify
from django.utils.functional import cached_property

# Create your models here.
class Category(models.Model):
    """
    django要求模型必须继承 models.Model类
    Category只需要一个简单的类名name类就可以啦
    charFiled制定了分类名name的数据类型，CharField是字符型
    max_length参数指定了其最大长度，超过这个长度分类名就不能被存入到数据库
    时间类型DateTimeField，整数类型IntegerField等等
    """
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "分类"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "标签"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class Post(models.Model):
    # 文章标题
    title = models.CharField("标题",max_length=70)

    # 文章正文，我们使用TextField
    # 存储比较短的字符串可以使用CharField，但是对于文章的正文来说可能会是一大段文本，因此使用TextField来存储大段文本
    body = models.TextField("正文")

    # 这两个列表分别表示文章的创建时间和最后一次修改时间，存储时间的字段用DateTimeField类型
    created_time = models.DateTimeField("创建时间",default=timezone.now)
    modified_time = models.DateTimeField("修改时间")

    # 文章摘要，可以没有文章摘要，但默认情况下CharField要求我们必须存入数据，否则会报错
    # 指定CharField的blank=True参数值就可以允许空值了
    excerpt = models.CharField("摘要",max_length=200,blank=True)

    # 这是分类和标签，分类和标签的模型我们已经定义在上面了
    # 我们在这里把文章对应的数据库表和分类，标签对应的数据库关联起来了，但是关联的形式有些不同
    # 我们对应一篇文章只能对应一个分类，但是一个分类下可以有多篇文章，所以我们使用的是ForeignKey，即一对多的关联关系
    # Djando2.0以后，Foreignkey必须传入一个on_delete参数来指定当关联的数据被删除时，被关联的数据的行为，这里我们假定当某个分类被删除时，该分类下的所有文章全部删除，因此使用models.CASCADE参数，意为级联删除
    # 对于标签来说，一篇文章可以有多个标签，同一个标签下也可能有多篇文章，所以我们使用ManyToManyField，表明这是多对多的关联关系
    # 规定文章可以没有标签，因此为标签tags指定了blank=True
    category = models.ForeignKey(Category,verbose_name="分类",on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag,verbose_name="标签",blank=True)

    # 文章作者，这里user是从django.contrib.auth.models导入的
    # 是django内置应用，专门用来处理网站用户的注册，登陆流程，user是django为我们已经写好的用户模型
    # 我们用过Foreignkey把文章和User关联起来
    # 我们规定一篇文章只能有一个作者，而一个作何可能会有多篇文章，因此这是一对多的关系
    author = models.ForeignKey(User,verbose_name="作者",on_delete=models.CASCADE)

    # 新增view字段，记录阅读量
    views = models.PositiveIntegerField(default=0,editable=False)

    class Meta:
        verbose_name = "文章"
        verbose_name_plural = verbose_name
        ordering = ["-created_time"]

    def save(self,*args,**kwargs):
        self.modified_time = timezone.now()

        # 首先实例化一个Markdown类，用于渲染body得儿文章
        # 由于摘要不需要生成文章目录，所以去掉了目录拓展
        md = markdown.Markdown(extensions=[
            "markdown.extensions.extra",
            "markdown.extensions.codehilite",
        ])

        # 先将markdown文本渲染成HTML文本
        # stripe_tags去掉HTML文本的全部HTML标签
        # 从文本摘取前54个字符赋给excerpt
        self.excerpt = strip_tags(md.convert(self.body))[:54]

        super().save(*args,**kwargs)

    def __str__(self):
        return self.title

    # 自定义get_absolute_url方法
    # 记得从django.urls中导入reverse函数
    def get_absolute_url(self):
        return reverse("blog:detail",kwargs={"pk":self.pk})

    # 自定义increase-views方法
    # 当用户访问文章，即views + 1
    def increase_views(self):
        self.views += 1
        self.save(update_fields=["views"])

    @property
    def toc(self):
        return self.rich_content.get("toc","")
    
    @property
    def body_html(self):
        return self.rich_content.get("content","")
    
    @cached_property
    def rich_content(self):
        return generate_rich_content(self.body)


def generate_rich_content(value):
    md = markdown.Markdown(extensions=[
                                "markdown.extensions.extra",
                                "markdown.extensions.codehilite",
                                # "markdown.extensions.toc",
                                # "markdown.extensions.fenced_code",
                                TocExtension(slugify=slugify),
                            ]
    )
    content = md.convert(value)

    # 空目录的处理
    m = re.search(r'<div class="toc">\s*<ul>(.*)</ul>\s*</div>', md.toc, re.S)
    toc = m.group(1) if m is not None else ''

    return {"content": content,"toc": toc}