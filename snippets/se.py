#Serializer이란?

#serializers: 쿼리셋, 모델 인스턴스 등의 복잡한 데이터를 JSON, XML 등의 컨셉트 타입으로 쉽게 변환 
#가능한 python datatype으로 변환 시키는것.

#deserialization : 받은 데이터를 validating 한 후에 parsed data를 complex type으로 다시 변환

#python manage.py startapp snippet을 해주고
#INSTALLED_APPS = ['rest_framework', 'snippets.apps.SnippetsConfig']
#을 추가해주고
#project 이름이 tutorail
# app name snippets


#snippets/models.py
from django.db import models
from pygments.lexers import get_all_lexers
from pygments.styles import get_all_styles

LEXERS = [item for item in get_all_lexers() if item[1]]
LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS])
STYLE_CHOICES = sorted([(item, item) for item in get_all_styles()])


class Snippet(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, blank=True, default='')
    code = models.TextField()
    linenos = models.BooleanField(default=False)
    language = models.CharField(choices=LANGUAGE_CHOICES, default='python', max_length=100)
    style = models.CharField(choices=STYLE_CHOICES, default='friendly', max_length=100)

    class Meta:
        ordering = ['created']
#Creating a Serializer class 
#snippet instances => representations such as json
#by declaring serializers
#make file = snippets/serializers.py
#and add the following.

from rest_framework import serializers
from snippets.models import Snippet, LANGUAGE_CHOICES, STYLE_CHOICES

#클래스에서 serialized/deserialized 할 필드를 정의내린다.

class SnippetSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(required=False, allow_blank=True, max_length=100)
    code = serializers.CharField(style={'base_template': 'textarea.html'})
    linenos = serializers.BooleanField(required=False)
    language = serializers.ChoiceField(choices=LANGUAGE_CHOICES, default='python')
    style = serializers.ChoiceField(choices=STYLE_CHOICES, default='friendly')

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return Snippet.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the validated data.
        """
        instance.title = validated_data.get('title', instance.title)
        instance.code = validated_data.get('code', instance.code)
        instance.linenos = validated_data.get('linenos', instance.linenos)
        instance.language = validated_data.get('language', instance.language)
        instance.style = validated_data.get('style', instance.style)
        instance.save()
        return instance


#Django shell에 들어가봐



















from datatime import datatime

class Comment(object):
    def __init__(self, email, content, created=None):
        self.email = email
        self.content = content
        self.created = created or datatime.now()

comment = Comment(email='exid0429@gmail.com', content = 'boo far')

#데이터를 serialize, deserialize 하기 위해 serializer을 선언

from rest_framework import serializers

class CommentSerializer(serializers.Serializer):
    email = serializers.EmailField()
    content = serializers.CharField(max_length=200)
    created = serializers.DateTimeField

#CommentSerializer을 통해 comment(list)을 serialize 할 수 있다.
# comment을 serialize하겠다. 저 email이랑 content을
serialzer = CommentSerializer(comment)
serializer.data
#{'email': 'exid0429@gmai.com', 'content' : 'boo far'....}
#json type

#data을 json 타입으로 변환
