from django.urls import path, include, reverse
from .views import IndexView, CoursesView, CourseDetailView, LessonDetailView, TestView, CharactersView
from django_registration.backends.one_step.views import RegistrationView
from django.contrib.auth.views import LoginView

urlpatterns = [
    path('', IndexView.as_view()),
    path('accounts/register/',
        RegistrationView.as_view(
            template_name='registration/registration_form.html',
            success_url='/'),
        name='django_registration_register'),
    path('accounts/login/',
        LoginView.as_view(
            template_name='registration/login.html',
            redirect_authenticated_user=True),
        name='django_registration_register'),
    path('accounts/', include('django_registration.backends.one_step.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('courses/', CoursesView.as_view(), name='courses'),
    path('characters/', CharactersView.as_view(), name='characters'),
    path('course/<int:pk>', CourseDetailView.as_view(), name='course'),
    path('lesson/test/<int:lesson_id>', TestView.as_view(), name='test'),
    path('lesson/<int:pk>', LessonDetailView.as_view(), name='lesson'),
]
