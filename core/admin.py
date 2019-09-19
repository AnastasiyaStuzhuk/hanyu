from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin
from .models import WordCard, Course, Lesson, TestResult, Student
# Register your models here.

admin.site.register(WordCard)
admin.site.register(Course)
admin.site.register(Student)
admin.site.register(TestResult)
admin.site.register(Lesson, MarkdownxModelAdmin)
