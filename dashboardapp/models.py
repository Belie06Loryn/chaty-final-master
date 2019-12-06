from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Category(models.Model):
    category_name = models.CharField(max_length = 30, null=True)
    category_image = models.ImageField(upload_to='category_image/',blank=True,null = True)
    description = models.CharField(max_length = 300, null = True)

    def __str__(self):
        return self.category_name

class Question(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    title=models.CharField(max_length=300)
    content=models.TextField(blank=True)
    snippet=models.ImageField(upload_to='question/',blank =True, null=True)
    category=models.ForeignKey(Category, related_name='category',on_delete=models.CASCADE)

    @classmethod
    def get_all_questions(cls):
        questions = cls.objects.all().prefetch_related('answer_set')
        return questions

    @classmethod
    def search_by_title(cls,search_term):
        questions = cls.objects.filter(title__icontains = search_term)
        return questions

    @classmethod
    def filter_by_category_id(cls,id):
        Q_questions = cls.objects.filter(id = id)
        return Q_questions
    
    def __str__(self):
        return self.title
  

class Profile(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    coverimage=models.ImageField(upload_to='profile/',blank=True)
    image=models.ImageField(upload_to='profile/',blank=True)
    name=models.CharField(max_length=30,blank=True)
    bio=models.CharField(max_length=30,blank=True)
    email=models.EmailField(max_length=254,blank=True)
    facebook_page = models.URLField(blank=True)
    twitter_link = models .URLField(blank=True)

    def __str__(self):
        return self.user

class Answer(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    question=models.ForeignKey(Question,on_delete=models.CASCADE)
    upvotes=models.ManyToManyField(User, blank=True,related_name='answer_upvotes')
    downvotes=models.ManyToManyField(User, blank=True,related_name='answer_downvotes')
    answer=models.TextField()

    def __str__(self):
        return self.answer

class Approved(models.Model):
    name=models.OneToOneField(Profile,on_delete=models.CASCADE)
    answer=models.OneToOneField(Answer,on_delete=models.CASCADE)
    approve=models.BooleanField()
    score=models.IntegerField()

    def __str__(self):
        return self.name.user.username

class Vote(models.Model):
    name=models.ForeignKey(Profile,on_delete=models.CASCADE)
    answer=models.ForeignKey(Answer,on_delete=models.CASCADE)
    vote=models.IntegerField()


    def __str__(self):
        return self.name.user.username

class Invitation(models.Model):
    name=models.CharField(max_length=30)
    email=models.EmailField()

class Approved(models.Model):
    approve=models.BooleanField()
    question=models.ForeignKey(Question, on_delete=models.CASCADE)
    answer=models.OneToOneField(Answer, on_delete=models.CASCADE)

