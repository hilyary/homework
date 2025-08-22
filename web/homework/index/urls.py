#index urls.py
from django.urls import path,include
from .views import delete_user
from .views import *
from . import views
from django.views.generic.base import RedirectView  # 导入RedirectView类，用于重定向到指定的URL
from django.urls import path

urlpatterns = [
    #用户管理
    path('',RedirectView.as_view(pattern_name='login')),#访问IP/index/就跳转到登录页面(/index/login/)
    path("vcode/",views.varityCody),    #验证码功能
    path("captcha/",include("captcha.urls")),
    path("login/",views.indexLogin,name="login"),    #登录功能
    path("fhdl/",views.fhdl,name="fhdl"),    #登录功能
    path("manage/",views.managePage,name="manage"),    #管理页面
    path("logout_view/",views.logout_view,name="logout_view"), #退出登录
    path("changepass/",views.changepass,name="changepass"),    #改密码
    path("change_user_pass/<int:user_id>/",views.change_user_pass,name="change_user_pass"),#管理员改其他用户密码
    path("createuser/",views.createuser,name="createuser"),    #创建用户
    path("zhuye/",views.zhuye,name="zhuye"), #返回到管理页面
    path("yhym/",views.yhym,name="yhym"), #返回到用户管理页面
    path("user_list/",views.user_list,name="user_list"),  #用户列表
    path("update_user/<int:user_id>/",views.update_user,name="update_user"),  #编辑用户信息
    path("delete_user/<int:user_id>/",delete_user,name="delete_user"), #删除用户
    
    #任务管理
    path('list_tasks/', list_collection_tasks, name='list_tasks'), #收集任务列表
    path("rwlb/",views.fh_rwlb,name="rwlb"),  #返回任务列表
    path('add/', add_collection_task, name='add_task'), #创建收集任务
    path('edit/<int:task_id>/', edit_collection_task, name='edit_task'),    #编辑收集任务
    path('delete/<int:task_id>/', delete_collection_task, name='delete_task'),  #删除收集任务
    path('download/<int:task_id>/', download_collection_task, name='download_task'),    #打包下载
    path('<int:task_id>/upload/', upload_file, name='upload_file'), # 添加上传文件URL路径
    path('<int:task_id>/add_match/',views.add_match, name='add_match'), #添加类似学号-姓名匹配项
    path('<int:task_id>/upload_work_jilu', views.upload_work_jilu, name='upload_work_jilu'), # 提交记录
    path('check_submission/<int:task_id>/', views.check_submission, name='check_submission'),   #未提交记录

    #找回密码
    path('password_find/', views.password_find, name='password_find'),  #找回密码
    path('check_code/', views.check_code, name='check_code'),   #检测验证
    path('password_reset/<uid>/<token>/', views.password_reset, name='password_reset'), #重设密码
    path('zhmm/',views.zhmm,name="zhmm"),   #跳转到找回密码页面

    #公告消息
    path('send_message/', views.send_message, name='send_message'), #发送公告消息
    path('messages/', views.message_list, name='message_list'), #公告消息列表
    path('delete_message/<int:message_id>/', views.delete_message, name='delete_message'),  #删除公告消息
    path('edit_message/<int:message_id>/', views.edit_message, name='edit_message'),    #编辑公告消息
    path('toggle_pin_message/<int:message_id>/', views.toggle_pin_message, name='toggle_pin_message'),  #置顶公告


]