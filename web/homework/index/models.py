# Create your models here.
from django.db import models  # 导入Django模型类，用于创建数据库表
import time  # 导入time模块，用于处理时间相关的操作
from django.contrib.auth.models import User


class CollectionTask(models.Model):  # 定义CollectionTask模型类，继承自models.Model类
    name = models.CharField(max_length=100, verbose_name='任务名字')  # CharField类型，存储任务名字，最大长度为100，verbose_name用于设置在Django Admin中显示的名称
    creator = models.CharField(max_length=100, verbose_name='创建人')  # CharField类型，存储创建人，最大长度为100
    create_time = models.DateTimeField(default=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), verbose_name='创建时间')  # DateTimeField类型，存储创建时间，默认为当前时间
    file_path = models.CharField(max_length=200, verbose_name='收集文件路径')  # CharField类型，存储收集文件路径，最大长度为200

    def __str__(self):  # 重写__str__方法，用于在Django Admin中显示任务名字
        return self.name

    def get_matches(self):  # 定义get_matches方法，用于获取任务匹配对象
        return TaskMatch.objects.filter(task=self) if self.id else TaskMatch.objects.none()  # 如果任务存在，则获取匹配对象，否则返回空对象

class TaskMatch(models.Model):  # 定义TaskMatch模型类，继承自models.Model类
    task = models.ForeignKey(CollectionTask, on_delete=models.CASCADE, blank=True, null=True)  # ForeignKey类型，与CollectionTask模型相关联，用于存储任务匹配对象
    name_pattern = models.CharField(max_length=100, blank=True, null=True)  # CharField类型，存储匹配对象的名字，最大长度为100，可以为空
    creator = models.CharField(max_length=100, blank=True)  # CharField类型，最大长度为100，可以为空

    def __str__(self):  # 重写__str__方法，用于在Django Admin中显示匹配对象
        return f'{self.name_pattern} ({self.task.name})'  # 返回匹配对象的名字和所属任务的名字
    
# 定义一个名为 Message 的模型类，它继承自 models.Model
class Message(models.Model):
    # 定义一个字符字段（CharField），用于存储消息的标题，最大长度是200
    title = models.CharField(max_length=200)
    # 定义一个文本字段（TextField），用于存储消息的内容
    content = models.TextField()
    # 定义一个日期时间字段（DateTimeField），用于存储消息的创建时间，默认值是当前的日期和时间
    date = models.DateTimeField(default=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), verbose_name='创建时间')
    # 定义一个外键字段（ForeignKey），用于关联 User 模型，表示消息的发送者，如果关联的 User 被删除，那么这个消息也会被删除（models.CASCADE）
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    is_pinned = models.BooleanField(default=False)