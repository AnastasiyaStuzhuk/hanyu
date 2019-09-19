from django.shortcuts import render, redirect
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseBadRequest
from django.db.models import Q
from django.urls import reverse
from .models import Course, Lesson, Test, TestWord, TestResult
from random import shuffle

# Create your views here.

class IndexView(generic.TemplateView):
  template_name='index.html'

class CharactersView(generic.TemplateView):
  template_name='characters.html'

class CoursesView(generic.ListView, LoginRequiredMixin):
  template_name='courses.html'
  model = Course

class CourseDetailView(generic.DetailView, LoginRequiredMixin):
  template_name='course-detail.html'
  model = Course

  def get(self, request, *args, **kwargs):
    self.object = self.get_object()
    context = self.get_context_data(object=self.object)
    opened_lessons = list(request.user.student.opened_lessons.filter(
      course=self.object
    ))
    lessons = list(self.object.lessons.all())
    if len(opened_lessons) == 0:
      opened_lessons = lessons[0:1]
    opened_lessons_length = len(opened_lessons)
    closed_lessons = lessons[opened_lessons_length:]
    context['opened_lessons'] = opened_lessons
    context['closed_lessons'] = closed_lessons
    return self.render_to_response(context)

class LessonDetailView(generic.DetailView, LoginRequiredMixin):
  template_name='lesson-detail.html'
  model = Lesson

  def get(self, request, *args, **kwargs):
    self.object = self.get_object()
    if not self.object.number == 0 and not request.user.student.opened_lessons.filter(id=self.object.id).exists():
      return redirect(reverse('course', kwargs={'pk': self.object.course.id}))
    context = self.get_context_data(object=self.object)
    return self.render_to_response(context)

class TestView(generic.View, LoginRequiredMixin):
  
  def get(self, request, *args, lesson_id, **kwargs):

    lesson = Lesson.objects.get(pk=lesson_id)
    try:
      test = lesson.tests.get(user__id=request.user.id)
      return self.render_test(request, test, lesson)
    except Test.DoesNotExist:
      test = Test.objects.create(user=request.user, lesson=lesson)
      
    lesson_words = list(lesson.words.all())
    test.words_count = words_count = len(lesson_words) // 2
    shuffle(lesson_words)
    for i in range(words_count):
      word = lesson_words[i]
      TestWord.objects.create(word=word, test=test, number=i)
      test.save()
    
    return self.render_test(request, test, lesson)

  def post(self, request, *args, lesson_id, **kwargs):
    lesson = Lesson.objects.get(pk=lesson_id)
    try:
      test = lesson.tests.get(user__id=request.user.id)
    except Test.DoesNotExist:
      return redirect('/')
    
    user_response = request.POST.get('response')
    word_number = request.POST.get('word_number')
    if not user_response or not word_number:
      return self.render_test(request, test, lesson)

    user_response = int(user_response)
    word_number = int(word_number)

    try:
      TestWord.objects.get(number=word_number, word__pk=user_response, test=test)
      test.points += 1
    except TestWord.DoesNotExist:
      pass
    if test.words_count == test.current_word_index + 1:
      return self.handle_test_end(request, test, lesson)
    else:
      test.current_word_index += 1
      test.save()
      return self.render_test(request, test, lesson)

  def handle_test_end(self, request, test, lesson):
    test_result = TestResult.objects.create(
      lesson=lesson,
      user=request.user,
      words_count=test.words_count,
      points=test.points
    )
    if test_result.points / test_result.words_count >= 0.75:
      self.add_next_lesson_for_student(request.user.student, lesson)
    test.delete()
    return render(request, 'test-result.html', { 'test_result': test_result })
  
  def add_next_lesson_for_student(self, student, lesson):
    new_lesson_q = Q(
      course=lesson.course,
      number=lesson.number + 1
    )
    if lesson.number == 0:
      new_lesson_q = new_lesson_q | Q(
        course=lesson.course,
        number=0
      )
    new_lessons = list(Lesson.objects.filter(new_lesson_q))
    student.opened_lessons.add(*new_lessons)

  def render_test(self, request, test, lesson):
    current_word = test.words.all()[test.current_word_index]
    lesson_words = list(lesson.words.exclude(id=current_word.id))
    shuffle(lesson_words)
    variants = lesson_words[0:3]
    variants.append(current_word)
    shuffle(variants)
    context = { 'word' : current_word, 'variants': variants, 'word_number': test.current_word_index }
    return render(request, 'test.html', context)
