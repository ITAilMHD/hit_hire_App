# core/serializers.py

from .models import User, JobDescription, CV, CandidateRanking, CustomScoring
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'company', 'password', 'confirm_password']

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        # Remove confirm_password from validated_data
        validated_data.pop('confirm_password', None)
        return User.objects.create_user(**validated_data)

class JobDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobDescription
        fields = '__all__'

class CVSeralizer(serializers.ModelSerializer):
    class Meta:
        model = CV
        fields = '__all__'

class CandidateRankingSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateRanking
        fields = '__all__'

class CustomScoringSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomScoring
        fields = '__all__'