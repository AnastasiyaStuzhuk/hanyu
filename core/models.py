from django.db import models
from django.db.models.signals import pre_save, post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify

# Create your models here.

class Course(models.Model):
  name = models.CharField(max_length=255)
  description = models.TextField(max_length=1024)
  thumbnail = models.ImageField(null=True, blank=True)
  number = models.IntegerField(default=0)

  class Meta:
    ordering = ['number']

  def __str__(self):
        return  self.name

class Lesson(models.Model):
  name = models.CharField(max_length=255)
  thumbnail = models.ImageField(null=True, blank=True)
  content = MarkdownxField()
  formatted_content = models.TextField(editable=False, default="")
  grammar = MarkdownxField()
  formatted_grammar = models.TextField(editable=False, default="")

  course = models.ForeignKey(
    Course,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='lessons',
    related_query_name='lesson',
  )

  number = models.IntegerField(default=0)

  class Meta:
    ordering = ['number']

  def __str__(self):
      return  self.name

class Student(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  opened_lessons = models.ManyToManyField(
    Lesson,
    related_name='students',
    related_query_name='student',
  )

class TestResult(models.Model):
  lesson = models.ForeignKey(
    Lesson,
    on_delete=models.CASCADE,
    related_name='test_results',
    related_query_name='test_result',
  )
  user = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    related_name='test_results',
    related_query_name='test_result',
  )

  created_at = models.DateField(auto_now_add=True, editable=False)
  words_count = models.IntegerField(default=0)
  points = models.IntegerField(default=0)

class WordCard(models.Model):
  hieroglyph = models.CharField(max_length=20)
  translation = models.CharField(max_length=512)
  transcription = models.CharField(max_length=255)
  thumbnail = models.ImageField(null=True, blank=True)
  lesson = models.ForeignKey(
    Lesson,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="words",
    related_query_name="word"
  )

  def __str__(self):
        return  self.hieroglyph + ' | ' + self.translation


class Test(models.Model):
  user = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    related_name='tests',
    related_query_name='test',
  )

  lesson = models.ForeignKey(
    Lesson,
    related_name='tests',
    related_query_name='test',
    on_delete=models.CASCADE
  )

  words = models.ManyToManyField(
    WordCard,
    through='TestWord',
  )

  words_count = models.IntegerField(default=0)
  current_word_index = models.IntegerField(default=0)
  points = models.IntegerField(default=0)

class TestWord(models.Model):
  word = models.ForeignKey(
    WordCard,
    related_name='+',
    related_query_name='+',
    on_delete=models.CASCADE
  )

  test = models.ForeignKey(
    Test,
    related_name='test_words',
    related_query_name='test_word',
    on_delete=models.CASCADE
  )

  number = models.IntegerField(default=0)

  class Meta:
    ordering = ['number']

@receiver(pre_save, sender=Lesson)
def formatter_handler(sender, instance, **kwargs):
  instance.formatted_content = markdownify(instance.content)
  instance.formatted_grammar = markdownify(instance.grammar)

@receiver(post_save, sender=User)
def create_student(sender, instance, created, **kwargs):
  if created:
    Student.objects.create(user=instance)