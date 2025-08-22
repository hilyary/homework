from django import forms  # 导入Django表单类，用于创建表单
from django.contrib.auth.models import User  # 导入Django内置的用户模型类
from .models import TaskMatch  # 导入TaskMatch模型类
from .models import Message


class UserForm(forms.ModelForm):  # 定义UserForm表单类，继承自forms.ModelForm类
    class Meta:
        model = User  # 指定表单使用的模型类为User
        fields = ['username', 'email', 'first_name', 'last_name']  # 指定表单需要显示的字段

    def __init__(self, *args, **kwargs):  # 重写__init__方法，用于设置表单字段的属性
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['readonly'] = True  # 将用户名字段设置为只读
        self.fields['email'].widget.attrs['readonly'] = True  # 将电子邮件字段设置为只读

class MatchForm(forms.ModelForm):  # 定义MatchForm表单类，继承自forms.ModelForm类
    name_patterns = forms.CharField(max_length=1000, label='学号-姓名匹配模式',  # 定义name_patterns字段，用于存储学号-姓名匹配模式，最大长度为1000，设置表单中的标签
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': '例如：20230101-张三\n20230102-李四\n20230103-王五'}))  # 将字段的widget设置为Textarea类型，指定CSS类和占位符

    class Meta:
        model = TaskMatch  # 指定表单使用的模型类为TaskMatch
        fields = ['name_patterns']  # 指定表单需要显示的字段
        labels = {'name_patterns': '学号-姓名匹配模式'}  # 设置表单中的标签，将name_patterns字段的标签设置为“学号-姓名匹配模式”

# 定义一个名为 MessageForm 的表单类，它继承自 forms.ModelForm
class MessageForm(forms.ModelForm):
    # Meta 是一个内部类，它定义了一些 Django 模型表单的行为
    class Meta:
        # 指定这个表单关联的模型是 Message
        model = Message
        # 定义这个表单包含的字段，这里包含 'title' 和 'content' 两个字段
        fields = ['title', 'content']