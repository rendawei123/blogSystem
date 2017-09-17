from django.shortcuts import render, HttpResponse, redirect
from django.contrib import auth   # 引入auth类
from blog import settings
from myblog import forms
import json
from myblog.models import UserInfo
from myblog import models
import datetime
from django.db.models import F
# Create your views here.


def index(request, **kwargs):
    # print(kwargs)   # myblog下的urls下的?P<type_id>\d+)中的type_id 和\d+会以键值对的形式传入到kwargs中
    current_home_page_id = int(kwargs.get('home_page_id', 0))  # 注意添加默认值
    # print(current_home_page_id)
    # print(type(current_home_page_id))
    article_list = models.Article.objects.all()
    category_list = models.Category.objects.all()
    return render(request, 'index.html', {
        'current_home_page_id': current_home_page_id,
        'article_list': article_list,
        'category_list': category_list
    })


def log_in(request):
    print(request.path)
    local_path = request.path.replace('/login/', '')
    print(local_path)
    if request.is_ajax():
        print(local_path)

        user = request.POST.get('user')
        pwd = request.POST.get('pwd')
        valid = request.POST.get('valid')
        valid_s = request.session['valid_code']  # 因为验证码发送的时候是添加进session中发送的
        # print(request.method)
        # print(user, pwd, valid, valid_s)

        # 判断user表里面的和传过来的是否一致（自带功能）
        u = auth.authenticate(username=user, password=pwd)

        msg_dict = {'user': None, 'error': ''}
        print(msg_dict)
        if valid == valid_s:
            if u:  # 如果登录成功
                auth.login(request, u)  # 借助cook 和session 实现登录
                msg_dict['user'] = u.username
            else:  # 如果登录失败
                msg_dict['error'] = '用户名或密码错误'

        else:
            msg_dict['error'] = '验证码错误'

        return HttpResponse(json.dumps(msg_dict))

    else:

        print(request.method)
        return render(request, 'login.html', locals())


def log_out(request):
    local_path = request.path.replace('/logout/', '')
    print(local_path)
    auth.logout(request)
    return redirect(local_path+'/')


def reg(request):
    if request.method == 'POST':
        # return HttpResponse('1')
        form_obj = forms.RegForm(request, request.POST)  # 实例化form对象
        response = {'flag': False, 'errors': ''}  # 将结果以字典的形式发过去
        # 如果是正确的,id_valid返回的是一个布尔值，所有规则符合了返回True
        if form_obj.is_valid():
            # 打印全部正确信息
            print(form_obj.cleaned_data)  # {'username':klj, 'password': lkj,...}
            username = form_obj.cleaned_data['username']
            password = form_obj.cleaned_data['password']
            email = form_obj.cleaned_data['email']
            file_obj = request.FILES.get('img')
            # 写入UserInfo表
            UserInfo.objects.create_user(
                username=username,
                password=password,
                email=email,
                avatar=file_obj
            )
            response['flag'] = True
        else:
            #  取出错误信息，传到模板进行渲染,错误信息是一个字典，里面的一组组键值对存储的是
            #  每一个的错误信息，建是username，值为错误信息
            error = form_obj.errors
            print(form_obj.cleaned_data)
            print(error)
            response['errors'] = error
            print('1')

        return HttpResponse(json.dumps(response))

    form_obj = forms.RegForm(request)
    return render(request, 'reg.html', {'form_obj': form_obj})


def func_class(request):
    """
    返回一个模板能够认识的上下文对象
    """
    return {'func': settings.FUNCTION}


# 验证码
def valid_code(request):
    # 方式1
    # with open('myblog/static/img/valid.png', 'rb') as f:
    #     data = f.read()
    #
    # return HttpResponse(data)

    # 方式2
    # 导入模块
    # from PIL import Image
    # 创建图片
    # img = Image.new(mode='RGB', size=(120, 30), color=(50, 120, 255))
    # 保存在本地
    # with open('code.png', 'wb') as f:
    #     img.save(f, format='png')
    # 读取文件
    # with open('code.png', 'rb') as f_read:
    #     data = f_read.read()

    # 发送文件
    # return HttpResponse(data)

    # 方式3 内存方法
    # 导入io模块
    from io import BytesIO
    import random
    # 实例化文件对象
    f = BytesIO()
    # 导入图片，画笔，字体模块
    from PIL import Image, ImageDraw, ImageFont
    # 创建图片 参数为颜色模式，大小，颜色（随机的三个数）
    img = Image.new(mode='RGB', size=(120, 30), color=(
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255)
    ))

    # 创建画笔
    draw = ImageDraw.Draw(img, mode='RGB')

    # 创建字体 参数为字体路径，字体大小
    font = ImageFont.truetype('myblog/static/dist/fonts/Bradley Hand Bold.ttf', 28)

    # 创建随机颜色
    color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    # 写文本,参数分别为位置，文本(随机)，颜色(随机)，字体, 循环5次，每次写一个字符，一次添加进列表
    code_list = []
    for i in range(5):
        # 创建随机字符
        char = random.choice([chr(random.randint(65, 90)), str(random.randint(1, 9))])
        code_list.append(char)
        draw.text([i*24, 0], char, color, font=font)

    # 使用画笔写文本到图片
    # draw.text([20, 0], 'python', color)

    # 保存图片到内存里面
    img.save(f, 'png')
    # 从内存里读取数据
    data = f.getvalue()
    # 将保存的验证码转化成字符串
    valid_codes = ''.join(code_list)
    # 将验证码字符串添加到session中进行发送
    request.session['valid_code'] = valid_codes
    # 发送数据
    return HttpResponse(data)


def home_site(request, user_site, **kwargs):
    user = UserInfo.objects.filter(username=user_site)

    # 如果没有这个用户
    if not user:
        return render(request, 'not_find.html')
    # 获取当前博客对象
    current_blog = models.Blog.objects.filter(user=user)

    # 获取当前用户文章
    article_list = models.Article.objects.filter(blog=current_blog)

    # 获取当前站点的所有分类
    category_list = models.Category.objects.filter(blog=current_blog)

    # 分组获取每个分类的个数
    from django.db.models import Count
    category_result_list = models.Article.objects.filter(blog=current_blog)\
        .values_list('category__title', 'category__nid').annotate(Count('nid'))

    # 获取当前站点的所有标签
    tag_list = models.Tag.objects.filter(blog=current_blog)

    # 查询对应的标签以及对应的文章个数
    tag_result_list = models.Article.objects.filter(blog=current_blog)\
        .values_list('tags__title', 'tags__nid').annotate(Count('nid'))
    date_list = models.Article.objects.archive(blog=current_blog)
    # now_time = datetime.datetime.today()
    # print(now_time)

    # 判断使用哪一种分类来分别显示每一类的文章，也就是更改article_list
    print(kwargs)
    if kwargs.get('condition'):
        condition = kwargs.get('condition')
        para = kwargs.get('para')
        if condition == 'category':
            article_list = models.Article.objects.filter(blog=current_blog, category_id=para)
        elif condition == 'tags':
            print(kwargs)
            article_list = models.Article.objects.filter(blog=current_blog, tags__article2tag__nid=para)

    return render(request, 'home_site.html', {
        'article_list': article_list,
        'user': user[0],
        'category_result_list': category_result_list,
        'tag_result_list': tag_result_list,
        'date_list': date_list
    })


# 文章内容
def article_detail(request, user_site, article_id):
    blog_obj = models.Blog.objects.filter(site=user_site).first()
    article_obj = models.Article.objects.filter(nid=article_id).first()
    comment_list = models.Comment.objects.filter(article_id=article_id)

    # 渲染多级评论部分
    # if request.is_ajax():
    #     comment_list = models.Comment.objects.filter(article_id=article_id).values('nid', 'content', 'parent_id_id')
    #     print(comment_list)
    #
    #     import collections
    #     # 创建有序字典
    #     comment_dict = collections.OrderedDict()
    #     for each_comment in comment_list:
    #         each_comment['children_comments'] = []
    #         comment_dict[each_comment['nid']] = each_comment
    #
    #     ret = []
    #     # print(comment_dict)
    #     for each in comment_dict:
    #         # print(each)
    #         if comment_dict[each]['parent_id_id']:
    #             pid = comment_dict[each]['parent_id_id']
    #             # print(each, pid)
    #             # print(comment_dict[pid])
    #             comment_dict[pid]['children_comments'].append(comment_dict[each])
    #         else:
    #             print(each, '123')
    #             ret.append(comment_dict[each])
    #     return HttpResponse(json.dumps(ret))

    return render(request, 'article_detail.html', locals())


# 点赞
def poll(request):
    user_id = request.user.nid
    article_id = request.POST.get('article_id')
    response = {'flag':True}
    if models.ArticleUpDown.objects.filter(user_id=user_id, article_id=article_id):
        response['flag'] = False
    else:
        models.ArticleUpDown.objects.create(user_id=user_id, article_id=article_id)

        models.Article.objects.filter(nid=article_id).update(up_count=F('up_count')+1)
    return HttpResponse(json.dumps(response))


# 评论
def comment(request):
    user_id = request.user.nid
    article_id = request.POST.get('article_id')
    comment_content = request.POST.get('comment_content')
    comment_obj = models.Comment.objects.create(
        article_id=article_id,
        content=comment_content,
        user_id=user_id
    )
    models.Article.objects.filter(nid=article_id).update(comment_count=F('comment_count') + 1)
    comment_create_time = comment_obj.create_time
    comment_avatar = comment_obj.user.avatar.url
    print(comment_avatar)
    comment_nickname = comment_obj.user.nickname
    comment_nid = comment_obj.nid
    comment_response = {
        'comment_avatar': comment_avatar,
        'comment_create_time': str(comment_create_time)[:16],
        'comment_nickname': comment_nickname,
        'comment_nid': comment_nid
    }

    return HttpResponse(json.dumps(comment_response))


def comment1(request):
    user_id = request.user.nid
    article_id = request.POST.get('article_id')
    comment_content = request.POST.get('comment_content')
    parent_comment_id = request.POST.get('parent_comment_id')
    models.Comment.objects.create(
        article_id=article_id,
        content=comment_content,
        user_id=user_id,
        parent_id_id=parent_comment_id
    )
    models.Article.objects.filter(nid=article_id).update(comment_count=F('comment_count') + 1)
    return HttpResponse('ok')


# 后台管理
def back(request):
    # 获取当前登录的用户
    user = request.user
    current_blog = models.Blog.objects.filter(user=user)[0]
    print(user.username, current_blog.site)
    article_list = models.Article.objects.filter(blog=current_blog)

    return render(request, 'back.html', {
        'article_list': article_list,
    })


# 写文章
def write_article(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('article_content')
        print(title, content)
        return render(request, 'show_content.html', {'title': title, 'content': content})

    return render(request, 'write_article.html')


# 上传文件
def upload_file(request):

    file_obj = request.FILES.get('imgFile')
    file_name = file_obj.name

    with open('myblog/media/upload/img/'+file_name, 'wb') as f:
        for chunk in file_obj.chunks():
            f.write(chunk)

    response_put = {
        'error': 0,
        'url': 'media/upload/img' + file_name
    }

    return HttpResponse(json.dumps(response_put))
