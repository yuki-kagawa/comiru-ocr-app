from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views
from .forms import EmailLoginForm
from .views import SignupView

app_name = 'accounts'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('password_change/',
         auth_views.PasswordChangeView.as_view(success_url=reverse_lazy('accounts:password_change_done')),
         name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('mypage/', views.mypage, name='mypage'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('child/add/', views.child_add, name='child_add'),
    path('child/select/<int:child_id>/', views.set_select_child, name='set_select_child'),
    path('child/<int:child_id>/edit/', views.child_edit, name='child_edit'),
    path('child/delete/<int:child_id>/', views.child_delete, name='child_delete'),
]
