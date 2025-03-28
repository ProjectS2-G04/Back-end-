from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import (
    DossierMedicalEtudian,
    DossierMedicalEnseignant,
    DossierMedicalFonctionnaire,
)
from .serializers import (
    DossierMedicalEtudiantSerializer,
    DossierMedicalEnseignantSerializer,
    DossierMedicalAtsSerializer,
)

# from .permissions import check_doctor_permission
from rest_framework.permissions import IsAuthenticated


class DossierMedicalEtudiantView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            dossier = DossierMedicalEtudian.objects.get(pk=pk)
            serializer = DossierMedicalEtudiantSerializer(dossier)
        else:
            dossiers = DossierMedicalEtudian.objects.all()
            serializer = DossierMedicalEtudiantSerializer(dossiers, many=True)
        return Response(serializer.data)

    def post(self, request):
        # check_doctor_permission(request)
        serializer = DossierMedicalEtudiantSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        # check_doctor_permission(request)
        dossier = DossierMedicalEtudian.objects.get(pk=pk)
        serializer = DossierMedicalEtudiantSerializer(
            dossier, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DossierMedicalEnseignantView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            dossier = DossierMedicalEnseignant.objects.get(pk=pk)
            serializer = DossierMedicalEnseignantSerializer(dossier)
        else:
            dossiers = DossierMedicalEnseignant.objects.all()
            serializer = DossierMedicalEnseignantSerializer(dossiers, many=True)
        return Response(serializer.data)

    def post(self, request):
        # check_doctor_permission(request)
        serializer = DossierMedicalEnseignantSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        # check_doctor_permission(request)
        dossier = DossierMedicalEnseignant.objects.get(pk=pk)
        serializer = DossierMedicalEnseignantSerializer(
            dossier, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DossierMedicalATSView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            dossier = DossierMedicalFonctionnaire.objects.get(pk=pk)
            serializer = DossierMedicalAtsSerializer(dossier)
        else:
            dossiers = DossierMedicalFonctionnaire.objects.all()
            serializer = DossierMedicalAtsSerializer(dossiers, many=True)
        return Response(serializer.data)

    def post(self, request):
        # check_doctor_permission(request)
        serializer = DossierMedicalAtsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        # check_doctor_permission(request)
        dossier = DossierMedicalFonctionnaire.objects.get(pk=pk)
        serializer = DossierMedicalAtsSerializer(
            dossier, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
