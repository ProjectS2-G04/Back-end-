import os
from io import BytesIO

from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import FormParser, MultiPartParser

# from .permissions import check_doctor_permission
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import *
from .serializers import *


class DossierMedicalEtudiantView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            dossier = get_object_or_404(DossierMedicalEtudiant, pk=pk)
            serializer = DossierMedicalEtudiantSerializer(
                dossier, context={"request": request}
            )
        else:
            dossiers = DossierMedicalEtudiant.objects.all()
            serializer = DossierMedicalEtudiantSerializer(
                dossiers, many=True, context={"request": request}
            )
        return Response(serializer.data)

    def post(self, request):
        serializer = DossierMedicalEtudiantSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        dossier = get_object_or_404(DossierMedicalEtudiant, pk=pk)
        serializer = DossierMedicalEtudiantSerializer(
            dossier, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DossierMedicalEnseignantView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            dossier = get_object_or_404(DossierMedicalEnseignant, pk=pk)
            serializer = DossierMedicalEnseignantSerializer(
                dossier, context={"request": request}
            )
        else:
            dossiers = DossierMedicalEnseignant.objects.all()
            serializer = DossierMedicalEnseignantSerializer(
                dossiers, many=True, context={"request": request}
            )
        return Response(serializer.data)

    def post(self, request):
        serializer = DossierMedicalEnseignantSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        dossier = get_object_or_404(DossierMedicalEnseignant, pk=pk)
        serializer = DossierMedicalEnseignantSerializer(
            dossier, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DossierMedicalATSView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            dossier = get_object_or_404(DossierMedicalFonctionnaire, pk=pk)
            serializer = DossierMedicalAtsSerializer(
                dossier, context={"request": request}
            )
        else:
            dossiers = DossierMedicalFonctionnaire.objects.all()
            serializer = DossierMedicalAtsSerializer(
                dossiers, many=True, context={"request": request}
            )
        return Response(serializer.data)

    def post(self, request):
        serializer = DossierMedicalAtsSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        dossier = get_object_or_404(DossierMedicalFonctionnaire, pk=pk)
        serializer = DossierMedicalAtsSerializer(
            dossier, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# search functions
def base_search_view(request, model, serializer):
    search_query = request.GET.get("search", "").strip()

    if search_query:
        words = search_query.split()
        query = Q()
        for word in words:
            query |= Q(prenom__istartswith=word) | Q(nom__icontains=word)
            # query |= Q(nom__iexact=word) | Q(prenom__iexact=word)
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
    return base_search_view(
        request, DossierMedicalEtudiant, DossierMedicalEtudiantSerializer
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_DossierMedicalEnseignant(request):
    return base_search_view(
        request, DossierMedicalEnseignant, DossierMedicalEnseignantSerializer
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_DossierMedicalFonctionnaire(request):
    return base_search_view(
        request, DossierMedicalFonctionnaire, DossierMedicalFonctionnaireSerializer
    )


# consulter_dossier_medical
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
            for model in [
                DossierMedicalEtudiant,
                DossierMedicalEnseignant,
                DossierMedicalFonctionnaire,
            ]:
                temp_dossier = model.objects.filter(pk=dossier_id).first()
                if temp_dossier:
                    dossier = temp_dossier
                    model_found = model
                    break

            if not dossier:
                return Response(
                    {"error": "Ce dossier n'existe pas"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if dossier.is_archived:
                return Response(
                    {
                        "error": "Dossier archivé",
                        "message": "Ce dossier existe mais a été archivé",
                        "dossier_id": dossier_id,
                        "nom_complet": f"{dossier.nom} {dossier.prenom}",
                    },
                    status=status.HTTP_403_FORBIDDEN,
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

            # etudiants = DossierMedicalEtudian.objects.all().order_by('-id')
            etudiants = DossierMedicalEtudiant.objects.filter(
                is_archived=False
            ).order_by("-id")
            result.extend(DossierMedicalEtudiantSerializer(etudiants, many=True).data)

            # enseignants = DossierMedicalEnseignant.objects.all().order_by('-id')
            enseignants = DossierMedicalEnseignant.objects.filter(
                is_archived=False
            ).order_by("-id")
            result.extend(
                DossierMedicalEnseignantSerializer(enseignants, many=True).data
            )

            # fonctionnaires = DossierMedicalFonctionnaire.objects.all().order_by('-id')
            fonctionnaires = DossierMedicalFonctionnaire.objects.filter(
                is_archived=False
            ).order_by("-id")
            result.extend(
                DossierMedicalFonctionnaireSerializer(fonctionnaires, many=True).data
            )

            # Tri final par ID (équivalent à date de création si auto-incrément)
            result.sort(key=lambda x: x["id"], reverse=True)

            return Response(result)

    elif user.role == "PATIENT":
        model, serializer_class = get_dossier_model(user)

        if dossier_id:
            dossier = None
            for model_class in [
                DossierMedicalEtudiant,
                DossierMedicalEnseignant,
                DossierMedicalFonctionnaire,
            ]:
                dossier = model_class.objects.filter(pk=dossier_id, user=user).first()
                if dossier:
                    break

            if not dossier:
                return Response(
                    {"error": "Vous n'avez pas accès à ce dossier."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if dossier.is_archived == True:
                return Response(
                    {"error": "Votre dossier médical a été archivé."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            if isinstance(dossier, DossierMedicalEtudiant):
                serializer = DossierMedicalEtudiantSerializer(dossier)
            elif isinstance(dossier, DossierMedicalEnseignant):
                serializer = DossierMedicalEnseignantSerializer(dossier)
            else:
                serializer = DossierMedicalFonctionnaireSerializer(dossier)

            return Response(serializer.data)

        else:

            if not model:
                return Response(
                    {"error": "Votre dossier médical n'a pas encore été créé."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            dossier = model.objects.filter(user=user).first()
            if not dossier:
                return Response(
                    {"error": "Votre dossier médical n'a pas encore été créé."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if dossier.is_archived == True:
                return Response(
                    {"error": "Votre dossier médical a été archivé."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            serializer = serializer_class(dossier)
            return Response(serializer.data)

    elif user.role == "ADMIN":
        # l'admin voient tous les dossiers (archivés et non archivés)
        if dossier_id:
            for model in [
                DossierMedicalEtudiant,
                DossierMedicalEnseignant,
                DossierMedicalFonctionnaire,
            ]:
                dossier = model.objects.filter(pk=dossier_id).first()
                if dossier:
                    return Response(
                        {
                            "id": dossier.id,
                            "nom": dossier.nom,
                            "prenom": dossier.prenom,
                            "is_archived": dossier.is_archived,
                        }
                    )
            return Response(
                {"error": "Dossier non trouvé "}, status=status.HTTP_404_NOT_FOUND
            )
        else:
            result = []
            for dossier in DossierMedicalEtudiant.objects.all().order_by("-id"):
                result.append(
                    {
                        "id": dossier.id,
                        "nom": dossier.nom,
                        "prenom": dossier.prenom,
                        "is_archived": dossier.is_archived,
                    }
                )
            for dossier in DossierMedicalEnseignant.objects.all().order_by("-id"):
                result.append(
                    {
                        "id": dossier.id,
                        "nom": dossier.nom,
                        "prenom": dossier.prenom,
                        "is_archived": dossier.is_archived,
                    }
                )
            for dossier in DossierMedicalFonctionnaire.objects.all().order_by("-id"):
                result.append(
                    {
                        "id": dossier.id,
                        "nom": dossier.nom,
                        "prenom": dossier.prenom,
                        "is_archived": dossier.is_archived,
                    }
                )
            result.sort(key=lambda x: x["id"], reverse=True)
            return Response(result)
    return Response(
        {"error": "Accès non autorisé aux dossiers médicaux"},
        status=status.HTTP_403_FORBIDDEN,
    )


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
        pdf.drawString(
            100, 760, f"Medical History: {data.get('medical_history', 'N/A')}"
        )
        pdf.drawString(
            100, 740, f"Current Symptoms: {data.get('current_symptoms', 'N/A')}"
        )
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
                response["Content-Disposition"] = (
                    f'attachment; filename="{document.title}"'
                )
                return response
        except FileNotFoundError:
            return Response({"error": "File not found!"}, status=404)
