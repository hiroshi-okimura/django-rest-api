from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.views import obtain_auth_token
from .models import Todo
from .serializers import TodoSerializer


class TodoViewSet(viewsets.ModelViewSet):
    """
    TodoのCRUD操作を提供するViewSet
    """

    queryset = Todo.objects.all()
    serializer_class = TodoSerializer


@api_view(["GET"])
def test_view(request):
    """
    動作確認用の簡単なAPIエンドポイント
    """
    return Response({"message": "API is working!"})


@api_view(["POST"])
@permission_classes([AllowAny])
def auth_token(request):
    """
    認証トークン取得用エンドポイント。
    POST で username と password を送るとトークンを返す。
    認証不要でアクセス可能。
    """
    # obtain_auth_token は Django の HttpRequest を期待するため、元の request を渡す
    return obtain_auth_token(request._request)
