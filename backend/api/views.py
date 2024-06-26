from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.dateparse import parse_date
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import JournalEntry, ActivityType, MetricType, Activity, Metric, Category
from .serializers import JournalEntrySerializer, ActivityTypeSerializer, MetricTypeSerializer, ActivitySerializer, \
    MetricSerializer, UserSerializer, CategorySerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]  # Adjust based on your security requirements

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class JournalEntryViewSet(viewsets.ModelViewSet):
    serializer_class = JournalEntrySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return JournalEntry.objects.filter(author=self.request.user)

    @action(detail=True, methods=['post'], url_path='add_activity')
    def add_activity(self, request, pk=None):
        """Add an activity to the journal entry."""
        journal_entry = self.get_object()  # Get the journal entry instance
        activity_type_id = request.data.get('activityTypeId')  # ID of the ActivityType to be added

        try:
            activity_type = ActivityType.objects.get(pk=activity_type_id, author=request.user)
            activity = Activity.objects.create(
                journal_entry=journal_entry,
                activity_type=activity_type
            )
            return Response(ActivitySerializer(activity).data, status=status.HTTP_201_CREATED)
        except ActivityType.DoesNotExist:
            return Response({"error": "Invalid activity type ID or not authorized"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='by-date')
    def get_by_date(self, request):
        date = request.query_params.get('date', None)
        if date:
            date_obj = parse_date(date)
            if date_obj:
                entries = self.get_queryset().filter(date=date_obj)
                serializer = self.get_serializer(entries, many=True)
                return Response(serializer.data)
            return Response({"error": "Invalid date format"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "Date parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        # Check if the journal entry already exists for the given date and user
        if JournalEntry.objects.filter(date=serializer.validated_data['date'], author=self.request.user).exists():
            raise ValidationError('You already have a journal entry for this date.')

        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        # Get the instance being updated
        instance = self.get_object()

        # Check if the updated journal entry would violate the unique constraint
        if JournalEntry.objects.filter(date=serializer.validated_data['date'], author=self.request.user).exclude(
                pk=instance.pk).exists():
            raise ValidationError('You already have a journal entry for this date.')

        serializer.save()

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter categories by the currently logged-in user
        return Category.objects.filter(author=self.request.user)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class ActivityTypeViewSet(viewsets.ModelViewSet):
    serializer_class = ActivityTypeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Access all activity types if needed for user to create Activities
        return ActivityType.objects.filter(author=self.request.user)

    def perform_create(self, serializer):
        # Automatically set the author to the currently authenticated user when creating a new journal entry
        serializer.save(author=self.request.user)


class MetricTypeViewSet(viewsets.ModelViewSet):
    serializer_class = MetricTypeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Access all metric types linked to activity types created by the current user
        return MetricType.objects.filter(activity_type__author=self.request.user)


class ActivityViewSet(viewsets.ModelViewSet):
    serializer_class = ActivitySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only return activities that belong to the current user's journal entries
        return Activity.objects.filter(journal_entry__author=self.request.user)

    @action(detail=False, methods=['get'], url_path='by-type')
    def get_activities_by_type(self, request):
        activity_type_id = request.query_params.get('activity_type_id')
        if not activity_type_id:
            return Response({'error': 'Activity type ID parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

        activities = self.get_queryset().filter(activity_type_id=activity_type_id)
        serializer = self.get_serializer(activities, many=True)
        return Response(serializer.data)


    @action(detail=False, methods=['post'], url_path='add_to_journal')
    def add_activity_to_journal(self, request):
        """Create an activity and add it to a specified journal entry."""
        journal_entry_id = request.data.get('journal_entry_id')
        activity_type_id = request.data.get('activity_type_id')

        try:
            journal_entry = JournalEntry.objects.get(id=journal_entry_id, author=request.user)
            activity_type = ActivityType.objects.get(id=activity_type_id, author=request.user)

            activity = Activity.objects.create(
                journal_entry=journal_entry,
                activity_type=activity_type
            )
            return Response(ActivitySerializer(activity).data, status=status.HTTP_201_CREATED)
        except JournalEntry.DoesNotExist:
            return Response({"error": "Journal entry not found"}, status=status.HTTP_404_NOT_FOUND)
        except ActivityType.DoesNotExist:
            return Response({"error": "Activity type not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='metrics')
    def get_metrics(self, request, pk=None):
        """
        This custom action fetches all metrics associated with a specific activity.
        """
        activity = self.get_object()  # DRF helper to get the activity instance
        metrics = Metric.objects.filter(activity=activity)  # Get all metrics related to the activity

        # Serialize the data
        serializer = MetricSerializer(metrics, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MetricViewSet(viewsets.ModelViewSet):
    serializer_class = MetricSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only return metrics that belong to activities associated with the current user's journal entries
        return Metric.objects.filter(activity__journal_entry__author=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)  # Log or print the errors
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

