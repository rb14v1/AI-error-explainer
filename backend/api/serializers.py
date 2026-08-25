from rest_framework import serializers


class ExplainErrorSerializer(serializers.Serializer):
    error_message = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=50000,
        help_text="The exact error message or exception string"
    )
    stack_trace = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=50000,
        help_text="Optional stack trace string"
    )
    code_snippet = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=50000,
        help_text="Optional surrounding code snippet"
    )
    language = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=100,
        help_text="Optional programming language identifier"
    )

    def validate_error_message(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("error_message cannot be empty.")
        return value.strip()

    def validate(self, data):
        total_size = sum(
            len(str(v)) for v in data.values()
        )
        if total_size > 50000:
            raise serializers.ValidationError(
                "Total payload size exceeds 50KB limit."
            )
        return data
