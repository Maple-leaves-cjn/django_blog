from django.contrib.auth import authenticate, models

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, redirect, HttpResponse
from app_all import models, forms
# Create your views here.
from django.contrib import auth
from geetest import GeetestLib
import logging
from django.db.models import Count
# 生成一个logger实例，专门用来记录日志
logger = logging.getLogger(__name__)
# logger_s10 = logging.getLogger("collect")

# Create your views here.

# VALID_CODE = ""


# 自己生成验证码的登录
# def login(request):
#     # if request.is_ajax():  # 如果是AJAX请求
#     if request.method == "POST":
#         # 初始化一个给AJAX返回的数据
#         ret = {"status": 0, "msg": ""}
#         # 从提交过来的数据中 取到用户名和密码
#         username = request.POST.get("username")
#         pwd = request.POST.get("password")
#         valid_code = request.POST.get("valid_code")  # 获取用户填写的验证码
#         print(valid_code)
#         print("用户输入的验证码".center(120, "="))
#         if valid_code and valid_code.upper() == request.session.get("valid_code", "").upper():
#             # 验证码正确
#             # 利用auth模块做用户名和密码的校验
#             user = auth.authenticate(username=username, password=pwd)
#             if user:
#                 # 用户名密码正确
#                 # 给用户做登录
#                 auth.login(request, user)
#                 ret["msg"] = "/index/"
#             else:
#                 # 用户名密码错误
#                 ret["status"] = 1
#                 ret["msg"] = "用户名或密码错误！"
#         else:
#             ret["status"] = 1
#             ret["msg"] = "验证码错误"
#
#         return JsonResponse(ret)
#     return render(request, "login.html")


# 使用极验滑动验证码的登录


def index(request):
    article_list = models.Article.objects.all()
    
    return render(request, "index.html", {"article_list": article_list})


def logout(request):
    auth.logout(request)
    return redirect("/index/")


# def register(request):
#
#     # User.objects.create(username="alex", password="alexdsb")  # 不用这个
#     # User.objects.create_superuser()
#     user_obj = models.UserInfo.objects.create_user(username="ning", password="ning123456")
#     # 校验密码是否正确
#     ret = user_obj.check_password("ning123456")
#     print(ret)
#     # 修改密码
#     user_obj.set_password("ning1234")
#     user_obj.save()
#     return HttpResponse("ok")


pc_geetest_id = "b46d1900d0a894591916ea94ea91bd2c"
pc_geetest_key = "36fc3fe98530eea08dfc6ce76e3d24c4"

# 使用极验滑动验证码的登录
# 请在官网申请ID使用，示例ID不可使用


def login(request):
    # if request.is_ajax():  # 如果是AJAX请求
    if request.method == "POST":
        # 初始化一个给AJAX返回的数据
        ret = {"status": 0, "msg": ""}
        # 从提交过来的数据中 取到用户名和密码
        username = request.POST.get("username")
        pwd = request.POST.get("password")
        # 获取极验 滑动验证码相关的参数
        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        challenge = request.POST.get(gt.FN_CHALLENGE, '')
        validate = request.POST.get(gt.FN_VALIDATE, '')
        seccode = request.POST.get(gt.FN_SECCODE, '')
        status = request.session[gt.GT_STATUS_SESSION_KEY]
        user_id = request.session["user_id"]

        if status:
            result = gt.success_validate(challenge, validate, seccode, user_id)
        else:
            result = gt.failback_validate(challenge, validate, seccode)
        if result:
            # 验证码正确
            # 利用auth模块做用户名和密码的校验
            user = auth.authenticate(username=username, password=pwd)
            if user:
                # 用户名密码正确
                # 给用户做登录
                auth.login(request, user)  # 将登录用户赋值给 request.user
                ret["msg"] = "/index/"
            else:
                # 用户名密码错误
                ret["status"] = 1
                ret["msg"] = "用户名或密码错误！"
        else:
            ret["status"] = 1
            ret["msg"] = "验证码错误"

        return JsonResponse(ret)
    return render(request, "login2.html")


# 处理极验 获取验证码的视图
def get_geetest(request):
    user_id = 'test'
    gt = GeetestLib(pc_geetest_id, pc_geetest_key)
    status = gt.pre_process(user_id)
    request.session[gt.GT_STATUS_SESSION_KEY] = status
    request.session["user_id"] = user_id
    response_str = gt.get_response_str()
    return HttpResponse(response_str)


# 注册的视图函数
def register(request):
    if request.method == "POST": # ajax和form
        print(request.POST)
        print("=" * 120)
        ret = {"status": 0, "msg": ""}
        form_obj = forms.RegForm(request.POST) # 提交的数据
        print(request.POST)
        # 帮我做校验
        if form_obj.is_valid():
            # 校验通过，去数据库创建一个新的用户
            form_obj.cleaned_data.pop("re_password")
            # 去掉确认密码
            avatar_img = request.FILES.get("avatar")
            models.UserInfo.objects.create_user(**form_obj.cleaned_data, avatar=avatar_img)
            ret["msg"] = "/index/"
            return JsonResponse(ret)
        else:
            print(form_obj.errors)
            # 校验不通过
            ret["status"] = 1
            # 返回错误信息
            ret["msg"] = form_obj.errors
            print(ret)
            print("=" * 120)
            return JsonResponse(ret)
    # 生成一个form对象
    form_obj = forms.RegForm()
    print(form_obj.fields)
    return render(request, "register.html", {"form_obj": form_obj})


# 校验用户名是否已被注册
def check_username_exist(request):
    ret = {"status": 0, "msg": ""}
    username = request.GET.get("username")
    print(username)
    is_exist = models.UserInfo.objects.filter(username=username)
    if is_exist:
        ret["status"] = 1
        ret["msg"] = "用户名已被注册！"
    return JsonResponse(ret)


# 个人博客主页
def home(request, username, *args):
    logger.debug("home视图获取到用户名:{}".format(username))
    # 去UserInfo表里把用户对象取出来
    user = models.UserInfo.objects.filter(username=username).first()
    if not user:
        logger.warning("又有人访问不存在页面了...")
        return HttpResponse("404")
    # 如果用户存在需要将TA写的所有文章找出来
    blog = user.blog
    if not args:
        logger.debug("args没有接收到参数，默认走的是用户的个人博客页面！")
        # 我的文章列表
        article_list = models.Article.objects.filter(user=user)
      
    else:
        logger.debug(args)
        logger.debug("------------------------------")
        # 表示按照文章的分类或tag或日期归档来查询
        # args = ("category", "技术")
        # article_list = models.Article.objects.filter(user=user).filter(category__title="技术")
        if args[0] == "category":
            article_list = models.Article.objects.filter(user=user).filter(category__title=args[1])
        elif args[0] == "tag":
            article_list = models.Article.objects.filter(user=user).filter(tags__title=args[1])
        else:
            # 按照日期归档
            try:
                year, month = args[1].split("-")
                logger.debug("分割得到参数year:{}, month:{}".format(year, month))
                # logger_s10.info("得到年和月的参数啦！！！！")
                logger.debug("************************")
                article_list = models.Article.objects.filter(user=user).filter(
                    create_time__year=year, create_time__month=month
                )
            except Exception as e:
                logger.warning("请求访问的日期归档格式不正确！！！")
                logger.warning((str(e)))
                return HttpResponse("404")
    return render(request, "home.html", {
        "username": username,
        "blog": blog,
        "article_list": article_list,
    })


def get_left_menu(username):
    user = models.UserInfo.objects.filter(username=username).first()
    blog = user.blog
    category_list = models.Category.objects.filter(blog=blog).annotate(c=Count("article")).values("title", "c")
    tag_list = models.Tag.objects.filter(blog=blog).annotate(c=Count("article")).values("title", "c")
    # 按日期归档
    archive_list = models.Article.objects.filter(user=user).extra(
        select={"archive_ym": "date_format(create_time,'%%Y-%%m')"}
    ).values("archive_ym").annotate(c=Count("nid")).values("archive_ym", "c")

    return category_list, tag_list, archive_list


def article_detail(request, username, pk):
    """
    :param username: 被访问的blog的用户名
    :param pk: 访问的文章的主键id值
    :return:
    """
    user = models.UserInfo.objects.filter(username=username).first()
    if not user:
        return HttpResponse("404")
    blog = user.blog
    # 找到当前的文章
    article_obj = models.Article.objects.filter(pk=pk).first()

    return render(
        request,
        "article_detail.html",
        {
            "username": username,
            "article": article_obj,
            "blog": blog,
         }
    )


import json
from django.db.models import F


def up_down(request):
    print(request.POST)
    article_id=request.POST.get('article_id')
    is_up=json.loads(request.POST.get('is_up'))
    user=request.user
    response={"state":True}
    print("is_up",is_up)
    try:
        models.ArticleUpDown.objects.create(user=user,article_id=article_id,is_up=is_up)
        models.Article.objects.filter(pk=article_id).update(up_count=F("up_count")+1)

    except Exception as e:
        response["state"]=False
        response["fisrt_action"]=models.ArticleUpDown.objects.filter(user=user,article_id=article_id).first().is_up

    return JsonResponse(response)
    # return HttpResponse(json.dumps(response))






