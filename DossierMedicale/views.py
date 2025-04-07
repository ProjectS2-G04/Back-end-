import os
from io import BytesIO

from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework import generics
from accounts.models import User
from .models import *
from .serializers import *

class ActivateUserView(APIView):
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if user.is_active:
            return Response({"message": "This user is already active."}, status=status.HTTP_400_BAD_REQUEST)
        user.is_active = True
        user.save()
        return Response({"message": "User activated successfully."}, status=status.HTTP_200_OK)

class DesactivateUserView(APIView):
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if not user.is_active:
            return Response({"message": "This user is already inactive."}, status=status.HTTP_400_BAD_REQUEST)
        user.is_active = False
        user.save()
        return Response({"message": "User deactivated successfully."}, status=status.HTTP_200_OK)

class ArchiveDossierMedicalView(APIView):
    def post(self, request, pk):
        dossier = get_object_or_404(DossierMedical, pk=pk)
        dossier.is_archived = True
        dossier.save()
        return Response({"message": "Dossier archived successfully"}, status=status.HTTP_200_OK)

class DossierMedicalEtudianListView(generics.ListAPIView):
    queryset = DossierMedicalEtudiant.objects.filter(is_archived=False)
    serializer_class = DossierMedicaleSerializer

class DossierMedicalEnseignantListView(generics.ListAPIView):
    queryset = DossierMedicalEnseignant.objects.filter(is_archived=False)
    serializer_class = DossierMedicaleSerializer

class DossierMedicalFonctionnaireListView(generics.ListAPIView):
    queryset = DossierMedicalFonctionnaire.objects.filter(is_archived=False)
    serializer_class = DossierMedicaleSerializer

class DossierMedicalSearchView(ListAPIView):
    queryset = None
    serializer_class = DossierMedicaleSerializer
    filter_backends = [SearchFilter]
    search_fields = ['nom', 'prenom']

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(nom__istartswith=search_query) | queryset.filter(prenom__istartswith=search_query)
        return queryset

class DossierMedicalEnseignantSearchView(DossierMedicalSearchView):
    queryset = DossierMedicalEnseignant.objects.all()

class DossierMedicalEtudiantSearchView(DossierMedicalSearchView):
    queryset = DossierMedicalEtudiant.objects.all()

class DossierMedicalFonctionnaireSearchView(DossierMedicalSearchView):
    queryset = DossierMedicalFonctionnaire.objects.all()

class DossierMedicalEtudiantView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            dossier = get_object_or_404(DossierMedicalEtudiant, pk=pk)
            serializer = DossierMedicalEtudiantSerializer(dossier, context={"request": request})
        else:
            dossiers = DossierMedicalEtudiant.objects.all()
            serializer = DossierMedicalEtudiantSerializer(dossiers, many=True, context={"request": request})
        return Response(serializer.data)  # Positional argument

    def post(self, request):
        try:
            serializer = DossierMedicalEtudiantSerializer(data=request.data, context={"request": request})
            if serializer.is_valid():
                dossier = serializer.save()

                # Generate styled PDF
                buffer = BytesIO()
                pdf = canvas.Canvas(buffer, pagesize=letter)
                width, height = letter

                # Header
                pdf.setFillColorRGB(0.29, 0.63, 0.66)  # #4BA0A8
                pdf.setFont("Helvetica-Bold", 16)
                pdf.drawCentredString(width / 2, height - 40, "FICHE MÉDICALE")
                pdf.setFont("Helvetica", 10)
                pdf.drawCentredString(width / 2, height - 60, "République Algérienne Démocratique et Populaire")
                pdf.drawCentredString(width / 2, height - 75, "École Nationale Supérieure d'Informatique")
                pdf.setStrokeColorRGB(0.47, 0.84, 0.75)  # #79D7BE
                pdf.setLineWidth(2)
                pdf.line(50, height - 80, width - 50, height - 80)

                # Personal Info Section
                pdf.setFillColorRGB(0.18, 0.31, 0.47)  # #2E5077
                pdf.setFont("Helvetica-Bold", 12)
                pdf.drawString(50, height - 100, "Informations Personnelles")
                pdf.setStrokeColorRGB(0.47, 0.84, 0.75)  # #79D7BE
                pdf.rect(50, height - 240, width - 100, 130, stroke=1, fill=0)
                pdf.setFillColorRGB(0, 0, 0)  # Black for text
                pdf.setFont("Helvetica", 10)
                y = height - 120
                personal_fields = [
                    ("Nom", "nom"), ("Prénom", "prenom"), ("Date de naissance", "date_naissance"),
                    ("Lieu de naissance", "lieu_naissance"), ("Adresse", "adresse"),
                    ("Numéro de téléphone", "numero_telephone"), ("Email", "email"),
                    ("Situation familiale", "situation_familiale"), ("Admis(e)", "admission_etablissement"),
                    ("Filière", "Filiere"), ("Niveau", "Niveau"), ("N° dossier", "numero_dossier"),
                    ("Groupe sanguin", "groupe_sanguin"), ("N° sécurité sociale", "numero_securite_sociale")
                ]
                x_label, x_value = 60, 200
                for label, key in personal_fields[:7]:
                    value = request.data.get(key, "N/A")
                    pdf.drawString(x_label, y, f"{label}:")
                    pdf.drawString(x_value, y, str(value))
                    y -= 15
                y = height - 120
                for label, key in personal_fields[7:]:
                    value = request.data.get(key, "N/A")
                    pdf.drawString(x_label + 300, y, f"{label}:")
                    pdf.drawString(x_value + 300, y, str(value))
                    y -= 15

                # Biometric Data Section
                pdf.setFillColorRGB(0.18, 0.31, 0.47)  # #2E5077
                pdf.setFont("Helvetica-Bold", 12)
                pdf.drawString(50, height - 260, "Données Biométriques")
                pdf.line(50, height - 265, 200, height - 265)  # Underline
                pdf.setStrokeColorRGB(0.47, 0.84, 0.75)  # #79D7BE
                pdf.rect(50, height - 340, width - 100, 70, stroke=1, fill=0)
                pdf.setFillColorRGB(0, 0, 0)
                pdf.setFont("Helvetica", 10)
                y = height - 280
                biometric_fields = [
                    ("Taille (cm)", "taille"), ("Poids (kg)", "poids"),
                    ("Fréquence cardiaque (bpm)", "frequence_cardiaque"), ("Pression artérielle", "pression_arterielle")
                ]
                for label, key in biometric_fields:
                    value = request.data.get(key, "N/A")
                    pdf.drawString(x_label, y, f"{label}:")
                    pdf.drawString(x_value, y, str(value))
                    y -= 15

                pdf.showPage()
                pdf.save()
                pdf_data = buffer.getvalue()
                buffer.close()

                document = Document(
                    title=f"Dossier_{dossier.nom}_{dossier.prenom}_{dossier.numero_dossier}.pdf",
                    dossier_medical=dossier
                )
                document.file.save(document.title, ContentFile(pdf_data))
                document.save()
                dossier.dossier_documents.add(document)

                return Response(serializer.data, status=status.HTTP_201_CREATED)  # Consistent usage
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({"error": "Internal server error", "detail": str(e)}, status=500)

    def put(self, request, pk):
        dossier = get_object_or_404(DossierMedicalEtudiant, pk=pk)
        serializer = DossierMedicalEtudiantSerializer(dossier, data=request.data, partial=True, context={"request": request})
        if serializer.is_valid():
            dossier = serializer.save()

            # Generate styled PDF
            buffer = BytesIO()
            pdf = canvas.Canvas(buffer, pagesize=letter)
            width, height = letter

            # Header
            pdf.setFillColorRGB(0.29, 0.63, 0.66)  # #4BA0A8
            pdf.setFont("Helvetica-Bold", 16)
            pdf.drawCentredString(width / 2, height - 40, "FICHE MÉDICALE")
            pdf.setFont("Helvetica", 10)
            pdf.drawCentredString(width / 2, height - 60, "République Algérienne Démocratique et Populaire")
            pdf.drawCentredString(width / 2, height - 75, "École Nationale Supérieure d'Informatique")
            pdf.setStrokeColorRGB(0.47, 0.84, 0.75)  # #79D7BE
            pdf.setLineWidth(2)
            pdf.line(50, height - 80, width - 50, height - 80)

            # Personal Info Section
            pdf.setFillColorRGB(0.18, 0.31, 0.47)  # #2E5077
            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawString(50, height - 100, "Informations Personnelles")
            pdf.setStrokeColorRGB(0.47, 0.84, 0.75)  # #79D7BE
            pdf.rect(50, height - 240, width - 100, 130, stroke=1, fill=0)
            pdf.setFillColorRGB(0, 0, 0)
            pdf.setFont("Helvetica", 10)
            y = height - 120
            personal_fields = [
                ("Nom", "nom"), ("Prénom", "prenom"), ("Date de naissance", "date_naissance"),
                ("Lieu de naissance", "lieu_naissance"), ("Adresse", "adresse"),
                ("Numéro de téléphone", "numero_telephone"), ("Email", "email"),
                ("Situation familiale", "situation_familiale"), ("Admis(e)", "admission_etablissement"),
                ("Filière", "Filiere"), ("Niveau", "Niveau"), ("N° dossier", "numero_dossier"),
                ("Groupe sanguin", "groupe_sanguin"), ("N° sécurité sociale", "numero_securite_sociale")
            ]
            x_label, x_value = 60, 200
            for label, key in personal_fields[:7]:
                value = serializer.data.get(key, "N/A")
                pdf.drawString(x_label, y, f"{label}:")
                pdf.drawString(x_value, y, str(value))
                y -= 15
            y = height - 120
            for label, key in personal_fields[7:]:
                value = serializer.data.get(key, "N/A")
                pdf.drawString(x_label + 300, y, f"{label}:")
                pdf.drawString(x_value + 300, y, str(value))
                y -= 15

            # Biometric Data Section
            pdf.setFillColorRGB(0.18, 0.31, 0.47)  # #2E5077
            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawString(50, height - 260, "Données Biométriques")
            pdf.line(50, height - 265, 200, height - 265)  # Underline
            pdf.setStrokeColorRGB(0.47, 0.84, 0.75)  # #79D7BE
            pdf.rect(50, height - 340, width - 100, 70, stroke=1, fill=0)
            pdf.setFillColorRGB(0, 0, 0)
            pdf.setFont("Helvetica", 10)
            y = height - 280
            biometric_fields = [
                ("Taille (cm)", "taille"), ("Poids (kg)", "poids"),
                ("Fréquence cardiaque (bpm)", "frequence_cardiaque"), ("Pression artérielle", "pression_arterielle")
            ]
            for label, key in biometric_fields:
                value = serializer.data.get(key, "N/A")
                pdf.drawString(x_label, y, f"{label}:")
                pdf.drawString(x_value, y, str(value))
                y -= 15

            pdf.showPage()
            pdf.save()
            pdf_data = buffer.getvalue()
            buffer.close()

            # Update or create PDF
            if dossier.dossier_documents.exists():
                document = dossier.dossier_documents.first()
                document.file.save(document.title, ContentFile(pdf_data))
            else:
                document = Document(
                    title=f"Dossier_{dossier.nom}_{dossier.prenom}_{dossier.numero_dossier}.pdf",
                    dossier_medical=dossier
                )
                document.file.save(document.title, ContentFile(pdf_data))
                document.save()
                dossier.dossier_documents.add(document)

            return Response(serializer.data)  # Consistent usage
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DossierMedicalEnseignantView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            dossier = get_object_or_404(DossierMedicalEnseignant, pk=pk)
            serializer = DossierMedicalEnseignantSerializer(dossier, context={"request": request})
        else:
            dossiers = DossierMedicalEnseignant.objects.all()
            serializer = DossierMedicalEnseignantSerializer(dossiers, many=True, context={"request": request})
        return Response(serializer.data)

    def post(self, request):
        serializer = DossierMedicalEnseignantSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        dossier = get_object_or_404(DossierMedicalEnseignant, pk=pk)
        serializer = DossierMedicalEnseignantSerializer(dossier, data=request.data, partial=True, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DossierMedicalATSView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            dossier = get_object_or_404(DossierMedicalFonctionnaire, pk=pk)
            serializer = DossierMedicalAtsSerializer(dossier, context={"request": request})
        else:
            dossiers = DossierMedicalFonctionnaire.objects.all()
            serializer = DossierMedicalAtsSerializer(dossiers, many=True, context={"request": request})
        return Response(serializer.data)

    def post(self, request):
        serializer = DossierMedicalAtsSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        dossier = get_object_or_404(DossierMedicalFonctionnaire, pk=pk)
        serializer = DossierMedicalAtsSerializer(dossier, data=request.data, partial=True, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Search functions
def base_search_view(request, model, serializer):
    search_query = request.GET.get("search", "").strip()
    if search_query:
        words = search_query.split()
        query = Q()
        for word in words:
            query |= Q(prenom__istartswith=word) | Q(nom__icontains=word)
        if request.user.role == "ADMIN":
            queryset = model.objects.filter(query).distinct()
        else:
            queryset = model.objects.filter(query, is_archived=False).distinct()
    else:
        if request.user.role == "ADMIN":
            queryset = model.objects.all()
        else:
            queryset = model.objects.filter(is_archived=False)
    serialized_data = serializer(queryset, many=True)
    return Response(serialized_data.data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_DossierMedicalEtudian(request):
    return base_search_view(request, DossierMedicalEtudiant, DossierMedicalEtudiantSerializer)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_DossierMedicalEnseignant(request):
    return base_search_view(request, DossierMedicalEnseignant, DossierMedicalEnseignantSerializer)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_DossierMedicalFonctionnaire(request):
    return base_search_view(request, DossierMedicalFonctionnaire, DossierMedicalFonctionnaireSerializer)

# Consulter dossier médical
def get_dossier_model(user):
    for model, serializer_class in [
        (DossierMedicalEtudiant, DossierMedicalEtudiantSerializer),
        (DossierMedicalEnseignant, DossierMedicalEnseignantSerializer),
        (DossierMedicalFonctionnaire, DossierMedicalFonctionnaireSerializer),
    ]:
        if model.objects.filter(user=user).exists():
            return model, serializer_class
    return None, None

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def consulter_dossier_medical(request, dossier_id=None):
    user = request.user
    if user.role in ["MEDECIN", "ASSISTANT_MEDECIN", "DOCTOR", "ASSISTANT"]:
        if dossier_id:
            dossier = None
            model_found = None
            for model in [DossierMedicalEtudiant, DossierMedicalEnseignant, DossierMedicalFonctionnaire]:
                temp_dossier = model.objects.filter(pk=dossier_id).first()
                if temp_dossier:
                    dossier = temp_dossier
                    model_found = model
                    break
            if not dossier:
                return Response({"error": "Ce dossier n'existe pas"}, status=status.HTTP_404_NOT_FOUND)
            if dossier.is_archived:
                return Response(
                    {"error": "Dossier archivé", "message": "Ce dossier existe mais a été archivé", "dossier_id": dossier_id, "nom_complet": f"{dossier.nom} {dossier.prenom}"},
                    status=status.HTTP_403_FORBIDDEN
                )
            if model_found == DossierMedicalEtudiant:
                serializer = DossierMedicalEtudiantSerializer(dossier)
            elif model_found == DossierMedicalEnseignant:
                serializer = DossierMedicalEnseignantSerializer(dossier)
            else:
                serializer = DossierMedicalFonctionnaireSerializer(dossier)
            return Response(serializer.data)
        else:
            result = []
            etudiants = DossierMedicalEtudiant.objects.filter(is_archived=False).order_by("-id")
            result.extend(DossierMedicalEtudiantSerializer(etudiants, many=True).data)
            enseignants = DossierMedicalEnseignant.objects.filter(is_archived=False).order_by("-id")
            result.extend(DossierMedicalEnseignantSerializer(enseignants, many=True).data)
            fonctionnaires = DossierMedicalFonctionnaire.objects.filter(is_archived=False).order_by("-id")
            result.extend(DossierMedicalFonctionnaireSerializer(fonctionnaires, many=True).data)
            result.sort(key=lambda x: x["id"], reverse=True)
            return Response(result)
    elif user.role == "PATIENT":
        model, serializer_class = get_dossier_model(user)
        if dossier_id:
            dossier = None
            for model_class in [DossierMedicalEtudiant, DossierMedicalEnseignant, DossierMedicalFonctionnaire]:
                dossier = model_class.objects.filter(pk=dossier_id, user=user).first()
                if dossier:
                    break
            if not dossier:
                return Response({"error": "Vous n'avez pas accès à ce dossier."}, status=status.HTTP_404_NOT_FOUND)
            if dossier.is_archived:
                return Response({"error": "Votre dossier médical a été archivé."}, status=status.HTTP_403_FORBIDDEN)
            if isinstance(dossier, DossierMedicalEtudiant):
                serializer = DossierMedicalEtudiantSerializer(dossier)
            elif isinstance(dossier, DossierMedicalEnseignant):
                serializer = DossierMedicalEnseignantSerializer(dossier)
            else:
                serializer = DossierMedicalFonctionnaireSerializer(dossier)
            return Response(serializer.data)
        else:
            if not model:
                return Response({"error": "Votre dossier médical n'a pas encore été créé."}, status=status.HTTP_404_NOT_FOUND)
            dossier = model.objects.filter(user=user).first()
            if not dossier:
                return Response({"error": "Votre dossier médical n'a pas encore été créé."}, status=status.HTTP_404_NOT_FOUND)
            if dossier.is_archived:
                return Response({"error": "Votre dossier médical a été archivé."}, status=status.HTTP_404_NOT_FOUND)
            serializer = serializer_class(dossier)
            return Response(serializer.data)
    elif user.role == "ADMIN":
        if dossier_id:
            for model in [DossierMedicalEtudiant, DossierMedicalEnseignant, DossierMedicalFonctionnaire]:
                dossier = model.objects.filter(pk=dossier_id).first()
                if dossier:
                    return Response({"id": dossier.id, "nom": dossier.nom, "prenom": dossier.prenom, "is_archived": dossier.is_archived})
            return Response({"error": "Dossier non trouvé "}, status=status.HTTP_404_NOT_FOUND)
        else:
            result = []
            for dossier in DossierMedicalEtudiant.objects.all().order_by("-id"):
                result.append({"id": dossier.id, "nom": dossier.nom, "prenom": dossier.prenom, "is_archived": dossier.is_archived})
            for dossier in DossierMedicalEnseignant.objects.all().order_by("-id"):
                result.append({"id": dossier.id, "nom": dossier.nom, "prenom": dossier.prenom, "is_archived": dossier.is_archived})
            for dossier in DossierMedicalFonctionnaire.objects.all().order_by("-id"):
                result.append({"id": dossier.id, "nom": dossier.nom, "prenom": dossier.prenom, "is_archived": dossier.is_archived})
            result.sort(key=lambda x: x["id"], reverse=True)
            return Response(result)
    return Response({"error": "Accès non autorisé aux dossiers médicaux"}, status=status.HTTP_403_FORBIDDEN)

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GenerateMedicalFormPDF(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        if not data:
            return Response({"error": "Form data is missing!"}, status=400)
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer)
        pdf.drawString(100, 800, f"Patient Name: {data.get('name', 'N/A')}")
        pdf.drawString(100, 780, f"Patient Age: {data.get('age', 'N/A')}")
        pdf.drawString(100, 760, f"Medical History: {data.get('medical_history', 'N/A')}")
        pdf.drawString(100, 740, f"Current Symptoms: {data.get('current_symptoms', 'N/A')}")
        pdf.drawString(100, 720, f"Doctor's Notes: {data.get('doctors_notes', 'N/A')}")
        pdf.showPage()
        pdf.save()
        pdf_data = buffer.getvalue()
        buffer.close()
        document = Document()
        document.title = f"Medical Form - {data.get('name', 'Unknown')}"
        document.file.save("medical_form.pdf", ContentFile(pdf_data))
        document.save()
        response = HttpResponse(pdf_data, content_type="application/pdf")
        response["Content-Disposition"] = 'inline; filename="medical_form.pdf"'
        return response

class DownloadMedicalForm(APIView):
    def get(self, request, document_id):
        document = get_object_or_404(Document, id=document_id)
        file_path = document.file.path
        try:
            with open(file_path, "rb") as file:
                response = HttpResponse(file.read(), content_type="application/pdf")
                response["Content-Disposition"] = f'attachment; filename="{document.title}"'
                return response
        except FileNotFoundError:
            return Response({"error": "File not found!"}, status=404)