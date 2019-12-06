from django.shortcuts import render,redirect
from django.http  import HttpResponse,Http404,HttpResponseRedirect
from .models import Question,Category,Answer,Profile,Approved
from .forms import NewQuestionForm,AnswerForm,ProfileForm,ApproveForm
from django.contrib.auth.decorators import login_required
from .models import Question,Invitation
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from .forms import UserRegistrationForm
from django.contrib import messages
from django.contrib.auth import login,logout, authenticate
from .email import send_welcome_email
from django.contrib.auth.models import User
from django.db.models import Count

# Create your views here.
@login_required(login_url='/accounts/login/')
def page(request):
    categories = Category.objects.all()
    return render(request,'all-pages/index.html',{"categories": categories})

# @login_required(login_url='/accounts/login/')
def question_category(request, id):
    q_category = Category.objects.filter(id = id).first()
    questions = Question.objects.filter(category = q_category.id).all()
    return render(request,'all-pages/question_category.html',{'q_category':q_category,"id":id,"questions":questions})

@login_required(login_url='/accounts/login/')
def learn(request,profile_id):
    post_question = Question.objects.all()
    current_user = request.user
    user = User.objects.get(pk=profile_id)
    profile = Profile.objects.filter(user=profile_id)
    return render(request,'all-pages/learn.html',{"profile":profile,"post_question":post_question})  

@login_required(login_url='/accounts/login/')
# def question_answer(request, id):
#     questions = Question.objects.filter(id = id).first()
#     q_category = Category.objects.filter(id = questions.category.id).first() 
#     answer = Answer.objects.filter(question = questions.id).all()
#     related_question = Question.objects.filter(category = q_category.id).all()
#     return render(request,'all-pages/answers.html',{'q_category':q_category,"id":id,"questions":questions,"related_question":related_question,"answer":answer})

def question_answer(request, id):
    questions = Question.objects.filter(id = id).first()
    q_category = Category.objects.filter(id = questions.category.id).first() 
    answer = Answer.objects.filter(question = questions.id).order_by('-upvotes')
    # sorted_answer= sorted(answer, key= lambda answer:answer.upvotes.count(), reverse=True)
    sorted_answer = Answer.objects.annotate(answer_count=Count('upvotes')).order_by('answer_count')
    related_question = Question.objects.filter(category = q_category.id).all()
    form = ApproveForm()
    return render(request,'all-pages/answers.html',{'q_category':q_category,"id":id,"questions":questions,"related_question":related_question,"answer":sorted_answer,'form':form})

@login_required(login_url='/accounts/login/')
def post_question(request):
    current_user = request.user
    profiles = Profile.objects.filter(user = current_user.id).first()
    if request.method == 'POST':
        form = NewQuestionForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = current_user
            post.save()
            return redirect('learn')

    else:
        form = NewQuestionForm()
    return render(request, 'all-pages/post_question.html', {"form": form})

@login_required(login_url='/accounts/login')
def post_answer(request, id):
    current_user = request.user
    question = Question.objects.filter(id=id).first()
    profiles = Profile.objects.filter(user = current_user.id).first()
    if request.method == 'POST':
        form = AnswerForm(request.POST,request.FILES)
        if form.is_valid():
            answers = form.save(commit=False)
            answers.user = current_user
            answers.question = question
            answers.save()
            return redirect('q_answer', id)
    else:
        form = AnswerForm()
    title = "Question"
    return render(request, 'all-pages/add_answer.html',{"form":form, "id":id} )


@login_required(login_url='/accounts/login')
def new_profile(request):
    current_user = request.user
    if request.method == 'POST':
        if Profile.objects.filter(user_id=current_user).exists():
            form = ProfileForm(request.POST, request.FILES,instance=Profile.objects.get(user_id=current_user))
        else:
            form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = current_user
            profile.save()
        return redirect('profile',current_user.id)
    else:
        if Profile.objects.filter(user_id=current_user).exists():
            form = ProfileForm(instance = Profile.objects.get(user_id=current_user))
        else:
            form = ProfileForm()
    return render(request, 'all-pages/new-profile.html', {"form": form})

@login_required(login_url='/accounts/login')
def profile(request,profile_id):
    current_user = request.user
    user = User.objects.get(pk=profile_id)
    profile = Profile.objects.filter(user=profile_id)
    questions=Question.objects.filter(user=current_user) 
    return render (request, 'all-pages/profile.html', {'profile':profile,'questions':questions})

@login_required(login_url='/accounts/login')
def search_question(request):
    if 'question' in request.GET and request.GET["question"]:
        search_term = request.GET.get("question")
        searched_question = Question.search_by_title(search_term)
        message = f"{search_term}"
        return render(request, "all-pages/search.html",{"message":message,"questions": searched_question})
    else:
        message = "You haven't searched for any term"
        return render(request, 'all-pages/search.html',{"message":message})

def upvotes(request,answer_id):
    answer=Answer.objects.get(pk=answer_id)
    if answer.upvotes.filter(id=request.user.id).exists():
            answer.upvotes.remove(request.user)
    else:
        answer.upvotes.add(request.user)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
def downvotes(request,answer_id):
    answer=Answer.objects.get(pk=answer_id)
    if answer.downvotes.filter(id=request.user.id).exists():
            answer.downvotes.remove(request.user)
    else:
        answer.downvotes.add(request.user)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def signUp(request):
    currentUser=request.user
    if request.method=='POST':
        form=UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username=form.cleaned_data.get('username')
            email=form.cleaned_data.get('email')
            send_welcome_email(username,email)
            messages.success(request,f'{username} , your account was successfuly created check your email to log in')
            return redirect('http://127.0.0.1:8000/admin/')
    else:
        form=UserRegistrationForm()
    return render(request,'auth/signUp.html',{'form':form})

def approve_answer(request, id):
    current_user = request.user
    question = Question.objects.filter(id=id).first()
    answer = Answer.objects.filter(question=question).first()
    profiles = Profile.objects.filter(user = current_user.id).first()
    if request.method == 'POST':
        form = ApproveForm(request.POST,request.FILES)
        if form.is_valid():
            approveAnswer = form.save(commit=False)
            approveAnswer.user = current_user
            approveAnswer.answer = answer
            approveAnswer.question=question
            approveAnswer.save()
            return redirect('learn')
    else:
        form = AnswerForm()
    title = "approve"
    return render(request, 'all-pages/answer.html',{"form":form, "id":id,'question':question,'answer':answer} )
        
def logIn(request):
    if request.method=='POST':
        form=AuthenticationForm(data=request.POST)
        if form.is_valid():
            user=form.get_user()
            login(request,user)
            if 'next' in request.POST:
                return redirect(request.POST.get('next'))
            else:
                return redirect('page')
    else:
        form=AuthenticationForm()
    return render(request,'auth/logIn.html',{'form':form})
def logOut(request):
    if request.method=='POST':
        logout(request)
    return redirect('logIn')

