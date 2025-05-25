from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from consultation.models import Consultation, MaladieContagieuse, MaladieCronique
from rendez_vous.models import RendezVous
from datetime import datetime
from django.utils import timezone
from .serializers import ChronicDiseaseStatsSerializer, ContagiousDiseaseBarSerializer, ContagiousDiseasePieSerializer

class DashboardStatsView(APIView):
    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        consultations = Consultation.objects.all()

        if start_date and end_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
                consultations = consultations.filter(
                    rendezvous__Datetime__range=[start_date, end_date]
                )
            except ValueError:
                return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        total_consultations = consultations.count()
        chronic_diseases = MaladieCronique.objects.filter(consultation__in=consultations).count()
        contagious_diseases = MaladieContagieuse.objects.filter(consultation__in=consultations).count()
        percent_chronic = round((chronic_diseases / total_consultations * 100), 1) if total_consultations > 0 else 0
        percent_contagious = round((contagious_diseases / total_consultations * 100), 1) if total_consultations > 0 else 0

        monthly_stats = (
            consultations.annotate(month=TruncMonth('rendezvous__Datetime'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )
        monthly_data = [
            {"month": item['month'].strftime('%b'), "count": item['count']}
            for item in monthly_stats
        ]

        gender_stats = (
            consultations.values('rendezvous__patient__gender')
            .annotate(count=Count('id'))
        )
        gender_data = [
            {"name": item['rendezvous__patient__gender'], "value": item['count']}
            for item in gender_stats if item['rendezvous__patient__gender']
        ]

        data = {
            "total_consultations": total_consultations,
            "chronic_diseases": chronic_diseases,
            "percent_chronic": percent_chronic,
            "contagious_diseases": contagious_diseases,
            "percent_contagious": percent_contagious,
            "consultations_by_month": monthly_data,
            "gender_stats": gender_data,
        }

        return Response(data, status=status.HTTP_200_OK)

class ChronicDiseasesStatsView(APIView):
    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        consultations = Consultation.objects.all()

        if start_date and end_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
                consultations = consultations.filter(
                    rendezvous__Datetime__range=[start_date, end_date]
                )
            except ValueError:
                return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        repertoires = ['Asthme', 'Allergie', 'Tuberculose', 'Inflammation des poumons']
        mentales = ['Dépression', 'TOC / Bipolaire', 'Autre']
        cardiaques = ['Hypertension', 'Rhumatisme', 'Rhum. aigu', 'Trouble rythme']
        digestives = ['Hépatite', 'Crohn', 'Cœliaque', 'Ulcère']

        def get_stats(disease_names):
            stats = (
                MaladieCronique.objects.filter(
                    consultation__in=consultations,
                    nom__in=disease_names
                )
                .values('nom')
                .annotate(
                    Homme=Count('id', filter=Q(consultation__rendezvous__patient__gender='Male')),
                    Femme=Count('id', filter=Q(consultation__rendezvous__patient__gender='Female'))
                )
                .order_by('nom')
            )
            return [
                {"name": item['nom'], "Homme": item['Homme'], "Femme": item['Femme']}
                for item in stats
            ]

        data = {
            "maladies_repertoires": get_stats(repertoires),
            "maladies_mentales": get_stats(mentales),
            "maladies_cardiaques": get_stats(cardiaques),
            "maladies_digestives": get_stats(digestives),
        }

        return Response(data, status=status.HTTP_200_OK)

class ContagiousDiseasesStatsView(APIView):
    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        consultations = Consultation.objects.all()

        if start_date and end_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
                consultations = consultations.filter(
                    rendezvous__Datetime__range=[start_date, end_date]
                )
            except ValueError:
                return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        # Bar chart data (by gender)
        bar_stats = (
            MaladieContagieuse.objects.filter(consultation__in=consultations)
            .values('nom')
            .annotate(
                Homme=Count('id', filter=Q(consultation__rendezvous__patient__gender='Male')),
                Femme=Count('id', filter=Q(consultation__rendezvous__patient__gender='Female'))
            )
            .order_by('nom')
        )
        bar_data = [
            {"name": item['nom'], "Homme": item['Homme'], "Femme": item['Femme']}
            for item in bar_stats
        ]

        # Pie chart data (total count)
        pie_stats = (
            MaladieContagieuse.objects.filter(consultation__in=consultations)
            .values('nom')
            .annotate(value=Count('id'))
            .order_by('nom')
        )
        pie_data = [
            {"name": item['nom'], "value": item['value']}
            for item in pie_stats
        ]

        data = {
            "bar_data": bar_data,
            "pie_data": pie_data,
        }

        return Response(data, status=status.HTTP_200_OK)