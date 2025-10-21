from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LeadViewSet, SalesOpportunityViewSet, CustomerInteractionViewSet,
    SupportTicketViewSet, TicketCommentViewSet,
    CustomerNoteViewSet, CustomerSegmentViewSet
)

router = DefaultRouter()
router.register(r'leads', LeadViewSet, basename='lead')
router.register(r'opportunities', SalesOpportunityViewSet, basename='opportunity')
router.register(r'interactions', CustomerInteractionViewSet, basename='interaction')
router.register(r'tickets', SupportTicketViewSet, basename='ticket')
router.register(r'ticket-comments', TicketCommentViewSet, basename='ticket-comment')
router.register(r'customer-notes', CustomerNoteViewSet, basename='customer-note')
router.register(r'customer-segments', CustomerSegmentViewSet, basename='customer-segment')

urlpatterns = [
    path('', include(router.urls)),
]
