from rest_framework import status
from rest_framework import viewsets
from rest_framework.pagination import LimitOffsetPagination, Response


from .models import Task
from .serializers import TaskSerializer

from concurrent.futures import ThreadPoolExecutor


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    pagination_class = LimitOffsetPagination

    def create(self, request, *args, **kwargs):
        # TODO: Require Content-Type json

        def update_serializer(request):
            serializer = self.get_serializer(data=request)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return serializer.data

        if isinstance(request.data, list):
            futures = []
            with ThreadPoolExecutor(max_workers=2) as e:
                for single_request in request.data:
                    # TODO: Error handling drops out of loop.
                    # Example: If 2 tasks asked to be created but 1 already exists.
                    # A single object will be returned instead of an array with 1 pass / 1 fail.
                    future = e.submit(update_serializer, single_request)
                    futures.append(future)
                headers = self.get_success_headers(futures[0].result())
                combined_responses = [response.result() for response in futures]
                return Response(combined_responses, status=status.HTTP_201_CREATED, headers=headers)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
