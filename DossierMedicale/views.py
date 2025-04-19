import os
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework import generics
from accounts.models import User
from .models import *
from .serializers import *
from .utils.pdf_generator import generate_medical_pdf

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
        return Response(serializer.data)

    def post(self, request):
        try:
            serializer = DossierMedicalEtudiantSerializer(data=request.data, context={"request": request})
            if serializer.is_valid():
                dossier = serializer.save()
                generate_medical_pdf(dossier, serializer.data, "etudiant", Document)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
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
            generate_medical_pdf(dossier, serializer.data, "etudiant", Document)
            return Response(serializer.data)
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
            dossier = serializer.save()
            generate_medical_pdf(dossier, serializer.data, "enseignant", Document)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        dossier = get_object_or_404(DossierMedicalEnseignant, pk=pk)
        serializer = DossierMedicalEnseignantSerializer(dossier, data=request.data, partial=True, context={"request": request})
        if serializer.is_valid():
            dossier = serializer.save()
            generate_medical_pdf(dossier, serializer.data, "enseignant", Document)
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
            dossier = serializer.save()
            generate_medical_pdf(dossier, serializer.data, "ats", Document)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        dossier = get_object_or_404(DossierMedicalFonctionnaire, pk=pk)
        serializer = DossierMedicalAtsSerializer(dossier, data=request.data, partial=True, context={"request": request})
        if serializer.is_valid():
            dossier = serializer.save()
            generate_medical_pdf(dossier, serializer.data, "ats", Document)
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
    return base_search_view(request, DossierMedicalFonctionnaire, DossierMedicalAtsSerializer)

# Consulter dossier médical
def get_dossier_model(user):
    for model, serializer_class in [
        (DossierMedicalEtudiant, DossierMedicalEtudiantSerializer),
        (DossierMedicalEnseignant, DossierMedicalEnseignantSerializer),
        (DossierMedicalFonctionnaire, DossierMedicalAtsSerializer),
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
            context = {"request": request}  # Add context for single dossier
            if model_found == DossierMedicalEtudiant:
                serializer = DossierMedicalEtudiantSerializer(dossier, context=context)
            elif model_found == DossierMedicalEnseignant:
                serializer = DossierMedicalEnseignantSerializer(dossier, context=context)
            else:
                serializer = DossierMedicalAtsSerializer(dossier, context=context)
            return Response(serializer.data)
        else:
            result = []
            context = {"request": request}  # Add context for list of dossiers
            etudiants = DossierMedicalEtudiant.objects.filter(is_archived=False).order_by("-id")
            result.extend(DossierMedicalEtudiantSerializer(etudiants, many=True, context=context).data)
            enseignants = DossierMedicalEnseignant.objects.filter(is_archived=False).order_by("-id")
            result.extend(DossierMedicalEnseignantSerializer(enseignants, many=True, context=context).data)
            fonctionnaires = DossierMedicalFonctionnaire.objects.filter(is_archived=False).order_by("-id")
            result.extend(DossierMedicalAtsSerializer(fonctionnaires, many=True, context=context).data)
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
            context = {"request": request}  # Add context for patient dossier
            if isinstance(dossier, DossierMedicalEtudiant):
                serializer = DossierMedicalEtudiantSerializer(dossier, context=context)
            elif isinstance(dossier, DossierMedicalEnseignant):
                serializer = DossierMedicalEnseignantSerializer(dossier, context=context)
            else:
                serializer = DossierMedicalAtsSerializer(dossier, context=context)
            return Response(serializer.data)
        else:
            if not model:
                return Response({"error": "Votre dossier médical n'a pas encore été créé."}, status=status.HTTP_404_NOT_FOUND)
            dossier = model.objects.filter(user=user).first()
            if not dossier:
                return Response({"error": "Votre dossier médical n'a pas encore été créé."}, status=status.HTTP_404_NOT_FOUND)
            if dossier.is_archived:
                return Response({"error": "Votre dossier médical a été archivé."}, status=status.HTTP_404_NOT_FOUND)
            context = {"request": request}  # Add context for patient dossier
            serializer = serializer_class(dossier, context=context)
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