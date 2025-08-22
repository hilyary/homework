from django.http import HttpResponse # 导入HttpResponse模块，用于返回HTTP响应
from django.shortcuts import redirect, get_object_or_404, render # 导入快捷函数，用于重定向、获取模型对象和渲染模板
import random # 导入random模块，用于生成随机数
from PIL import Image, ImageDraw, ImageFont # 导入PIL模块，用于处理和生成图片
import os # 导入os模块，提供了访问操作系统功能的方法
from django.conf import settings # 导入settings模块，用于访问和修改Django项目的全局设置
from index.models import * # 导入index应用下的所有模型
from django.contrib.auth.decorators import login_required # 导入装饰器，用于限制只有登录用户才能访问视图函数
from django.contrib.auth import authenticate, login, logout # 导入身份验证方法，用于验证、登录和注销用户
from django.contrib.auth.models import User # 导入Django内置用户模型
from django.core.paginator import Paginator # 导入分页模块，用于将数据分页
from .forms import UserForm,MessageForm # 导入自定义表单类，用于用户注册和编辑个人信息
import shutil # 导入shutil模块，提供了高级文件操作方法，例如复制、移动和删除文件
from django.views.decorators.csrf import csrf_exempt # 导入装饰器，用于在视图函数中禁用CSRF保护
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger # 导入分页模块相关异常类
import tempfile # 导入tempfile模块，用于创建临时文件和目录
from django.contrib import messages # 导入消息模块，用于向用户发送消息
from .models import CollectionTask # 导入CollectionTask模型，用于管理收集任务
from datetime import datetime # 导入datetime模块，用于处理日期和时间
from django.contrib.auth.tokens import default_token_generator # 导入身份验证令牌生成器
from django.utils.encoding import force_bytes, force_text # 导入编码和解码方法，用于将字节序列转换为字符串和字符串转换为字节序列
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode # 导入URL编码和解码方法
from django.template.loader import render_to_string # 导入模板渲染方法，用于渲染邮件内容模板
from django.core.mail import EmailMessage # 导入邮件模块，用于发送邮件
from django.contrib.auth import get_user_model # 导入用户模型
from django.urls import reverse # 导入URL反向解析方法，用于生成URL
from django.db.models import Q # 导入查询条件模块，用于构造复杂的查询条件
import re # 导入正则表达式模块，用于处理字符串匹配
from urllib.parse import quote # 导入URL编码方法，用于将字符串编码为URL安全的格式
import logging
import logging.handlers
from django.utils.deprecation import MiddlewareMixin


#-------访问日志记录功能-------#
#由于挂在公网后发现老有sb攻击我，搞个记录的
class AccessLogMiddleware(MiddlewareMixin):  # 定义 AccessLogMiddleware 类并继承 MiddlewareMixin 类
    def __init__(self, get_response=None):  # 定义 __init__ 方法
        self.get_response = get_response  # 将 get_response 参数赋值给 self.get_response 属性
        self.logger = logging.getLogger('access_log')  # 初始化日志记录器
        self.logger.setLevel(logging.INFO)  # 设置日志级别为 INFO

        # 定义日志文件的路径和格式，并创建日志文件及其目录（如果不存在的话）
        logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')  # 获取日志文件所在目录的路径
        if not os.path.exists(logs_dir):  # 如果目录不存在
            os.makedirs(logs_dir)  # 创建目录
        handler = logging.handlers.TimedRotatingFileHandler(  # 创建按时间分割的日志文件处理器
            os.path.join(logs_dir, 'access.log'),  # 日志文件路径
            when='midnight',  # 分割时间为每天的午夜
            backupCount=15,  # 最多保留 15 个日志文件
        )
        handler.suffix = '%Y-%m-%d'  # 日志文件名的时间格式
        handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))  # 设置日志记录格式
        self.logger.addHandler(handler)  # 将日志文件处理器添加到日志记录器中

    def process_response(self, request, response):  # 定义 process_response 方法
        path = request.path  # 获取请求的路径
        status_code = response.status_code  # 获取响应的状态码
        ip_address = request.META.get('REMOTE_ADDR')  # 获取客户端 IP 地址
        request_method=request.method   #获取请求方式
        body_POST = request.POST    #获取post传递的参数

        if status_code != 200 or not path.endswith(('.css', '.js','.ico')):  # 如果状态码不是200，或者路径不以 '.css' 或 '.js' 结尾
            log_message = f'{ip_address} - {request_method} - {status_code} - {path} - {body_POST}'  # 拼接日志信息
            self.logger.info(log_message)  # 记录日志信息

        return response  # 返回响应对象，以便 Django 可以将其返回给客户端



#-------验证码功能-------#
def varityCody(request):    #验证码功能
    # 1.创建画面对象
    # 定义变量，用于画面的背景色、宽、高
    bgcolor = (255,255,255)
    width = 200
    height = 45
 
    im = Image.new('RGB', (width, height), bgcolor)
    # 2.创建画笔对象
    draw = ImageDraw.Draw(im)


    # 3.定义验证码的备选值
    str1 = 'ABCD123EFGHIJK456klmnopqrstuvwsyzLMNOPQRS789TUVWXYZ0abcdefghij'
    # 随机选取4个值作为验证码
    rand_str = ''
    for i in range(0, 4):
        rand_str += str1[random.randrange(0, len(str1))]
    # 构造字体类型和大小
    fonts_path=os.getcwd()
    font = ImageFont.truetype(f'{fonts_path}/static-files/fonts/FreeMono.ttf', random.randrange(23,40))
    # 绘制4个字
    draw.text((15, 10), rand_str[0], font=font, fill=random.randrange(0, 255))
    draw.text((65, 10), rand_str[1], font=font, fill=random.randrange(0, 255))
    draw.text((120, 10), rand_str[2], font=font, fill=random.randrange(0, 255))
    draw.text((175, 10), rand_str[3], font=font, fill=random.randrange(0, 255))
    # 4.释放画笔
    del draw

    # 5.存入session，用于做进一步验证
    request.session['verifycode'] = rand_str

    # 内存文件操作(python3)
    from io import BytesIO
    buf = BytesIO()
    # 6.将图片保存在内存中，文件类型为png
    im.save(buf, 'png')
    # 7.将内存中的图片数据返回给客户端，MIME类型为图片png
    return HttpResponse(buf.getvalue(), 'image/png')



#-------前台功能-------#
#登录功能
def indexLogin(request, view_msg=None):
    # GET请求返回login.html页面
    if request.method == "GET":
        return render(request, "login.html")

    # POST请求获取用户输入的用户名、密码及验证码
    uName = request.POST['username']  # 获取用户名
    password = request.POST['password']  # 获取密码
    vcode = request.POST['vcode']  # 获取验证码
    v = request.session['verifycode']  # 获取session中存储的验证码

    # 验证码校验
    if vcode != v:
        view_msg = "验证码错误，登录失败"
        return render(request, "login.html", {'view_msg': view_msg})  # 返回login.html页面并提示验证码错误

    # 获取next参数
    try:
        np = request.GET['next']  # 获取next参数
    except:
        np = None

    # 用户验证
    user = authenticate(username=uName, password=password)  # 验证用户
    if user is not None:
        # 登录成功
        login(request, user)  # 登录用户
        if np:
            return redirect('manage')  # 如果有next参数，则重定向到manage页面
        return redirect('manage')  # 否则重定向到manage页面
    else:
        # 登录失败
        view_msg = "登录出错，用户名不存在或密码错误！" #设置返回的报错信息
        return render(request, "login.html", {'view_msg': view_msg})  # 返回login.html页面并提示用户名或密码错误

#退出登录
def logout_view(request): # 定义logout_view函数，用于用户注销
    logout(request) # 调用logout函数，将当前用户注销
    return redirect('login') # 重定向到login页面


#登录成功跳转的页面
@login_required(login_url="/index/login/")  # 使用@login_required装饰器，确保用户已登录，否则重定向到login页面
def managePage(request):  # 定义managePage函数，用于展示管理页面
    user = request.user  # 获取当前用户
    return render(request, 'manage.html', {'user': user})  # 返回manage.html页面，并将当前用户传递给页面



#-------找回密码功能-------#

# 忘记密码页面，用户提交邮箱后发送验证邮件
def password_find(request):
    if request.method == 'POST':
        email = request.POST.get('email')  # 获取邮箱
        try:
            user = User.objects.get(email=email)  # 根据邮箱获取用户对象
        except User.DoesNotExist:
            messages.error(request, '此邮箱不存在，请核实后重试。')  # 如果用户不存在，设置错误信息
        else:
            send_password_reset_email(user)  # 发送重置密码邮件
            messages.info(request, '我们已经发送一封邮件到您的邮箱，请查收并按照提示完成操作。')
            # 设置信息
        return redirect(reverse('password_find'))  # 重定向到password_find页面
    return render(request, 'password_find.html')  # 返回password_find页面

# 发送找回密码的邮件
def send_password_reset_email(user):
    # 生成重置密码链接
    reset_link = 'http://192.168.29.131/index/password_reset/{}/{}'.format(urlsafe_base64_encode(force_bytes(user.pk)), default_token_generator.make_token(user))
    subject = '找回密码'  # 设置邮件主题
    to = [user.email]  # 设置收件人列表
    # 使用password_set_email.html模板渲染html内容，将用户名和重置密码链接传递给模板
    html_content = render_to_string('password_set_email.html', {'username': user.username, 'reset_link': reset_link})
    message = EmailMessage(subject, body=html_content, from_email=settings.EMAIL_HOST_USER, to=to)
    message.content_subtype = 'html'  # 设置邮件内容为html格式
    message.send(fail_silently=False)  # 发送邮件


# 用户点击邮件中的验证链接，进入修改密码页面
def check_code(request):
    uid = request.GET.get('uid')  # 获取从邮件中传来的uid
    token = request.GET.get('token')  # 获取从邮件中传来的token
    try:
        uid = urlsafe_base64_decode(uid).decode()  # 将uidb64解码并转换成字符串格式
        user = User.objects.get(pk=uid)  # 根据uid获取用户对象
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None  # 如果解码失败或者用户不存在，则将user置为None
    if user and default_token_generator.check_token(user, token):  # 如果用户存在并且token验证通过
        request.session['reset_user_id'] = user.id  # 将用户id存入session
        return render(request, 'password_reset.html')  # 返回password_reset页面
    else:
        messages.error(request, '验证链接无效，请重试。')  # 设置错误信息
        return redirect(reverse('password_find'))  # 重定向到password_find页面

# 用户提交新密码后进行修改操作
def password_reset(request, uid, token):
    try:
        # 将uidb64解码并转换成字符串格式
        uid = force_text(urlsafe_base64_decode(uid))
        # 根据uid获取用户对象
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        user = None
    if user and default_token_generator.check_token(user, token):  # 如果用户存在并且token验证通过
        if request.method == 'POST':  # 如果是POST请求
            # 获取用户输入的密码和确认密码
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            if password == confirm_password:  # 如果两次输入的密码一致
                user.set_password(password)  # 修改用户密码
                user.save()
                messages.success(request, f'尊敬的{user}用户,您的密码修改成功！请使用新密码进行登录。')  # 设置成功信息
                return redirect(reverse('login'))  # 重定向到登录页面
            else:
                messages.error(request, '两次输入的密码不一致，请检查后重新输入。')  # 设置错误信息
        return render(request, 'password_reset.html')  # 返回password_reset页面
    else:
        messages.error(request, '验证链接无效，请重试。')  # 设置错误信息
        return redirect(reverse('password_find'))  # 重定向到password_find页面
    
#跳转忘记密码页面
def zhmm(request):
    return redirect("password_find")
#跳转到登录页面
def fhdl(request):
    return redirect("login")

#-------用户管理功能-------#
 #修改自己的密码
@login_required(login_url="/index/login/")
def changepass(request):
    uID = request.session.get("_auth_user_id")  # 获取当前登录用户的ID
    user = User.objects.get(id=uID)  # 根据ID获取用户对象
    context = {}  # 初始化context字典
    # 载入界面
    if request.method == "GET":
        context['errMsg'] = ''  # 如果是GET请求，初始化errMsg为空
        context['userName'] = user.username  # 将当前用户名加入context字典
        return render(request, "changepass.html", context)  # 返回changepass.html页面和context字典
    # POST 修改密码
    old_password = request.POST['old_password']  # 获取旧密码
    new_password = request.POST['new_password']  # 获取新密码
    two_new_password = request.POST['two_new_password']  # 获取确认新密码
    if user.check_password(old_password):  # 如果旧密码正确
        if not new_password:  # 如果新密码为空
            context['errMsg'] = '新密码不能为空！'  # 设置错误信息
        elif new_password != two_new_password:  # 如果新密码和确认新密码不一致
            context['errMsg'] = "两次密码不一致！"  # 设置错误信息
        else:
            user.set_password(new_password)  # 设置新密码
            user.save()  # 保存用户对象
            logout(request)  # 登出当前用户
            messages.success(request, f'尊敬的{user.username}，您已成功修改密码！请您重新登录！')
            # 设置密码修改成功信息
            return redirect("login")  # 重定向到登录页面
    else:
        context['errMsg'] = "原密码输入错误！"  # 如果旧密码不正确，设置错误信息
    return render(request, "changepass.html", context)  # 返回changepass.html页面和context字典

#管理员改其他用户密码
@login_required(login_url="/index/login/")
def change_user_pass(request, user_id):
    uID = request.session.get("_auth_user_id")  # 获取当前登录用户的ID
    current_user = User.objects.get(id=uID)  # 根据ID获取当前用户对象
    context = {}  # 初始化context字典
    qx_user = current_user.username  # 获取当前用户名
    user_to_change = get_object_or_404(User, id=user_id)  # 根据user_id获取用户对象
    context['chan_user_name'] = user_to_change.username  # 将用户对象的用户名加入context字典
    # 非管理员仅能更改自己的密码
    if not current_user.is_superuser and current_user.id != user_to_change.id:
        messages.warning(request, '抱歉，您只能更改自己的密码！')
        return redirect('user_list')  # 如果当前用户不是管理员且不是要修改密码的用户本人，重定向到用户列表页面
    # 如果是管理员，可以直接修改密码
    elif current_user.is_superuser == True:
        if request.method == 'POST':
            one_password = request.POST['one_password']  # 获取新密码
            two_password = request.POST['two_password']  # 获取确认新密码
            if not one_password:
                context['errMsg'] = '新密码不能为空！'  # 如果新密码为空，设置错误信息
            elif one_password != two_password:
                context['errMsg'] = "两次密码不一致！"  # 如果新密码和确认新密码不一致，设置错误信息
            else:
                user_to_change.set_password(one_password)  # 设置新密码
                user_to_change.save()  # 保存用户对象
                messages.success(request, f'尊敬的{qx_user}用户，您已成功修改用户【{user_to_change.username}】的密码！')
                # 设置密码修改成功信息
                return redirect('user_list')  # 重定向到用户列表页面
    # 如果是要修改密码的用户本人，跳转到changepass页面
    elif current_user == user_to_change:
        return redirect('changepass')
    # 上面两个判断是为了防止越权
    else:
        if request.method == 'POST':
            one_password = request.POST['one_password']  # 获取新密码
            two_password = request.POST['two_password']  # 获取确认新密码
            if not one_password:
                context['errMsg'] = '新密码不能为空！'  # 如果新密码为空，设置错误信息
            elif one_password != two_password:
                context['errMsg'] = "两次密码不一致！"  # 如果新密码和确认新密码不一致，设置错误信息
            else:
                user_to_change.set_password(one_password)  # 设置新密码
                user_to_change.save()  # 保存用户对象
                messages.success(request, f'尊敬的{qx_user}用户，您已成功修改自己的密码！请重新登录')
                # 设置密码修改成功信息
                return redirect('user_list')  # 重定向到用户列表页面

    return render(request, "change_user_pass.html", context)  # 返回change_user_pass.html页面和context字典

#管理员修改用户密码
@login_required(login_url="/index/login/")
def change_user_pass(request, user_id):
    # 获取当前用户id
    uID = request.session.get("_auth_user_id")
    # 根据当前用户id获取用户对象
    current_user = User.objects.get(id=uID)
    context = {}
    # 获取当前用户的用户名
    qx_user = current_user.username
    # 根据user_id获取要修改密码的用户对象
    user_to_change = get_object_or_404(User, id=user_id)
    # 将要修改密码的用户的用户名存入context中
    context['chan_user_name'] = user_to_change.username
    # 非管理员仅能更改自己的密码
    if not current_user.is_superuser and current_user.id != user_to_change.id:
        messages.warning(request, '抱歉，您只能更改自己的密码！')
        return redirect('user_list')
    elif current_user.is_superuser == True:  # 如果是管理员
        if request.method == 'POST':  # 如果是POST请求
            one_password = request.POST['one_password']
            two_password = request.POST['two_password']
            if not one_password:
                context['errMsg'] = '新密码不能为空！'
            elif one_password != two_password:
                context['errMsg'] = "两次密码不一致！"
            else:
                user_to_change.set_password(one_password)  # 修改用户密码
                user_to_change.save()
                messages.success(request, f'尊敬的{qx_user}用户，您已成功修改用户【{user_to_change.username}】的密码！')  # 设置成功信息
                return redirect('user_list')  # 重定向到user_list页面
    # 如果是管理员或者是要修改密码的用户本人，就不需要输入用户密码可以直接改密码
    elif current_user == user_to_change:
        return redirect('changepass')
    # 上面两个判断是为了防止越权
    else:
        if request.method == 'POST':  # 如果是POST请求
            one_password = request.POST['one_password']
            two_password = request.POST['two_password']
            if not one_password:
                context['errMsg'] = '新密码不能为空！'
            elif one_password != two_password:
                context['errMsg'] = "两次密码不一致！"
            else:
                user_to_change.set_password(one_password)  # 修改用户密码
                user_to_change.save()
                messages.success(request, f'尊敬的{qx_user}用户，您已成功修改自己的密码！请重新登录')  # 设置成功信息
                return redirect('user_list')  # 重定向到user_list页面
    return render(request, "change_user_pass.html", context)  # 返回change_user_pass页面

#管理员创建用户
@login_required(login_url="/index/login/")
def createuser(request):
    # 获取当前用户id
    uID = request.session.get("_auth_user_id")
    # 根据当前用户id获取用户对象
    user = User.objects.get(id=uID)
    # 获取当前用户的用户名
    qx_user = user.username
    if user.is_superuser == True:  # 设置只有管理员用户才能创建用户
        context = {}
        if request.method == "GET":
            context['errMsg'] = ''
            return render(request, "createuser.html", context)
        # POST创建用户
        # 1.收集信息
        uName = request.POST['uName']
        pwd1 = request.POST['pwd1']
        pwd2 = request.POST['pwd2']
        email = request.POST['email']
        role = request.POST['role']
        try:
            user = User.objects.get(username=uName)
        except:
            user = None
        # 2.检测两次输入的密码是否一样
        if pwd1 != pwd2:
            context['errMsg'] = "两次密码不一致！"
        # 3.查询用户名是否已存在
        elif user:
            context['errMsg'] = "用户已存在！"
        # 添加用户
        else:
            new_user = User.objects.create_user(username=uName, password=pwd1, email=email, is_superuser=int(role))
            new_user.is_active = True  # 直接激活
            new_user.save()
            messages.success(request, f'尊敬的{qx_user}用户，您已成功创建【{uName}】用户！')  # 设置成功信息
            return redirect("user_list")  # 重定向到user_list页面
        return render(request, "createuser.html", context)
    else:
        messages.warning(request, f'尊敬的{qx_user}用户，您没有权限创建用户！')  # 设置警告信息
        return redirect("user_list")  # 重定向到user_list页面

 #返回主页功能
@login_required(login_url="/index/login/")
def zhuye(request):
    # 获取当前用户id
    uID = request.session.get("_auth_user_id")
    # 根据当前用户id获取用户对象
    user = User.objects.get(id=uID)
    if user.is_authenticated:  # 判断用户是否已登录
        return render(request, "manage.html")
    else:
        return render(request, "login.html")

#返回用户管理页面
@login_required(login_url="/index/login/") 
def yhym(reqiest):
   return redirect("user_list")

#检查当前登录用户是否为管理员
#如果不是设置错误信息并跳转
def requires_authorization(function):
    def wrap(request, *args, **kwargs):
        # 获取当前用户对象
        user = request.user
        # 获取user_id参数
        user_id = kwargs.get('user_id')

        if user.is_authenticated:  # 判断用户是否已登录
            if user.is_superuser or user_id == user.id:  # 判断是否是管理员或者是要修改信息的用户本人
                return function(request, *args, **kwargs)
        # 如果不是管理员或者是要修改信息的用户本人，就返回警告信息并重定向到user_list页面
        messages.warning(request, f'尊敬的{user.username} 用户，您没有权限修改其他用户的信息！')
        return redirect('user_list')
    return wrap


#编辑用户
@login_required(login_url="/index/login/")  #判断是否登录
@requires_authorization #检查当前登录用户是否为管理员
def update_user(request, user_id):
    # 根据user_id获取要修改信息的用户对象
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        # 检查用户名和邮箱是否被修改
        if request.POST.get('username') != user.username:
            messages.error(request, '不允许修改用户名！如果要修改请联系管理员')
            return redirect('update_user', user_id=user_id)
        if request.POST.get('email') != user.email:
            messages.error(request, '不允许修改邮箱！如果要修改请联系管理员')
            return redirect('update_user', user_id=user_id)

        # 生成表单并验证表单数据
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()  # 保存修改后的表单数据
            messages.success(request, f'{user.username} 用户信息修改成功！')  # 设置成功信息
            return redirect('user_list')  # 重定向到user_list页面
    else:
        # 生成表单
        form = UserForm(instance=user)
    return render(request, 'edit_user.html', {'form': form})  # 返回edit_user页面，并将表单对象传入模板

#用户列表
@login_required(login_url="/index/login/")
def user_list(request):
    # 获取当前用户id
    uID = request.session.get("_auth_user_id")
    # 根据当前用户id获取用户对象
    user = User.objects.get(id=uID)
    # 获取当前用户的用户名和是否是管理员
    qx_user = user.username
    user_qx = user.is_superuser
    if user_qx == 1:  # 只有管理员用户才能显示所有用户列表
        # 获取所有用户列表
        user_list = User.objects.all()
    else:
        # 获取当前用户列表
        user_list = User.objects.filter(username=qx_user)

    # 检索查询参数并过滤用户列表
    search_query = request.GET.get('search_query')
    if search_query:
        user_list = user_list.filter(username__icontains=search_query)

    # 设置每页6个条目
    user_paginator = Paginator(user_list, 6)
    # 获取页码参数
    page_number = request.GET.get('page')
    # 获取当前页的用户列表对象
    user_page_obj = user_paginator.get_page(page_number)
    # 返回user_list页面，并将用户列表对象传入模板
    return render(request, 'user_list.html', {'user_list': user_page_obj})



#管理员删除用户
@login_required(login_url="/index/login/")
def delete_user(request, user_id):
    # 获取当前用户id
    uID = request.session.get("_auth_user_id")
    # 根据当前用户id获取用户对象
    user = User.objects.get(id=uID)
    # 获取当前用户的用户名
    qx_user = user.username
    if int(uID) == (user_id):
        # 如果要删除的是当前用户，返回警告信息并重定向到user_list页面
        messages.warning(request, f'尊敬的{qx_user}用户，您不能删除您自己！')
        return redirect('user_list')
    elif user.is_superuser == True:
        # 如果当前用户是管理员，获取要删除的用户对象并删除
        user = get_object_or_404(User, id=user_id)
        user.delete()
        # 返回成功信息并重定向到user_list页面
        messages.success(request, f'尊敬的{qx_user}用户，您已成功删除用户【{user}】！')
        return redirect('user_list')
    else:
        # 如果当前用户不是管理员，返回警告信息并重定向到user_list页面
        messages.warning(request, f'尊敬的{qx_user}用户，您没有权限删除其他用户！')
        return redirect('user_list')

#-------收集任务管理功能-------#
#1.文件上传
def upload_file(request, task_id):
    # 根据task_id获取任务对象
    task = get_object_or_404(CollectionTask, id=task_id)
    # 获取任务名称
    task_name = task.name
    if request.method == 'POST':
        # 获取用户输入的文件名
        new_name = request.POST.get('file_name')
        # 获取所有的文件输入框
        file_inputs = [key for key in request.FILES.keys() if key.startswith('file')]
        for i, file_input in enumerate(file_inputs, 1):
            # 获取上传的文件对象
            file = request.FILES.get(file_input)
            # 获取文件名和文件扩展名
            original_name, file_extension = os.path.splitext(file.name)
            # 如果当前任务没有匹配项，则按照用户在前端输入的学号-姓名作为文件名
            if not task.get_matches():
                # 定义正则表达式，匹配学号后两位-姓名的格式
                pattern = r'^\d{2}-[\u4e00-\u9fa5]{2,4}$'
                # 如果用户输入的文件名不符合格式，则返回警告信息并重定向到同一任务的上传链接
                if not re.match(pattern, new_name):
                    messages.warning(request, f'{new_name}，您输入的信息格式错误，请严格按照学号后两位-姓名的格式输入！')
                    return redirect('upload_file', task_id=task_id)
            else:
                # 如果当前任务有匹配项，则匹配文件名是否符合设置的匹配项
                for match in task.get_matches():
                    if re.match(match.name_pattern, new_name):
                        break
                else:
                    messages.warning(request, f'{new_name}，您输入的信息格式错误，请严格输入真实信息，按照学号后两位-姓名的格式输入！')
                    return redirect('upload_file', task_id=task_id)
            # 如果上传了多个文件，添加编号
            file_name = f'{new_name}-{i}{file_extension}' if len(file_inputs) > 1 else f'{new_name}{file_extension}'
            # 生成文件路径并将上传的文件保存在文件路径下
            file_path = os.path.join(task.file_path, file_name)
            with open(file_path, 'wb') as f:
                for chunk in file.chunks():
                    f.write(chunk)
        # 设置上传成功的提示信息闪现消息
        messages.success(request, f'{new_name}，您已成功提交{task_name}！')
        return redirect('upload_file', task_id=task_id)  # 重定向到同一任务的上传链接
    # 返回upload页面，并将任务名称传入模板
    return render(request, 'upload.html', {'task_name': task_name})


#2.展示和管理任务列表功能
@login_required(login_url="/index/login/")
def list_collection_tasks(request):
    # 获取查询参数
    search_query = request.GET.get('search_query')
    # 获取当前用户id
    uID=request.session.get("_auth_user_id")
    # 根据当前用户id获取用户对象
    user=User.objects.get(id=uID)
    # 获取当前用户的用户名和是否是管理员
    qx_user=user.username
    user_qx=user.is_superuser
    if user_qx == True:
        # 如果当前用户是管理员，获取所有任务
        user_tasks = CollectionTask.objects.all()
    else:
        # 如果当前用户不是管理员，获取当前用户创建的任务
        user_tasks = CollectionTask.objects.filter(creator=request.user)
    # 如果有查询参数，则进行查询
    search_query = request.GET.get('search_query')
    if search_query:
        # 查询功能，筛选任务名称或创建者包含查询参数的任务
        user_tasks = CollectionTask.objects.filter(Q(name__icontains=search_query) | Q(creator__icontains=search_query))
        #使用 filter() 方法筛选任务名称或创建者
        #Q() 方法用于构建复杂的查询表达式，多个 Q() 表达式可以通过逻辑运算符 &（与）、|（或）和 ~（非）组合
        #在这里，Q(name__icontains=search_query) 表示任务名称包含查询参数 
        #search_query，Q(creator__icontains=search_query) 表示创建者包含查询参数 search_query，
        #两者使用 | 运算符进行或运算，表示只要任务名称或创建者中有一个包含查询参数 search_query，就符合要求。
        #最终，filter() 方法返回符合筛选条件的任务列表。
    # 设置每页6个条目
    paginator = Paginator(user_tasks, 6)
    # 获取页码参数
    page = request.GET.get('page')
    try:
        # 获取当前页的任务列表对象
        tasks = paginator.page(page)
    except PageNotAnInteger:
        # 如果页码参数不是整数，则返回第一页
        tasks = paginator.page(1)
    except EmptyPage:
        # 如果页码参数超出范围，则返回最后一页
        tasks = paginator.page(paginator.num_pages)
    # 返回list_tasks页面，并将任务列表对象传入模板
    return render(request, 'list_tasks.html', {'tasks': tasks})


#3.添加收集任务
@login_required(login_url="/index/login/")
def add_collection_task(request):
    if request.method == 'POST':
        # 获取任务名称
        task_name = request.POST.get('task_name')
        # 将 creator 设为当前登录用户
        creator = request.user.username
        # 设置存储文件路径
        file_path = os.path.join(f'{os.getcwd()}/uploads', task_name)
        # 如果文件夹不存在，则创建
        if not os.path.isdir(file_path):
            os.makedirs(file_path)
        # 检查数据库中是否已存在具有给定名称的任务
        if CollectionTask.objects.filter(name=task_name).exists():
            # 如果存在，返回错误信息
            error_message = "任务名已经存在！请更改任务名。"
            return render(request, 'add_task.html', {'error_message': error_message})
        # 如果不存在，创建新任务并保存到数据库中
        task = CollectionTask(name=task_name, creator=creator, file_path=file_path)
        task.save()
        # 发送成功消息
        messages.success(request, f'尊敬的{creator}，您的收集任务【{task_name}】创建成功！')
        # 重定向到任务列表页面
        return redirect("rwlb")
    # 如果请求方法是 GET，返回添加任务页面
    return render(request,'add_task.html')


# 4.编辑收集任务
@login_required(login_url="/index/login/")
def edit_collection_task(request, task_id):
    # 获取当前用户id
    uID=request.session.get("_auth_user_id")
    # 根据当前用户id获取用户对象
    user=User.objects.get(id=uID)
    # 获取当前用户的用户名
    qx_user=user.username
    # 根据任务id获取任务对象
    task = get_object_or_404(CollectionTask, id=task_id)
    if request.method == 'POST':
        if user.is_superuser == True: # 如果当前用户是管理员用户
            # 获取修改后的任务名称和创建者
            task_name = request.POST.get('task_name')
            creator = task.creator  # 从任务对象中获取创建者信息
            if task.creator == request.user:  # 检查当前用户是否是任务的创建者
                creator = request.POST.get('creator')
            # 构建新的文件路径
            old_path = task.file_path
            new_path = os.path.dirname(old_path) + '/' + task_name
            os.rename(old_path, new_path)
            # 更新任务对象的属性
            task.name = task_name
            task.creator = creator
            task.file_path = new_path
            task.save()
            # 更新index_collectiontask表中的file_path列的值
            CollectionTask.objects.filter(id=task_id).update(file_path=new_path)
            # 发送成功消息
            messages.success(request, f'您已成功修改{task_name}的收集任务！')
            # 重定向到任务列表页面
            return redirect('list_tasks')
        elif qx_user == task.creator: # 如果当前用户是任务的创建者
            # 获取修改后的任务名称和创建者
            task_name = request.POST.get('task_name')
            creator = task.creator  # 从任务对象中获取创建者信息
            if task.creator == request.user:  # 检查当前用户是否是任务的创建者
                creator = request.POST.get('creator')
            # 构建新的文件路径
            old_path = task.file_path
            new_path = os.path.dirname(old_path) + '/' + task_name
            os.rename(old_path, new_path)
            # 更新任务对象的属性
            task.name = task_name
            task.creator = creator
            task.file_path = new_path
            task.save()
            # 更新index_collectiontask表中的file_path列的值
            CollectionTask.objects.filter(id=task_id).update(file_path=new_path)
            # 发送成功消息
            messages.success(request, f'您已成功修改{task_name}的收集任务！')
            # 重定向到任务列表页面
            return redirect('list_tasks')
        else: # 如果当前用户既不是管理员用户，也不是任务的创建者
            # 发送警告消息
            messages.warning(request, f'尊敬的{qx_user}用户，您没有权限修改他人任务！')
            # 重定向到任务列表页面
            return redirect('list_tasks')

    # 如果当前用户不是管理员用户，且不是任务的创建者，发送警告消息
    if user.is_superuser != True:
        if qx_user != task.creator:
            messages.warning(request, f'尊敬的{qx_user}用户，您没有权限修改他人的任务！')
            return redirect('list_tasks')
    # 返回编辑任务页面，并将任务对象传入模板
    return render(request, 'edit_task.html', {'task': task})


# 5.删除收集任务
@login_required(login_url="/index/login/")
def delete_collection_task(request, task_id):
    # 获取当前用户id
    uID = request.session.get("_auth_user_id")
    # 根据当前用户id获取用户对象
    user = User.objects.get(id=uID)
    # 获取当前用户的用户名
    qx_user = user.username
    # 根据任务id获取任务对象
    task = get_object_or_404(CollectionTask, id=task_id)

    if user.is_superuser == True: # 如果当前用户是管理员用户
        # 删除任务对应的文件夹和任务对象
        shutil.rmtree(task.file_path)
        task.delete()
        # 发送成功消息
        messages.success(request, f'尊敬的{qx_user}用户，您已成功删除【{task.name}】收集任务！')
        # 重定向到任务列表页面
        return redirect('list_tasks')
    elif qx_user == task.creator: # 如果当前用户是任务的创建者
        # 删除任务对应的文件夹和任务对象
        shutil.rmtree(task.file_path)
        task.delete()
        # 发送成功消息
        messages.success(request, f'尊敬的{qx_user}用户，您已成功删除【{task.name}】收集任务！')
        # 重定向到任务列表页面
        return redirect('list_tasks')
    else: # 如果当前用户既不是管理员用户，也不是任务的创建者
        # 发送错误消息
        messages.error(request, '您无权删除该任务！')
        # 重定向到任务列表页面
        return redirect('list_tasks')

# 6.打包下载文件
@login_required(login_url="/index/login/") # 登录验证装饰器
@csrf_exempt # CSRF 保护装饰器
def download_collection_task(request, task_id):
    # 根据任务id获取任务对象
    task = get_object_or_404(CollectionTask, id=task_id)

    # 检查当前用户是否是任务的创建者或管理员
    if str(task.creator) != str(request.user) and not request.user.is_superuser:
        # 发送错误消息
        messages.error(request, '您无权下载该任务！')
        # 重定向到任务列表页面
        return redirect('list_tasks')

    # 创建临时文件夹
    with tempfile.TemporaryDirectory() as tmp_dir:
        # 遍历任务文件夹，将其中的文件复制到临时文件夹中
        for root, dirs, files in os.walk(task.file_path):
            for file in files:
                file_path = os.path.join(root, file) # 获取文件绝对路径
                relative_path = os.path.relpath(file_path, task.file_path) # 获取文件相对路径
                target_path = os.path.join(tmp_dir, relative_path) # 构建目标路径
                os.makedirs(os.path.dirname(target_path), exist_ok=True) # 创建目标路径的目录
                shutil.copy2(file_path, target_path) # 复制文件到目标路径

        # 打包临时文件夹到 zip 文件中
        zip_filename = os.path.join(task.file_path, task.name + '.zip') # 构建 zip 文件路径
        shutil.make_archive(zip_filename[:-4], 'zip', tmp_dir) # 打包临时文件夹

        with open(zip_filename, 'rb') as f:
            # 构建 HTTP 响应对象
            response = HttpResponse(f.read(), content_type='application/zip')
            # 设置文件名
            filename_header = 'filename*=UTF-8\'\'{}'.format(quote(task.name + '.zip'))
            response['Content-Disposition'] = 'attachment; {}'.format(filename_header)
            os.remove(zip_filename) # 删除压缩包文件
            return response

# 7.设置匹配项
#设置用户上传文件时输入的学号-姓名，可以实现匹配的功能
@login_required(login_url="/index/login/")
def add_match(request, task_id):
    # 根据任务id获取任务对象
    task = get_object_or_404(CollectionTask, id=task_id)

    if request.user.is_superuser: # 如果当前用户是管理员用户
        # 获取当前任务的所有匹配项和其他任务列表
        matches = task.taskmatch_set.all()
        tasks = CollectionTask.objects.exclude(id=task_id)
        tasks_with_matches = CollectionTask.objects.filter(taskmatch__isnull=False).exclude(id=task_id).distinct()
    else: # 如果当前用户是普通用户
        try:
            task = CollectionTask.objects.get(id=task_id, creator=request.user.username)
        except CollectionTask.DoesNotExist:
            # 发送警告消息
            messages.warning(request, '该任务不存在或不属于当前用户')
            # 重定向到任务列表页面
            return redirect('list_tasks')
        # 获取当前任务的匹配项和其他任务列表
        matches = task.taskmatch_set.filter(creator=request.user.username)
        tasks = CollectionTask.objects.filter(creator=request.user.username).exclude(id=task_id)
        tasks_with_matches = CollectionTask.objects.filter(taskmatch__isnull=False, creator=request.user.username).exclude(id=task_id).distinct()

    if request.method == 'POST': # 如果是 POST 请求
        action = request.POST.get('action') # 获取操作类型
        if action == 'clear': # 如果是清空匹配项操作
            # 删除当前任务的所有匹配项
            matches.delete()
            # 发送成功消息
            messages.success(request, f'{task.name}的匹配项已全部删除')
            # 重定向到匹配项添加页面
            return redirect('add_match', task_id=task_id)

        name_pattern = request.POST.get('name_pattern') # 获取单个匹配项的名称模式
        from_task_id = request.POST.get('from_task_id') # 获取从其他任务复制匹配项的任务id
        bulk_name_pattern = request.POST.get('bulk_name_pattern') # 获取批量添加匹配项的名称模式

        if name_pattern: # 如果是单个匹配项的添加操作
            # 创建匹配项对象并保存
            match = TaskMatch(task=task, name_pattern=name_pattern, creator=request.user.username)
            match.save()
            # 发送成功消息
            messages.success(request, '添加匹配项成功')
            # 重定向到匹配项添加页面
            return redirect('add_match', task_id=task_id)

        elif from_task_id: # 如果是从其他任务复制匹配项的操作
            try:
                from_task = CollectionTask.objects.get(id=from_task_id)
            except CollectionTask.DoesNotExist:
                # 发送错误消息
                messages.error(request, '该任务不存在')
                # 重定向到匹配项添加页面
                return redirect('add_match', task_id=task_id)
            if not request.user.is_superuser and from_task.creator != request.user.username:
                # 发送警告消息
                messages.warning(request, f'任务"{from_task.name}"是其他用户创建的，不能使用该任务的匹配项')
                # 重定向到匹配项添加页面
                return redirect('add_match', task_id=task_id)
            from_matches = from_task.taskmatch_set.all()
            for from_match in from_matches:
                # 创建匹配项对象并保存
                match = TaskMatch(task=task, name_pattern=from_match.name_pattern, creator=request.user.username)
                match.save()
            # 发送成功消息
            messages.success(request, f'已从任务"{from_task.name}"复制匹配项')
            # 重定向到匹配项添加页面
            return redirect('add_match', task_id=task_id)

        elif bulk_name_pattern: # 如果是批量添加匹配项的操作
            name_patterns = bulk_name_pattern.split('\n')
            for name_pattern in name_patterns:
                name_pattern = name_pattern.strip()
                if name_pattern:
                    # 创建匹配项对象并保存
                    match = TaskMatch(task=task, name_pattern=name_pattern, creator=request.user.username)
                    match.save()
            # 发送成功消息
            messages.success(request, '批量添加匹配项成功')
            # 重定向到匹配项添加页面
            return redirect('add_match', task_id=task_id)

        else: # 如果没有进行任何操作
            # 发送错误消息
            messages.error(request, '请输入匹配项')

    # 渲染匹配项添加页面，并传递任务对象、匹配项列表、其他任务列表、有匹配项的任务列表
    return render(request, 'add_match.html', {'task': task, 'matches': matches, 'tasks': tasks, 'tasks_with_matches': tasks_with_matches})


# 8.获取任务未交提交名单
@login_required(login_url="/index/login/")
def check_submission(request, task_id): # 定义任务未交名单视图函数
    task = get_object_or_404(CollectionTask, id=task_id) # 获取任务对象
    matches = task.taskmatch_set.all() # 获取任务的所有匹配项
    missing_submissions = [] # 定义未交名单列表
    storage_folder = task.file_path # 获取任务的文件存储路径
    for match in matches: # 遍历任务的每个匹配项
        name_pattern = re.compile(match.name_pattern) # 编译匹配项的名称模式为正则表达式对象
        pattern_matched = False # 初始化模式是否匹配的标志为 False
        for file_name in os.listdir(storage_folder): # 遍历存储路径下的每个文件名
            if name_pattern.search(file_name): # 如果文件名与匹配项的名称模式匹配
                pattern_matched = True # 将模式是否匹配的标志设为 True
                break # 结束遍历
        if not pattern_matched: # 如果模式未匹配
            missing_submissions.append(match) # 将匹配项添加到未交名单列表中
    # 渲染任务未交名单页面，并传递任务对象和未交名单列表
    return render(request, 'check_submission.html', {'task': task, 'missing_submissions': missing_submissions})


#返回任务列表
@login_required(login_url="/index/login/") 
def fh_rwlb(reqiest):
   return redirect("list_tasks")

#  9.展示提交记录
@login_required(login_url="/index/login/")
def upload_work_jilu(request, task_id):
    # 获取任务对象
    task = get_object_or_404(CollectionTask, id=task_id)
    # 获取任务存储路径
    filepath = task.file_path
    # 获取存储路径下的所有文件名
    files = os.listdir(filepath)
    # 定义记录字典
    records_dict = {}
    
    # 遍历每个文件名
    for file in files:
        # 获取文件的完整路径
        file_path = os.path.join(filepath, file)
        # 如果是文件而不是文件夹
        if os.path.isfile(file_path):
            # 获取学号
            xh = file.split('-', 1)[0]
            # 如果学号已经在记录字典中，就跳过
            if xh in records_dict:
                continue
            
            # 获取学生名，并去掉文件编号
            student_name = (file.split('-', 1)[1]).split('.',1)[0].rsplit('-', 1)[0]
            
            # 获取文件的最后修改时间
            modify_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            
            # 将文件名、学号、姓名和最后修改时间添加到记录字典中
            records_dict[xh] = {'xh': xh, 'student_name': student_name, 'modify_time': modify_time}
    
    # 将记录字典的值转换为列表，并按照学号排序（数字排序）
    records = sorted(list(records_dict.values()), key=lambda x: int(x['xh']))
    
    # 将记录列表传给Paginator对象，每页显示12条记录
    paginator = Paginator(records, 12)
    
    # 获取当前页码
    page_number = request.GET.get('page')
    
    # 获取当前页的记录列表
    records = paginator.get_page(page_number)
    
    # 定义模板上下文
    context = {'records': records,'task_name':task.name, 'task_id': task_id}
    
    # 渲染上传作业记录页面，并传递模板上下文
    return render(request, 'upload_work_jilu.html', context=context)

#-------公告消息-------#
#发送公告消息
def send_message(request):  #管理员发送消息(公告)
    # 获取当前用户id
    uID = request.session.get("_auth_user_id")
    # 根据当前用户id获取用户对象
    user = User.objects.get(id=uID)
    qx_user = user.username
    #获取用户名
    if user.is_superuser == True:
        if request.method == 'POST':
            form = MessageForm(request.POST)
            if form.is_valid():
                message = form.save(commit=False)
                message.sender = request.user
                message.save()
                # 在这里添加代码来发送消息给所有用户
                messages.info(request, f'尊敬的{qx_user}用户，您编辑的公告发布成功！')
                return redirect('message_list')
        else:
            form = MessageForm()
        return render(request, 'send_message.html', {'form': form})
    else:
        messages.warning(request, f'尊敬的{qx_user}用户，您没有权限发送公告消息！')
        return redirect('message_list')

#公告消息列表
def message_list(request):  #消息（公告）列表
    pinned_messages = Message.objects.filter(is_pinned=True).order_by('-date')  # 获取所有置顶的消息并按日期降序排序
    non_pinned_messages = Message.objects.filter(is_pinned=False).order_by('-date')  # 获取所有未置顶的消息并按日期降序排序
    messages = list(pinned_messages) + list(non_pinned_messages)  # 将两个列表合并
    shanchu = "<a href=\"{% url 'delete_message' xiaoxi.id %}\" class=\"btn btn-danger btn-sm\" onclick=\"return confirm('确定要删除这条消息吗？')\">删除</a>"
    return render(request, 'message_list.html', {'xiaoxi': messages,'shanchu':shanchu})

#公告置顶、取消置顶
def toggle_pin_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    message.is_pinned = not message.is_pinned
    message.save()
    return redirect('message_list')

#删除公告消息
def delete_message(request, message_id):    #管理员删除消息（公告）
    # 获取当前用户id
    uID = request.session.get("_auth_user_id")
    # 根据当前用户id获取用户对象
    user = User.objects.get(id=uID)
    qx_user = user.username
    #获取用户名
    if user.is_superuser == True:
        message = get_object_or_404(Message, id=message_id)
        message.delete()
        return redirect('message_list')
    else:
        messages.warning(request, f'尊敬的{qx_user}用户，您没有权限删除消息！')
        return redirect('message_list')

#管理员编辑消息(公告)
def edit_message(request, message_id):  
    # 获取当前用户id
    uID = request.session.get("_auth_user_id")
    # 根据当前用户id获取用户对象
    user = User.objects.get(id=uID)
    qx_user = user.username
    #获取用户名
    if user.is_superuser == True:
        message = get_object_or_404(Message, id=message_id)
        if request.method == 'POST':
            form = MessageForm(request.POST, instance=message)
            if form.is_valid():
                form.save()
                messages.success(request, f'尊敬的{qx_user}用户，您编辑的公告更新成功！')
                return redirect('message_list')
        else:
            form = MessageForm(instance=message)
        return render(request, 'edit_message.html', {'form': form})
    else:
        messages.warning(request, f'尊敬的{qx_user}用户，您没有权限编辑公告消息！')
        return redirect('message_list')