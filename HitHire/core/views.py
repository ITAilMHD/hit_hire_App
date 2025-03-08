
# core/views.py

from django.contrib.auth import authenticate, login
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, JobDescription, CV, CandidateRanking, CustomScoring
from .serializers import (
    UserSerializer, JobDescriptionSerializer, CVSeralizer,
    CandidateRankingSerializer, CustomScoringSerializer
)
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

User = get_user_model()

class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        # Manually check the password
        if check_password(password, user.password):
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            return Response({
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'message': 'Login successful'
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class SignupView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            # Use create_user to handle password hashing
            user = User.objects.create_user(
                username=serializer.validated_data['username'],
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password'],
                company=serializer.validated_data.get('company', '')
            )
            return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        print("Errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from django.core.mail import send_mail
from django.conf import settings
from .models import User
from .utils import generate_reset_token,validate_reset_token

class ForgotPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        # Check if the email exists in the database
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)

        # Generate a reset token and send it via email
        reset_token = generate_reset_token(user)  # Custom function to generate a token
        reset_url = f"{settings.RESET_PASSWORD_URL}?token={reset_token}"

        send_mail(
            subject='Reset Your Password',
            message=f'Click the link to reset your password: {reset_url}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        return Response({'message': 'Password reset link sent to your email'}, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    def post(self, request, token):
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        if new_password != confirm_password:
            return Response({'error': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate and reset the password using the token
        user = validate_reset_token(token)  # Custom function to validate the token
        if not user:
            return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({'message': 'Password reset successfully'}, status=status.HTTP_200_OK)


from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

'''
class UploadJobDescriptionView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        data = request.data.copy()
        data['uploaded_by'] = 2  # تعيين المستخدم يدويًا
        serializer = JobDescriptionSerializer(data=data)
        #print(serializer)
        if serializer.is_valid():
            serializer.save(uploaded_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

'''

from .utils import extract_job_description  # تأكد أن لديك دالة لاستخراج البيانات

'''
class UploadJobDescriptionView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        file = request.FILES.get('file')  # استقبال الملف
        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        extracted_data = extract_job_description(file)  # استخراج البيانات من الملف

        if not extracted_data:
            return Response({'error': 'Failed to extract data from file'}, status=status.HTTP_400_BAD_REQUEST)

        # إضافة المستخدم كمُحمّل للملف
        extracted_data['uploaded_by'] = 2

        serializer = JobDescriptionSerializer(data=extracted_data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
'''

class UploadJobDescriptionView(APIView):
    parser_classes = (MultiPartParser, FormParser, JSONParser)  # دعم استقبال JSON أيضًا

    def post(self, request):
        file = request.FILES.get('file')
        text = request.data.get('text')

        if not file and not text:
            return Response({'error': 'No file or text provided'}, status=status.HTTP_400_BAD_REQUEST)

        if file:
            extracted_data = extract_job_description(file)  # استخراج البيانات من الملف
        else:
            extracted_data = {"title": "Untitled Job", "description": text}  # استخدام النص

        if not extracted_data:
            return Response({'error': 'Failed to extract data'}, status=status.HTTP_400_BAD_REQUEST)

        extracted_data['uploaded_by'] = 2  # تعيين المستخدم افتراضيًا

        serializer = JobDescriptionSerializer(data=extracted_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from .utils import extract_cv_data
class UploadCVView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        files = request.FILES.getlist('files')
        cvs = []
        for file in files:
            cv_data = extract_cv_data(file)  # Custom function to extract data from CV
            cv_data['uploaded_by'] = 2
            serializer = CVSeralizer(data=cv_data)

            if serializer.is_valid():
                cvs.append(serializer.save())
            else:
                print(serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'CVs uploaded successfully', 'cvs': [cv.id for cv in cvs]}, status=status.HTTP_201_CREATED)


from django.db import transaction
from .models import CandidateRanking


def save_top_candidate(job_description, cvs):
    """
    Rank candidates and save only the top candidate in the database.
    """
    ranked_results = rank_candidates(job_description, cvs)

    if not ranked_results:
        return None  # لا يوجد مرشحين لتخزينهم

    top_candidate = ranked_results[0]  # اختيار أعلى درجة

    with transaction.atomic():  # لضمان حفظ البيانات بشكل آمن
        CandidateRanking.objects.create(
            job_description=job_description,
            cv=CV.objects.get(id=top_candidate['cv_id']),  # احصل على كائن السيرة الذاتية باستخدام ID
            overall_score=top_candidate['overall_score'],
            recommendation=top_candidate['recommendation']
        )

    return top_candidate


from .utils import rank_candidates  # Custom function for AI ranking

class RankCandidatesView(APIView):
    def post(self, request):
        job_description_id = request.data.get('job_description_id')
        cv_ids = request.data.get('cv_ids', [])

        try:
            job_description = JobDescription.objects.get(id=job_description_id)
        except JobDescription.DoesNotExist:
            return Response({'error': 'Job description not found'}, status=status.HTTP_404_NOT_FOUND)

        cvs = CV.objects.filter(id__in=cv_ids)
        ranked_results = rank_candidates(job_description, cvs)  # Perform AI ranking
        print(ranked_results)
        save_top_candidate(job_description, cvs)

        return Response(ranked_results, status=status.HTTP_200_OK)


from .utils import generate_report  # Custom function to generate report


class SearchReportView(APIView):
    def get(self, request):
        query = request.query_params.get('query', '')
        if not query:
            return Response({'error': 'Query parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

        reports = generate_report(query)  # Generate detailed report
        return Response(reports, status=status.HTTP_200_OK)

from django.http import FileResponse
from .utils import export_report
class DownloadReportView(APIView):
    def get(self, request, report_id, format):
        try:
            report = CandidateRanking.objects.filter(job_description_id=report_id)
        except CandidateRanking.DoesNotExist:
            return Response({'error': 'Report not found'}, status=status.HTTP_404_NOT_FOUND)

        file_path = export_report(report, format)  # Export report to specified format
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=f'report.{format}')


class SetCustomScoringView(APIView):
    def post(self, request):
        print('Received Request:', request.data)  # ✅ طباعة البيانات للتحقق من استقبالها

        try:
            education_weight = float(request.data.get('education_weight', 0.3))
            experience_weight = float(request.data.get('experience_weight', 0.3))
            skills_weight = float(request.data.get('skills_weight', 0.4))
        except ValueError:
            return Response({'error': 'Invalid weight values'}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ استخدم get_or_create بدون تحديد ID ثابت
        scoring, created = CustomScoring.objects.get_or_create(id=1, defaults={
            'education_weight': education_weight,
            'experience_weight': experience_weight,
            'skills_weight': skills_weight
        })

        # ✅ تحديث القيم إن لم يكن كائن جديد
        if not created:
            print('not created')
            scoring.education_weight = education_weight
            scoring.experience_weight = experience_weight
            scoring.skills_weight = skills_weight
            scoring.save()

        return Response({'message': 'Custom scoring weights updated'}, status=status.HTTP_200_OK)

from rest_framework.permissions import AllowAny

class GetCustomScoringView(APIView):
    permission_classes = [AllowAny]  # السماح للجميع بالوصول

    def get(self, request):
        # استرجاع القيم من قاعدة البيانات، أو استخدام القيم الافتراضية
        scoring, _ = CustomScoring.objects.get_or_create(id=1, defaults={
            'education_weight': 0.3,
            'experience_weight': 0.3,
            'skills_weight': 0.4
        })

        return Response({
            'education_weight': scoring.education_weight,
            'experience_weight': scoring.experience_weight,
            'skills_weight': scoring.skills_weight
        }, status=status.HTTP_200_OK)

class ResetScoringView(APIView):
    def post(self, request):
        scoring, created = CustomScoring.objects.get_or_create(user=request.user)
        scoring.education_weight = 0.3
        scoring.experience_weight = 0.3
        scoring.skills_weight = 0.4
        scoring.save()

        return Response({'message': 'Scoring weights reset to default'}, status=status.HTTP_200_OK)

class SearchPreviousRankingsView(APIView):
    def get(self, request):
        keyword = request.query_params.get('keyword', '')
        job_title = request.query_params.get('job_title', '')
        candidate_name = request.query_params.get('candidate_name', '')

        results = CandidateRanking.objects.filter(
            job_description__title__icontains=job_title,
            cv__name__icontains=candidate_name,
            job_description__description__icontains=keyword
        )

        serializer = CandidateRankingSerializer(results, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class PricingPlansView(APIView):
    def get(self, request):
        plans = [
            {'name': 'Free Plan', 'price': 0, 'features': ['Basic AI ranking']},
            {'name': 'Basic Plan', 'price': 49, 'features': ['Advanced AI ranking']},
            {'name': 'Pro Plan', 'price': 99, 'features': ['Custom scoring, unlimited uploads']}
        ]
        return Response({'plans': plans}, status=status.HTTP_200_OK)

class SubscribeToPlanView(APIView):
    def post(self, request):
        plan_id = request.data.get('plan_id')
        payment_token = request.data.get('payment_token')

        # Process subscription logic here
        return Response({'message': 'Subscription successful'}, status=status.HTTP_200_OK)

class ContactUsView(APIView):
    def post(self, request):
        name = request.data.get('name')
        email = request.data.get('email')
        subject = request.data.get('subject')
        message = request.data.get('message')

        send_mail(
            subject=subject,
            message=f"From: {name} ({email})\n\n{message}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.CONTACT_EMAIL],
            fail_silently=False,
        )
        return Response({'message': 'Message sent successfully'}, status=status.HTTP_200_OK)

# core/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CandidateRanking, JobDescription
from .serializers import CandidateRankingSerializer

class GetRankedResultsView(APIView):
    """
    Retrieve ranked candidate results for a specific job description.
    """

    def get(self, request, job_id, format=None):
        # Step 1: Validate that the job description exists
        try:
            job_description = JobDescription.objects.get(id=job_id)
        except JobDescription.DoesNotExist:
            return Response(
                {"error": "Job description not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Step 2: Fetch the ranked candidates for the given job description
        rankings = CandidateRanking.objects.filter(job_description=job_description).order_by('-overall_score')

        if not rankings.exists():
            return Response(
                {"message": "No ranked candidates found for this job description."},
                status=status.HTTP_200_OK
            )

        # Step 3: Serialize the ranking data
        serializer = CandidateRankingSerializer(rankings, many=True)

        # Step 4: Return the serialized data as the response
        return Response(serializer.data, status=status.HTTP_200_OK)


#################################################################################
# core/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class ForgotPasswordView1(APIView):
    def post(self, request):
        email = request.data.get('email')

        # Simulate sending a password reset email
        if email:
            return Response({'message': 'Password reset instructions sent to your email.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)


# core/views.py

from rest_framework.parsers import MultiPartParser, FormParser

class UploadJobDescriptionView1(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        file = request.FILES.get('file')
        text = request.data.get('text')

        # Simulate job description upload
        if file or text:
            return Response({'message': 'Job description uploaded successfully.'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'File or text is required.'}, status=status.HTTP_400_BAD_REQUEST)


# core/views.py

class UploadCVView1(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        files = request.FILES.getlist('files')

        # Simulate CV upload
        if files:
            return Response({'message': f'{len(files)} CV(s) uploaded successfully.'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'No files were uploaded.'}, status=status.HTTP_400_BAD_REQUEST)

# core/views.py

class RankCandidatesView1(APIView):
    def post(self, request):
        job_description_id = request.data.get('job_description_id')
        cv_ids = request.data.get('cv_ids', [])

        # Simulate AI ranking process
        if job_description_id and cv_ids:
            ranked_results = [
                {'name': 'John Doe', 'email': 'john.doe@example.com', 'score': 0.9},
                {'name': 'Jane Smith', 'email': 'jane.smith@example.com', 'score': 0.8},
            ]
            return Response(ranked_results, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid input.'}, status=status.HTTP_400_BAD_REQUEST)

# core/views.py

class GetRankedResultsView1(APIView):
    def get(self, request, job_id):
        # Simulate fetching ranked results
        ranked_results = [
            {'name': 'John Doe', 'email': 'john.doe@example.com', 'score': 0.9},
            {'name': 'Jane Smith', 'email': 'jane.smith@example.com', 'score': 0.8},
        ]
        return Response(ranked_results, status=status.HTTP_200_OK)

# core/views.py

class GenerateReportView1(APIView):
    def get(self, request, job_id):
        # Simulate generating a report
        report = {
            'job_title': 'Software Engineer',
            'date_created': '2023-10-01',
            'candidates': [
                {'name': 'John Doe', 'score': 0.9},
                {'name': 'Jane Smith', 'score': 0.8},
            ],
        }
        return Response(report, status=status.HTTP_200_OK)


# core/views.py

from django.http import HttpResponse

class DownloadReportView1(APIView):
    def get(self, request, report_id, format):
        # Simulate downloading a report
        content = "This is the report content."
        response = HttpResponse(content, content_type=f'application/{format}')
        response['Content-Disposition'] = f'attachment; filename="report.{format}"'
        return response

# core/views.py

class SetCustomScoringView1(APIView):
    def post(self, request, user_id):
        education_weight = request.data.get('education_weight', 0.3)
        experience_weight = request.data.get('experience_weight', 0.3)
        skills_weight = request.data.get('skills_weight', 0.4)

        # Simulate saving custom scoring weights
        return Response({'message': 'Custom scoring weights updated.'}, status=status.HTTP_200_OK)


# core/views.py

class SearchPreviousRankingsView1(APIView):
    def get(self, request):
        keyword = request.query_params.get('keyword', '')
        job_title = request.query_params.get('job_title', '')

        # Simulate searching previous rankings
        results = [
            {'job_title': 'Software Engineer', 'date_created': '2023-10-01', 'top_candidate': 'John Doe'},
        ]
        return Response(results, status=status.HTTP_200_OK)

# core/views.py

class PricingPlansView1(APIView):
    def get(self, request):
        plans = [
            {'name': 'Free Plan', 'price': 0, 'features': ['Basic AI ranking']},
            {'name': 'Basic Plan', 'price': 49, 'features': ['Advanced AI ranking']},
            {'name': 'Pro Plan', 'price': 99, 'features': ['Custom scoring, unlimited uploads']},
        ]
        return Response({'plans': plans}, status=status.HTTP_200_OK)


# core/views.py

class SubscribeToPlanView1(APIView):
    def post(self, request):
        plan_id = request.data.get('plan_id')
        payment_token = request.data.get('payment_token')

        # Simulate subscription process
        if plan_id and payment_token:
            return Response({'message': 'Subscription successful.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid input.'}, status=status.HTTP_400_BAD_REQUEST)


# core/views.py

class ContactUsView1(APIView):
    def post(self, request):
        name = request.data.get('name')
        email = request.data.get('email')
        subject = request.data.get('subject')
        message = request.data.get('message')

        # Simulate sending a contact form
        if name and email and subject and message:
            return Response({'message': 'Message sent successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'All fields are required.'}, status=status.HTTP_400_BAD_REQUEST)


import csv
import pandas as pd
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.template.loader import get_template
import random

def generate_random_metrics():
    skills_high = random.randint(40, 90)
    skills_medium = random.randint(10, 50)
    skills_low = 100 - (skills_high + skills_medium)

    degree_match = random.randint(60, 95)
    experience_match = random.randint(50, 90)

    rejection_reasons = {
        "Lack of experience": random.randint(5, 20),
        "Missing skills": random.randint(5, 20),
        "Low degree qualification": random.randint(5, 20),
        "Poor interview performance": random.randint(5, 20),
        "Salary expectations too high": random.randint(5, 20)
    }

    return {
        "skills_high": skills_high,
        "skills_medium": skills_medium,
        "skills_low": skills_low,
        "degree_match": degree_match,
        "experience_match": experience_match,
        "rejection_reasons": rejection_reasons
    }
# Export CSV
def export_csv(request):
    metrics = generate_random_metrics()

    data = {
        "Skills High": metrics["skills_high"],
        "Skills Medium": metrics["skills_medium"],
        "Skills Low": metrics["skills_low"],
        "Degree Match": metrics["degree_match"],
        "Experience Match": metrics["experience_match"],
    }
    data.update(metrics["rejection_reasons"])

    df = pd.DataFrame([data])
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="kpi_data.csv"'
    df.to_csv(response, index=False)
    return response


# Export Excel
def export_excel(request):
    metrics = generate_random_metrics()

    # Flatten rejection reasons for DataFrame
    data = {
        "Skills High": [metrics["skills_high"]],
        "Skills Medium": [metrics["skills_medium"]],
        "Skills Low": [metrics["skills_low"]],
        "Degree Match": [metrics["degree_match"]],
        "Experience Match": [metrics["experience_match"]],
    }
    data.update(metrics["rejection_reasons"])

    df = pd.DataFrame(data)
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="kpi_report.xlsx"'
    df.to_excel(response, index=False)
    return response


# Export PDF
def export_pdf(request):
    metrics = generate_random_metrics()
    template_path = 'reports/report_template.html'
    context = {'metrics': metrics}

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="kpi_report.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('PDF generation failed')
    return response
