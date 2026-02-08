from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET"])
def test_view(request):
    """
    動作確認用の簡単なAPIエンドポイント
    """
    return Response({"message": "API is working!"})
