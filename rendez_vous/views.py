from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import *
from .permissions import *
from datetime import date as dt_date
today_date = dt_date.today()
from .serializers import *
from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveAPIView

class OrdonnanceDetailView(RetrieveAPIView):
    queryset = Ordonnance.objects.all()
    serializer_class = OrdonnanceDetailSerializer
    permission_classes = [IsAuthenticatedMedecin]
    lookup_field = 'id'


class PatientOrdonnanceListView(ListAPIView):
    serializer_class = OrdonnanceDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only ordonnances of the connected patient
        return Ordonnance.objects.filter(patient=self.request.user)
    

    
class OrdonnanceCreateView(APIView):
    permission_classes = [IsAuthenticatedMedecin]

    def post(self, request, pk ):
        
        age = request.data.get("age")
        try:
            patient = User.objects.get(id=pk)
        except User.DoesNotExist:
            return Response({"error": "Patient not found."}, status=404)

        ordonnance = Ordonnance.objects.create(
            patient=patient,
            medecin=request.user,  # the authenticated doctor
            age=age,
            date=today_date
        )

        # Now create the medicaments
        medicaments_data = request.data.get("medicaments", [])
        for medicament in medicaments_data:
            Medicament.objects.create(
                nom=medicament["nom"],
                posologie=medicament["posologie"],
                duree=medicament["duree"],
                ordonnance=ordonnance
            )

        return Response({"message": "Ordonnance created successfully.", "ordonnance_id": ordonnance.id}, status=201)

class OrdonnanceListView(ListAPIView):
    queryset = Ordonnance.objects.all()
    serializer_class = OrdonnanceSimpleSerializer
    permission_classes = [IsAuthenticatedMedecin]


