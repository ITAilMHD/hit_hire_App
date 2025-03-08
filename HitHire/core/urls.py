# core/urls.py

from django.urls import path
from .views import (
    # Authentication
    LoginView, SignupView, ForgotPasswordView, ResetPasswordView,

    # Matching Page
    UploadJobDescriptionView, UploadCVView, RankCandidatesView, GetRankedResultsView, SetCustomScoringView,

    # Reports
    SearchReportView, DownloadReportView,

    # Search
    SearchPreviousRankingsView,

    # Pricing
    PricingPlansView, SubscribeToPlanView,

    # Contact
    ContactUsView,
    export_csv,
    export_excel,
    export_pdf,
    GetCustomScoringView,
)

urlpatterns = [
    # Authentication
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/signup/', SignupView.as_view(), name='signup'),
    path('auth/forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('auth/reset-password/<str:token>/', ResetPasswordView.as_view(), name='reset_password'),

    # Matching Page
    path('matching/upload-job-description/', UploadJobDescriptionView.as_view(), name='upload_job_description'),
    path('matching/upload-cvs/', UploadCVView.as_view(), name='upload_cvs'),
    path('matching/rank-candidates/', RankCandidatesView.as_view(), name='rank_candidates'),
    path('matching/get-ranked-results/<int:job_id>/', GetRankedResultsView.as_view(), name='get_ranked_results'),
    path('matching/set-custom-scoring/', SetCustomScoringView.as_view(), name='set_custom_scoring'),
    path('matching/GetCustomScoringView/', GetCustomScoringView.as_view(), name='GetCustomScoringView'),

    # Reports
    path('reports/SearchReportView/', SearchReportView.as_view(), name='generate_report'),
    path('reports/download-report/<int:report_id>/<str:format>/', DownloadReportView.as_view(), name='download_report'),

    # Search
    path('search/', SearchPreviousRankingsView.as_view(), name='search_rankings'),

    # Pricing
    path('pricing/plans/', PricingPlansView.as_view(), name='pricing_plans'),
    path('pricing/subscribe/', SubscribeToPlanView.as_view(), name='subscribe_to_plan'),

    # Contact
    path('contact/submit/', ContactUsView.as_view(), name='contact_us'),
    path('export/csv/', export_csv, name='export_csv'),
    path('export/excel/', export_excel, name='export_excel'),
    path('export/pdf/', export_pdf, name='export_pdf'),
]
'''
# core/urls.py

from django.urls import path
from .views import LoginView,SignupView,ContactUsView1,SubscribeToPlanView1,PricingPlansView1,SearchPreviousRankingsView1,SetCustomScoringView1,DownloadReportView1,GenerateReportView1,ForgotPasswordView1,UploadJobDescriptionView1,UploadCVView1,RankCandidatesView1,GetRankedResultsView1

urlpatterns = [
    path('auth/forgot-password/', ForgotPasswordView1.as_view(), name='forgot_password'),
    path('pricing/plans/', PricingPlansView1.as_view(), name='pricing_plans'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/signup/', SignupView.as_view(), name='signup'),
    path('contact/submit/', ContactUsView1.as_view(), name='contact_us'),
    path('pricing/subscribe/', SubscribeToPlanView1.as_view(), name='subscribe_to_plan'),
    path('matching/upload-job-description/', UploadJobDescriptionView1.as_view(), name='upload_job_description'),
    path('matching/upload-cvs/', UploadCVView1.as_view(), name='upload_cvs'),
    path('search/', SearchPreviousRankingsView1.as_view(), name='search_rankings'),
    path('matching/rank-candidates/', RankCandidatesView1.as_view(), name='rank_candidates'),
    path('matching/get-ranked-results/<int:job_id>/', GetRankedResultsView1.as_view(), name='get_ranked_results'),
    path('reports/generate-report/<int:job_id>/', GenerateReportView1.as_view(), name='generate_report'),
    path('matching/set-custom-scoring/<int:user_id>/', SetCustomScoringView1.as_view(), name='set_custom_scoring'),
    path('reports/download-report/<int:report_id>/<str:format>/', DownloadReportView1.as_view(), name='download_report'),
]
'''