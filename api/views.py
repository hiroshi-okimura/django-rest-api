from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
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
