#!/bin/sh

#---数据库配置---#

#安装mariadbs数据库客户端和服务端
sudo yum -y install mariadb-server && \

#启动mariadb数据库
sudo systemctl start mariadb && \

#设置mariadb数据库开机自启动
sudo systemctl enable mariadb && \

#设置数据库密码
sudo mysqladmin -u root password 'hil@12345' && \

#进入数据库创建对应的数据库以及设置字符编码与权限
mysql -u root -phil@12345<<EOF
create database homework;
use homework;
alter database homework character set utf8;
grant all privileges on homework.* to 'root'@'127.0.0.1' identified by 'hil@12345';
EOF

#---django环境准备---#

#安装python3
yum -y install python3 && \

#安装django2:1
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple "django==2.1.*" && \

#安装mysql客户端
yum -y install mysql-devel && \
yum -y install python36-devel && \
yum -y install gcc && \
pip3 install mysqlclient && \

#升级pip3
pip3 install --upgrade pip && \

#安装验证码图像库和安装富文本编辑器
pip3 install Pillow && \
pip3 install django-simple-captcha && \
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple django-tinymce && \

#---配置防火墙---#
firewall-cmd --zone=public --add-port=80/tcp --permanent && \
firewall-cmd --zone=public --add-port=3306/tcp --permanent && \
firewall-cmd --reload && \

#---配置项目---#
cd ./web/homework && \
python3 manage.py makemigrations && \
python3 manage.py migrate && \
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'homework@admin123')" | python3 manage.py shell && \

echo "yes" | python3 manage.py collectstatic  && \

#输出信息
RED='\033[0;31m' && \
GREEN='\033[0;32m' && \
YELLOW='\033[0;33m' && \
RESET='\033[0m' && \

success_message="${GREEN}恭喜您成功部署好了【一站式任务收集平台】${RESET}" && \
admin_username="${YELLOW}默认管理员用户名：admin${RESET}" && \
admin_password="${YELLOW}默认管理员密码：homework@admin123${RESET}" && \
start_message="${RED}下面就可以开始使用啦，请运行start.sh脚本${RESET}" && \

echo -e "╔════════════════════════════════════════════════════════════╗" && \
echo -e "║                                                            ║" && \
echo -e "║          $success_message          ║" && \
echo -e "║                                                            ║" && \
echo -e "║          $admin_username                           ║" && \
echo -e "║          $admin_password                 ║" && \
echo -e "║                                                            ║" && \
echo -e "║          $start_message          ║" && \
echo -e "║                                                            ║" && \
echo -e "╚════════════════════════════════════════════════════════════╝"