from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Todo


class TodoModelTest(TestCase):
    """Todoモデルのテスト"""

    def setUp(self):
        """テストデータの準備"""
        self.todo = Todo.objects.create(
            title="テストTodo",
            description="これはテスト用のTodoです",
            completed=False,
        )

    def test_todo_creation(self):
        """Todoが正しく作成されることを確認"""
        self.assertEqual(self.todo.title, "テストTodo")
        self.assertEqual(self.todo.description, "これはテスト用のTodoです")
        self.assertFalse(self.todo.completed)
        self.assertIsNotNone(self.todo.created_at)
        self.assertIsNotNone(self.todo.updated_at)

    def test_todo_str_method(self):
        """__str__メソッドが正しく動作することを確認"""
        self.assertEqual(str(self.todo), "テストTodo")

    def test_todo_default_completed(self):
        """completedのデフォルト値がFalseであることを確認"""
        todo = Todo.objects.create(title="デフォルトテスト")
        self.assertFalse(todo.completed)

    def test_todo_ordering(self):
        """作成日時の降順で並ぶことを確認"""
        todo1 = Todo.objects.create(title="最初のTodo")
        todo2 = Todo.objects.create(title="2番目のTodo")
        todo3 = Todo.objects.create(title="3番目のTodo")

        todos = list(Todo.objects.all())
        # 最新のものが最初に来る
        self.assertEqual(todos[0].title, "3番目のTodo")
        self.assertEqual(todos[1].title, "2番目のTodo")
        self.assertEqual(todos[2].title, "最初のTodo")


class TodoSerializerTest(TestCase):
    """Todoシリアライザーのテスト"""

    def test_serialize_todo(self):
        """TodoをJSONにシリアライズできることを確認"""
        from .serializers import TodoSerializer

        todo = Todo.objects.create(
            title="シリアライズテスト",
            description="説明",
            completed=True,
        )
        serializer = TodoSerializer(todo)
        data = serializer.data

        self.assertEqual(data["title"], "シリアライズテスト")
        self.assertEqual(data["description"], "説明")
        self.assertTrue(data["completed"])
        self.assertIn("id", data)
        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)

    def test_deserialize_todo(self):
        """JSONからTodoを作成できることを確認"""
        from .serializers import TodoSerializer

        data = {
            "title": "デシリアライズテスト",
            "description": "説明文",
            "completed": False,
        }
        serializer = TodoSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        todo = serializer.save()
        self.assertEqual(todo.title, "デシリアライズテスト")
        self.assertEqual(todo.description, "説明文")
        self.assertFalse(todo.completed)

    def test_read_only_fields(self):
        """read_only_fieldsが正しく動作することを確認"""
        from .serializers import TodoSerializer

        todo = Todo.objects.create(title="テスト")
        data = {
            "id": 999,  # read_onlyなので無視される
            "title": "更新されたタイトル",
            "created_at": "2020-01-01T00:00:00Z",  # read_onlyなので無視される
        }
        serializer = TodoSerializer(todo, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        serializer.save()

        todo.refresh_from_db()
        self.assertNotEqual(todo.id, 999)  # IDは変更されない
        self.assertEqual(todo.title, "更新されたタイトル")


class TodoAPITest(APITestCase):
    """Todo APIエンドポイントのテスト"""

    def setUp(self):
        """テストデータの準備"""
        self.todo1 = Todo.objects.create(
            title="最初のTodo",
            description="説明1",
            completed=False,
        )
        self.todo2 = Todo.objects.create(
            title="2番目のTodo",
            description="説明2",
            completed=True,
        )

    def test_list_todos(self):
        """GET /api/todos/ - Todo一覧を取得できることを確認"""
        url = "/api/todos/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        # 作成日時の降順で並んでいることを確認
        self.assertEqual(response.data[0]["title"], "2番目のTodo")
        self.assertEqual(response.data[1]["title"], "最初のTodo")

    def test_list_todos_empty(self):
        """GET /api/todos/ - 空のリストを返すことを確認"""
        Todo.objects.all().delete()
        url = "/api/todos/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_create_todo(self):
        """POST /api/todos/ - Todoを作成できることを確認"""
        url = "/api/todos/"
        data = {
            "title": "新規Todo",
            "description": "新規作成のテスト",
            "completed": False,
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "新規Todo")
        self.assertEqual(response.data["description"], "新規作成のテスト")
        self.assertFalse(response.data["completed"])
        self.assertIn("id", response.data)
        self.assertIn("created_at", response.data)

        # データベースに保存されていることを確認
        self.assertEqual(Todo.objects.count(), 3)
        todo = Todo.objects.get(title="新規Todo")
        self.assertIsNotNone(todo)

    def test_create_todo_minimal(self):
        """POST /api/todos/ - 最小限のデータでTodoを作成できることを確認"""
        url = "/api/todos/"
        data = {"title": "最小限のTodo"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "最小限のTodo")
        self.assertEqual(response.data["description"], "")  # 空文字列
        self.assertFalse(response.data["completed"])  # デフォルト値

    def test_create_todo_validation_error(self):
        """POST /api/todos/ - titleが空の場合、バリデーションエラーになることを確認"""
        url = "/api/todos/"
        data = {"title": ""}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)

    def test_retrieve_todo(self):
        """GET /api/todos/{id}/ - Todoの詳細を取得できることを確認"""
        url = f"/api/todos/{self.todo1.id}/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "最初のTodo")
        self.assertEqual(response.data["description"], "説明1")
        self.assertFalse(response.data["completed"])
        self.assertEqual(response.data["id"], self.todo1.id)

    def test_retrieve_todo_not_found(self):
        """GET /api/todos/{id}/ - 存在しないIDで404エラーになることを確認"""
        url = "/api/todos/999/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_todo_put(self):
        """PUT /api/todos/{id}/ - Todoを完全更新できることを確認"""
        url = f"/api/todos/{self.todo1.id}/"
        data = {
            "title": "更新されたタイトル",
            "description": "更新された説明",
            "completed": True,
        }
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "更新されたタイトル")
        self.assertEqual(response.data["description"], "更新された説明")
        self.assertTrue(response.data["completed"])

        # データベースが更新されていることを確認
        self.todo1.refresh_from_db()
        self.assertEqual(self.todo1.title, "更新されたタイトル")
        self.assertTrue(self.todo1.completed)

    def test_update_todo_patch(self):
        """PATCH /api/todos/{id}/ - Todoを部分更新できることを確認"""
        url = f"/api/todos/{self.todo1.id}/"
        data = {"completed": True}  # completedのみ更新
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["completed"])
        # 他のフィールドは変更されていない
        self.assertEqual(response.data["title"], "最初のTodo")

        # データベースが更新されていることを確認
        self.todo1.refresh_from_db()
        self.assertTrue(self.todo1.completed)
        self.assertEqual(self.todo1.title, "最初のTodo")

    def test_update_todo_patch_title(self):
        """PATCH /api/todos/{id}/ - titleのみを更新できることを確認"""
        url = f"/api/todos/{self.todo1.id}/"
        data = {"title": "タイトルだけ更新"}
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "タイトルだけ更新")

    def test_update_todo_not_found(self):
        """PUT /api/todos/{id}/ - 存在しないIDで404エラーになることを確認"""
        url = "/api/todos/999/"
        data = {"title": "更新", "description": "", "completed": False}
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_todo(self):
        """DELETE /api/todos/{id}/ - Todoを削除できることを確認"""
        url = f"/api/todos/{self.todo1.id}/"
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # データベースから削除されていることを確認
        self.assertEqual(Todo.objects.count(), 1)
        self.assertFalse(Todo.objects.filter(id=self.todo1.id).exists())

    def test_delete_todo_not_found(self):
        """DELETE /api/todos/{id}/ - 存在しないIDで404エラーになることを確認"""
        url = "/api/todos/999/"
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
