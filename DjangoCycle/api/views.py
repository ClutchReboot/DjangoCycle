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

        def update_serializer(request) -> dict:
            serializer = self.get_serializer(data=request)
            if serializer.is_valid():
                self.perform_create(serializer)
                return serializer.data
            return {**serializer.data, 'error': serializer.errors}

        if isinstance(request.data, list):
            if len(request.data) > 10:
                error = {'error': 'The length of the payload is too large.'}
                return Response(error, status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)

            futures = []
            with ThreadPoolExecutor(max_workers=2) as e:
                for single_request in request.data:
                    futures.append(e.submit(update_serializer, single_request))
            headers = self.get_success_headers(futures[0].result())
            combined_responses = [response.result() for response in futures]
            return Response(combined_responses, status=status.HTTP_201_CREATED, headers=headers)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
