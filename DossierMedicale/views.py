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
import DossierMedicale
from accounts.models import User
from .models import *
from .serializers import *
from .utils.pdf_generator import generate_medical_pdf
# views.py
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import DossierMedicalEtudiant, DossierMedicalEnseignant, DossierMedicalFonctionnaire
from .serializers import DossierMedicalEtudiantSerializer, DossierMedicalEnseignantSerializer, DossierMedicalAtsSerializer
import logging

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
    serializer_class = DossierMedicalEtudiantSerializer

class DossierMedicalEnseignantListView(generics.ListAPIView):
    queryset = DossierMedicalEnseignant.objects.filter(is_archived=False)
    serializer_class = DossierMedicalEnseignantSerializer

class DossierMedicalFonctionnaireListView(generics.ListAPIView):
    queryset = DossierMedicalFonctionnaire.objects.filter(is_archived=False)
    serializer_class = DossierMedicalAtsSerializer

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

# views.py
import logging
logger = logging.getLogger(__name__)

from rest_framework.parsers import MultiPartParser, FormParser

class DossierMedicalEtudiantView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # Add parsers

    def get(self, request, pk=None):
        if pk:
            dossier = get_object_or_404(DossierMedicalEtudiant, pk=pk)
            serializer = DossierMedicalEtudiantSerializer(dossier, context={"request": request})
        else:
            dossiers = DossierMedicalEtudiant.objects.all()
            serializer = DossierMedicalEtudiantSerializer(dossiers, many=True, context={"request": request})
        return Response(serializer.data)

    def post(self, request):
        logger.info(f"POST request received for DossierMedicalEtudiantView: {request.data}")
        serializer = DossierMedicalEtudiantSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            dossier = serializer.save()
            logger.info(f"Dossier created: ID {dossier.id}")
            generate_medical_pdf(dossier, serializer.data, "etudiant", Document)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f"Serializer errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        dossier = get_object_or_404(DossierMedicalEtudiant, pk=pk)
        serializer = DossierMedicalEtudiantSerializer(dossier, data=request.data, partial=True, context={"request": request})
        if serializer.is_valid():
            dossier = serializer.save()
            generate_medical_pdf(dossier, serializer.data, "etudiant", Document)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




logger = logging.getLogger(__name__)

class DossierMedicalEnseignantView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, pk=None):
        try:
            if pk:
                dossier = get_object_or_404(DossierMedicalEnseignant, pk=pk)
                serializer = DossierMedicalEnseignantSerializer(dossier, context={"request": request})
                logger.info(f"Retrieved dossier ID {pk} for user: {request.user.email}")
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                dossiers = DossierMedicalEnseignant.objects.filter(is_archived=False)
                serializer = DossierMedicalEnseignantSerializer(dossiers, many=True, context={"request": request})
                logger.info(f"Retrieved {len(dossiers)} dossiers for user: {request.user.email}")
                return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error retrieving dossier(s) for user {request.user.email}: {str(e)}", exc_info=True)
            return Response({"error": f"Internal server error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            logger.info(f"POST request received for DossierMedicalEnseignantView: {request.data}")
            serializer = DossierMedicalEnseignantSerializer(data=request.data, context={"request": request})
            if serializer.is_valid():
                dossier = serializer.save()
                generate_medical_pdf(dossier, serializer.data, "enseignant", Document)
                logger.info(f"Dossier created: ID {dossier.id} for user: {request.user.email}")
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error creating dossier for user {request.user.email}: {str(e)}", exc_info=True)
            return Response({"error": f"Internal server error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk):
        try:
            dossier = get_object_or_404(DossierMedicalEnseignant, pk=pk)
            logger.info(f"PUT request received for dossier ID {pk} by user: {request.user.email}")
            serializer = DossierMedicalEnseignantSerializer(dossier, data=request.data, partial=True, context={"request": request})
            if serializer.is_valid():
                dossier = serializer.save()
                generate_medical_pdf(dossier, serializer.data, "enseignant", Document)
                logger.info(f"Dossier updated: ID {dossier.id}")
                return Response(serializer.data, status=status.HTTP_200_OK)
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error updating dossier ID {pk} for user {request.user.email}: {str(e)}", exc_info=True)
            return Response({"error": f"Internal server error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DossierMedicalATSView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

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
            generate_medical_pdf(dossier, serializer.data, "fonctionnaires", Document)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        dossier = get_object_or_404(DossierMedicalFonctionnaire, pk=pk)
        serializer = DossierMedicalAtsSerializer(dossier, data=request.data, partial=True, context={"request": request})
        if serializer.is_valid():
            dossier = serializer.save()
            generate_medical_pdf(dossier, serializer.data, "fonctionnaires", Document)
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
logger = logging.getLogger(__name__)

def get_dossier_model(user):
    """
    Determine the dossier model and serializer based on user's sub_role.
    """
    try:
        sub_role = user.sub_role.lower() if hasattr(user, 'sub_role') and user.sub_role else None
        logger.info(f"Determining dossier model for user: {user.email}, sub_role: {sub_role}")
        if sub_role in ['student', 'etudiant']:
            return DossierMedicalEtudiant, DossierMedicalEtudiantSerializer
        elif sub_role in ['teacher', 'enseignant']:
            return DossierMedicalEnseignant, DossierMedicalEnseignantSerializer
        elif sub_role in ['ats', 'fonctionnaire']:
            return DossierMedicalFonctionnaire, DossierMedicalAtsSerializer
        logger.warning(f"No dossier model found for sub_role: {sub_role}")
        return None, None
    except Exception as e:
        logger.error(f"Error in get_dossier_model for user {user.email}: {str(e)}", exc_info=True)
        return None, None

# views.py
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def consulter_dossier_medical(request, dossier_id=None):
    user = request.user
    logger.info(f"Fetching dossier for user: {user.email}, dossier_id: {dossier_id}, role: {user.role}")

    try:
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
                    logger.warning(f"Dossier {dossier_id} not found for medical staff")
                    return Response({"error": "Ce dossier n'existe pas"}, status=status.HTTP_404_NOT_FOUND)
                if dossier.is_archived:
                    logger.warning(f"Dossier {dossier_id} is archived")
                    return Response(
                        {
                            "error": "Dossier archivé",
                            "message": "Ce dossier existe mais a été archivé",
                            "dossier_id": dossier_id,
                            "nom_complet": f"{dossier.nom} {dossier.prenom}"
                        },
                        status=status.HTTP_403_FORBIDDEN
                    )
                context = {"request": request}
                if model_found == DossierMedicalEtudiant:
                    serializer = DossierMedicalEtudiantSerializer(dossier, context=context)
                elif model_found == DossierMedicalEnseignant:
                    serializer = DossierMedicalEnseignantSerializer(dossier, context=context)
                else:
                    serializer = DossierMedicalAtsSerializer(dossier, context=context)
                logger.info(f"Dossier found: ID {dossier.id} for medical staff")
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                result = []
                context = {"request": request}
                etudiants = DossierMedicalEtudiant.objects.filter(is_archived=False).order_by("-id")
                result.extend(DossierMedicalEtudiantSerializer(etudiants, many=True, context=context).data)
                enseignants = DossierMedicalEnseignant.objects.filter(is_archived=False).order_by("-id")
                result.extend(DossierMedicalEnseignantSerializer(enseignants, many=True, context=context).data)
                fonctionnaires = DossierMedicalFonctionnaire.objects.filter(is_archived=False).order_by("-id")
                result.extend(DossierMedicalAtsSerializer(fonctionnaires, many=True, context=context).data)
                result.sort(key=lambda x: x["id"], reverse=True)
                logger.info(f"Returning {len(result)} dossiers for medical staff")
                return Response(result, status=status.HTTP_200_OK)

        elif user.role == "PATIENT":
            if dossier_id:
                dossier = None
                for model_class in [DossierMedicalEtudiant, DossierMedicalEnseignant, DossierMedicalFonctionnaire]:
                    dossier = model_class.objects.filter(pk=dossier_id, user=user).first()
                    if dossier:
                        break
                if not dossier:
                    logger.warning(f"Dossier {dossier_id} not found or not owned by user: {user.email}")
                    return Response({"error": "Vous n'avez pas accès à ce dossier."}, status=status.HTTP_404_NOT_FOUND)
                if dossier.is_archived:
                    logger.warning(f"Dossier {dossier_id} is archived for user: {user.email}")
                    return Response({"error": "Votre dossier médical a été archivé."}, status=status.HTTP_403_FORBIDDEN)
                context = {"request": request}
                if isinstance(dossier, DossierMedicalEtudiant):
                    serializer = DossierMedicalEtudiantSerializer(dossier, context=context)
                elif isinstance(dossier, DossierMedicalEnseignant):
                    serializer = DossierMedicalEnseignantSerializer(dossier, context=context)
                else:
                    serializer = DossierMedicalAtsSerializer(dossier, context=context)
                logger.info(f"Dossier found: ID {dossier.id} for patient")
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                model, serializer_class = get_dossier_model(user)
                if not model:
                    logger.warning(f"No dossier model for user: {user.email}")
                    return Response({"error": "Votre dossier médical n'a pas encore été créé."}, status=status.HTTP_404_NOT_FOUND)
                dossier = model.objects.filter(user=user).first()
                if not dossier:
                    logger.warning(f"No dossier found for user: {user.email}")
                    return Response({"error": "Votre dossier médical n'a pas encore été créé."}, status=status.HTTP_404_NOT_FOUND)
                if dossier.is_archived:
                    logger.warning(f"Dossier is archived for user: {user.email}")
                    return Response({"error": "Votre dossier médical a été archivé."}, status=status.HTTP_403_FORBIDDEN)
                context = {"request": request}
                serializer = serializer_class(dossier, context=context)
                logger.info(f"Dossier found: ID {dossier.id} for patient")
                return Response(serializer.data, status=status.HTTP_200_OK)

        elif user.role == "ADMIN":
            if dossier_id:
                for model in [DossierMedicalEtudiant, DossierMedicalEnseignant, DossierMedicalFonctionnaire]:
                    dossier = model.objects.filter(pk=dossier_id).first()
                    if dossier:
                        logger.info(f"Dossier found for admin: ID {dossier.id}")
                        return Response(
                            {"id": dossier.id, "nom": dossier.nom, "prenom": dossier.prenom, "is_archived": dossier.is_archived},
                            status=status.HTTP_200_OK
                        )
                logger.warning(f"Dossier {dossier_id} not found for admin")
                return Response({"error": "Dossier non trouvé"}, status=status.HTTP_404_NOT_FOUND)
            else:
                result = []
                for dossier in DossierMedicalEtudiant.objects.all().order_by("-id"):
                    result.append({"id": dossier.id, "nom": dossier.nom, "prenom": dossier.prenom, "is_archived": dossier.is_archived})
                for dossier in DossierMedicalEnseignant.objects.all().order_by("-id"):
                    result.append({"id": dossier.id, "nom": dossier.nom, "prenom": dossier.prenom, "is_archived": dossier.is_archived})
                for dossier in DossierMedicalFonctionnaire.objects.all().order_by("-id"):
                    result.append({"id": dossier.id, "nom": dossier.nom, "prenom": dossier.prenom, "is_archived": dossier.is_archived})
                result.sort(key=lambda x: x["id"], reverse=True)
                logger.info(f"Returning {len(result)} dossiers for admin")
                return Response(result, status=status.HTTP_200_OK)

        logger.warning(f"Unauthorized access by user: {user.email}, role: {user.role}")
        return Response({"error": "Accès non autorisé aux dossiers médicaux"}, status=status.HTTP_403_FORBIDDEN)

    except Exception as e:
        logger.error(f"Error in consulter_dossier_medical for user {user.email}, dossier_id: {dossier_id}: {str(e)}", exc_info=True)
        return Response({"error": f"Internal server error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
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



# Set up logging
logger = logging.getLogger(__name__)



class GetUserDossierView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            logger.info(f"Fetching dossier for user: {user.email} (ID: {user.id}, sub_role: {user.sub_role})")
            
            # Determine the correct model and serializer based on sub_role
            model, serializer_class = get_dossier_model(user)
            if not model:
                logger.warning(f"No dossier model found for user: {user.email}, sub_role: {user.sub_role}")
                return Response(
                    {"error": "No dossier model matches your user role."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Fetch the dossier for the authenticated user
            dossier = model.objects.filter(user=user).first()
            if not dossier:
                logger.warning(f"No dossier found for user: {user.email}, sub_role: {user.sub_role}")
                return Response(
                    {"error": "Dossier not found for this user."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            if dossier.is_archived:
                logger.warning(f"Dossier is archived for user: {user.email}, ID: {dossier.id}")
                return Response(
                    {"error": "Votre dossier médical a été archivé."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            serializer = serializer_class(dossier, context={'request': request})
            logger.info(f"Dossier found: ID {dossier.id} for user: {user.email}")
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error fetching dossier for user {user.email}: {str(e)}", exc_info=True)
            return Response(
                {"error": f"Internal server error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )