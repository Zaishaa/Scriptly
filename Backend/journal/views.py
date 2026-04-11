from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import JournalEntry
from .serializers import JournalEntrySerializer, JournalEntryCreateSerializer


class JournalEntryListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        entries = JournalEntry.objects.filter(user=request.user)
        serializer = JournalEntrySerializer(entries, many=True)
        return Response({
            'count': entries.count(),
            'entries': serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = JournalEntryCreateSerializer(data=request.data)
        if serializer.is_valid():
            entry = serializer.save(user=request.user)
            return Response({
                'message': 'Journal entry created successfully!',
                'entry': JournalEntrySerializer(entry).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class JournalEntryDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            return JournalEntry.objects.get(pk=pk, user=user)
        except JournalEntry.DoesNotExist:
            return None

    def get(self, request, pk):
        entry = self.get_object(pk, request.user)
        if not entry:
            return Response(
                {'error': 'Entry not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = JournalEntrySerializer(entry)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        entry = self.get_object(pk, request.user)
        if not entry:
            return Response(
                {'error': 'Entry not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = JournalEntryCreateSerializer(
            entry,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            entry = serializer.save()
            return Response({
                'message': 'Entry updated successfully!',
                'entry': JournalEntrySerializer(entry).data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        entry = self.get_object(pk, request.user)
        if not entry:
            return Response(
                {'error': 'Entry not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        entry.delete()
        return Response(
            {'message': 'Entry deleted successfully!'},
            status=status.HTTP_204_NO_CONTENT
        )