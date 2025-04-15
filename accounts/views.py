from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .models import Child, User
from .forms import ChildForm, CustomUserCreationForm
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from django.urls import reverse_lazy
from django.views.generic import CreateView

def root_redirect_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:mypage')
    else:
        return redirect('accounts:login')

@method_decorator(sensitive_post_parameters('password1', 'password2'), name='dispatch')
class SignupView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('accounts:mypage')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)  # 自動ログイン
        messages.success(self.request, 'アカウントを作成しました。')
        return response


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('accounts:mypage')
        else:
            messages.error(request, 'ログイン情報が正しくありません。')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('accounts:login')

@login_required
def mypage(request):
    children = Child.objects.filter(parent=request.user).order_by('-birthday')
    selected_id = request.session.get("selected_child_id")

    return render(request, 'accounts/mypage.html', {
        'children': children,
        'selected_child_id': selected_id,
    })


@login_required
def set_select_child(request, child_id):
    child = get_object_or_404(Child, id=child_id, parent=request.user)
    request.session['selected_child_id'] = child.id
    request.session['selected_child_name'] = child.name
    messages.success(request, f"{child.name} を選択しました。")
    return redirect('accounts:mypage')

@login_required
def child_add(request):
    if request.method == 'POST':
        form = ChildForm(request.POST)
        if form.is_valid():
            child = form.save(commit=False)
            child.parent = request.user
            child.save()
            return redirect('accounts:mypage')
    else:
        form = ChildForm()
    return render(request, 'accounts/child_add.html', {'form': form})

@login_required
def child_edit(request, child_id):
    child = get_object_or_404(Child, id=child_id, parent=request.user)

    if request.method == 'POST':
        form = ChildForm(request.POST, instance=child)
        if form.is_valid():
            form.save()
            return redirect('accounts:mypage')
    else:
        form = ChildForm(instance=child)

    return render(request, 'accounts/child_edit.html', {'form': form, 'child': child})

@login_required
def child_delete(request, child_id):
    child = get_object_or_404(Child, id=child_id, parent=request.user)
    if request.method == 'POST':
        child.delete()
        return redirect('accounts:mypage')
    return render(request, 'accounts/child_delete.html', {'child': child})

