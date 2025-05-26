
from django.urls import path ,include
from .views import *
from .views import GroupMembersAPIView



urlpatterns = [
   path('profile/' ,UserProfileView.as_view() , name="profile"),
   path('profile/update/' ,UpdateUserProfileView.as_view() , name="edit_profile"),
   path('groups/', GroupMembersAPIView.as_view(), name='group-list'),
   path('groups/admin/', ListAdminAPIView.as_view(), name='list-admin'),
   path('groups/medecin/', ListMedecinAPIView.as_view(), name='list-medecin'),
   path('groups/assistant-medecin/', ListAssisstantAPIView.as_view(), name='list-assistant'),
   path('groups/directeur/', ListDirecteurAPIView.as_view(), name='list-directeur'),
   path('groups/patient/', ListPatientAPIView.as_view(), name='list-patient'),
   path("registerAdmin/", RegisterAdminView.as_view(), name="registerAdmin"),

]



