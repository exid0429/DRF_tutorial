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
#python manage.py shell

from snippets.models import Snippet
from snippets.serializers import SnippetSerializer
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

snippet = Snippet(code='foo = "bar"\n')
snippet.save()

snippet = Snippet(code='print("hello, world")\n')
snippet.save()

serializer = SnippetSerializer(snippet)
serializer.data
# {'id': 2, 'title': '', 'code': 'print("hello, world")\n', 
#'linenos': False, 'language': 'python', 
#'style': 'friendly'}
#이렇게 하면 python native datatype으로 바꿨다.
#serialization process을 끝마치기 위해 data을 json으로 하자.

content = JSONRenderer().render(serializer.data)
content
# b'{"id": 2, "title": "", "code": "print(\\"hello, world\\")\\n", "linenos": false, "language": "python", "style": "friendly"}'

#Deserialzaation도 비슷한데. parse을 해서 python native datatype으로 해주자.
import io
stream = io.BytesIO(content)
data = JSONParser().parse(stream)

# python native datatype => object instance
serializer = SnippetSerializer(data=data)
serializer.is_valid() # true
serializer.validated_data
serializer.save()
# <Snippet: Snippet object>
serializer = SnippetSerializer(Snippet.objects.all(), many=True)
serializer.data
# [OrderedDict([('id', 1), ('title', ''), ('code', 'foo = "bar"\n'), ('linenos', False), ('language', 'python'), ('style', 'friendly')]), OrderedDict([('id', 2), ('title', ''), ('code', 'print("hello, world")\n'), ('linenos', False), ('language', 'python'), ('style', 'friendly')]), OrderedDict([('id', 3), ('title', ''), ('code', 'print("hello, world")'), ('linenos', False), ('language', 'python'), ('style', 'friendly')])]


#Using ModelSerializers
#좀더 간결하게

#snippets/serializers.py 을 이걸로 바꿔
class SnippetSerializer(serializers.Modelerializer):
    class Meta:
        model = Snippet
        fields = ['id', 'title', 'code', 'linenos', 'language', 'style']


from snippets.serializers import SnippetSerializer
serializer = SnippetSerializer()
print(repr(serializer))

#Writing regular Django views using our Serializer
#new serializer class을 이용해서 api을 만들어보자.

#snippets/views.py
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from snippets.models import Snippet
from snippets.serializers import SnippetSerializer

#Api는 스니펫리스트들을 보여주는 뷰일거야.

@csrf_exempt
def snippet_list(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method === 'GET':
        snippets = Snippet.objects.all()
        serializer = SnippetSerializer(snippets, many=True)
        return JsonResponse(serialzer.data, safe=False)

    elif request.method === 'POST':
        data = JSONParser().parse(request)
        serializer = SnippetSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

@csrf_exempt
def snippet_detail(request, pk):
    """
    Retrieve, update or delete a code snippet.
    """
    try:
        snippet = Snippet.objects.get(pk=pk)
    except Snippet.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = SnippetSerializer(snippet)
        return JsonResponse(serializer.data)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = SnippetSerializer(snippet, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        snippet.delete()
        return HttpResponse(status=204)

#snippets/urls.py
from django.urls import path
from snippets import views

urlpatterns = [
    path('snippets/', views.snippet_list),
    path('snippets/<int:pk>/', views.snippet_detail),
]

#tutorial/urls.py

from django.urls import path, include

urlpatterns = [
    path('', include('snippets.urls')),
]

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


#Chapter2
#Request objects
#Request 객체는 HttpRequest을 확장하여 좀더 유연하게 요청을 파싱한다.

request.POST #Form 데이터만 다루고, 오로지 POST 메서드에서만 사용이 가능함
request.data #아무 데이터나 다룰수 있다. POST, PUT, PATCH

return Response(data) # 클라가 원하는 형태로 컨텐츠를 렌더링한다.

#status codes : drf에서는 숫자로 된 식별자보단 문자 형태의 식별자를 사용한다.
#Wrapping API views : DRF에서는 Api view을 쓰는데 2가지 wrapper을 제공한다.
#1.CBV에서 사용할 수 있는 APIView 클래스
#2.FBV에서 사용할 수 있는 @api_rest 데코레이터
#이 둘은 Request에 기능을 더하거나, context을 추가해 컨텐츠가 잘 변환되도록한다.

#snippets / views.py
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from snippets.models import Snippet
from snippets.serializers import SnippetSerializer

@api_view(['GET', 'POST'])
def snippet_list(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        snippets = Snippet.objects.all()
        serializer = SnippetSerializer(snippets, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = SnippetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#개별 데이터를 담당하는 view을 수정해보면

@api_view(['GET', 'PUT', 'DELETE'])
def snippet_detail(request, pk):
    """
    Retrieve, update or delete a code snippet.
    """
    try:
        snippet = Snippet.objects.get(pk=pk)
    except Snippet.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = SnippetSerializer(snippet)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = SnippetSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

#request.data는 json 을 포함하여 다양한 형식을 다를 수 있다. 응답 객체 또한 원하는 형태로 렌더링이 가능

#Adding optional format suffixes to our URLS
#여러 형태를 제공할 수 있는 Response 객체의 장점을 이용하기 위해, API에서 여러형태를제공해야한다.

localhost:8000/api/items/4.json
#우선 형태를 다루기 위해 format 키워드를 views.py에 넣어주자.
def snippet_list(reuqest, format = None): #format은 정해진게 없기때문에 디폴트 값은 None
def snippet_detail(request, pk, format=None): #detail은 pk가 필요하다잉

#urls.py에 format_suffix_patterns라는 패턴을 추가로 등록
#snippets/urls.py

from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from snippets import views

urlpatterns = [
    url(r'^snippets/$', views.snippet_list),
    url(r'^snippets/(?P<pk>[0-9]+)$', views.snippet_detail),
]

urlpatterns = format_suffix_patterns(urlpatterns)