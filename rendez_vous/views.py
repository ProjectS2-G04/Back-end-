from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .models import DemandeRendezVous
from .serializers import DemandeRendezVousSerializer
from datetime import datetime

class CreateDemandeRendezVousView(generics.CreateAPIView):
    queryset = DemandeRendezVous.objects.all()
    serializer_class = DemandeRendezVousSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)

    def create(self, request, *args, **kwargs):
        if request.user.role != "PATIENT":
            return Response(
                {
                    "error": "Seuls les patients peuvent créer une demande de rendez-vous."
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().create(request, *args, **kwargs)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def confirmer_demande(request, demande_id):
    if not is_medecin_or_assistant(request.user):
        return Response(
            {
                "error": "Seuls les médecins ou assistants peuvent confirmer une demande."
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        demande = DemandeRendezVous.objects.get(id=demande_id)
    except DemandeRendezVous.DoesNotExist:
        return Response(
            {"error": "Aucune demande avec cet ID n'existe."},
            status=status.HTTP_404_NOT_FOUND,
        )

    demande.statut = "confirmee"
    demande.save()
    return Response(
        {"success": "Demande confirmée avec succès."}, status=status.HTTP_200_OK
    )


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def annuler_demande(request, demande_id):
    if not is_medecin_or_assistant(request.user):
        return Response(
            {"error": "Seuls les médecins ou assistants peuvent annuler une demande."},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        demande = DemandeRendezVous.objects.get(id=demande_id)
    except DemandeRendezVous.DoesNotExist:
        return Response(
            {"error": "Demande introuvable."}, status=status.HTTP_404_NOT_FOUND
        )

    demande.statut = "annulee"
    demande.save()
    return Response(
        {"success": "Demande annulée avec succès."}, status=status.HTTP_200_OK
    )


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def reporter_demande(request, demande_id):
    if not is_medecin_or_assistant(request.user):
        return Response(
            {"error": "Seuls les médecins ou assistants peuvent reporter une demande."},
            status=status.HTTP_403_FORBIDDEN,
        )

    nouvelle_date = request.data.get("nouvelle_date")

    if not nouvelle_date:
        return Response(
            {"error": "La nouvelle date est requise."},
            status=status.HTTP_400_BAD_REQUEST,
        )
        
    try:
        datetime.strptime(nouvelle_date, "%Y-%m-%d")
    except ValueError:
        return Response(
            {"error": "Format de date invalide. Utilisez 'YYYY-MM-DD."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        demande = DemandeRendezVous.objects.get(id=demande_id)
    except DemandeRendezVous.DoesNotExist:
        return Response(
            {"error": "Demande non trouvée."}, status=status.HTTP_404_NOT_FOUND
        )

    demande.date_demandee = nouvelle_date
    demande.statut = "reportee"
    demande.save()
    return Response(
        {"success": f"Demande reportée à {nouvelle_date}."}, status=status.HTTP_200_OK
    )

def is_medecin_or_assistant(user):
    return user.role in ["DOCTOR", "ASSISTANT"]