from rest_framework import serializers
from .models import JournalEntry


class JournalEntrySerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = JournalEntry
        fields = (
            'id', 'user', 'title', 'content',
            'mood', 'is_analyzed', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'user', 'is_analyzed', 'created_at', 'updated_at')


class JournalEntryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalEntry
        fields = ('title', 'content', 'mood')

    def validate_content(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError(
                "Journal entry must be at least 10 characters long."
            )
        return value

    def validate_title(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError(
                "Title must be at least 3 characters long."
            )
        return value