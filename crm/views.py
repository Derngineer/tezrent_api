from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q

from .models import (
    Lead, CustomerInteraction, SalesOpportunity,
    SupportTicket, TicketComment, CustomerNote, CustomerSegment
)
from .serializers import (
    LeadSerializer, LeadCreateSerializer, LeadMobileSerializer,
    SalesOpportunitySerializer, SalesOpportunityCreateSerializer,
    CustomerInteractionSerializer,
    SupportTicketSerializer, SupportTicketCreateSerializer, SupportTicketCustomerSerializer,
    TicketCommentSerializer, TicketMobileSerializer,
    CustomerNoteSerializer,
    CustomerSegmentSerializer
)
from .permissions import (
    IsStaffUser, IsSellerOwner, IsCustomerOwner,
    IsStaffOrSellerOwner, IsStaffOrCustomerOwner,
    CanCreateLead, CanCreateTicket
)


class LeadViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing leads.
    Staff: Full access to all leads
    Sellers: Can view and manage leads for their company
    """
    queryset = Lead.objects.all()
    permission_classes = [IsAuthenticated, IsStaffOrSellerOwner]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return LeadCreateSerializer
        elif self.request.GET.get('mobile') == 'true':
            return LeadMobileSerializer
        return LeadSerializer
    
    def get_queryset(self):
        # select only valid related fields present on Lead model
        queryset = Lead.objects.select_related(
            'assigned_to', 'interested_category', 'converted_to_customer'
        )
        
        # Filter by company for sellers
        if not self.request.user.is_staff and hasattr(self.request.user, 'company_profile'):
            queryset = queryset.filter(company=self.request.user.company_profile)
        
        # Filters
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        source_filter = self.request.query_params.get('source')
        if source_filter:
            queryset = queryset.filter(source=source_filter)
        
        assigned_to_me = self.request.query_params.get('assigned_to_me')
        if assigned_to_me == 'true':
            queryset = queryset.filter(assigned_to=self.request.user)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_contacted(self, request, pk=None):
        """Mark lead as contacted"""
        lead = self.get_object()
        lead.mark_contacted()
        return Response({'status': 'Lead marked as contacted'})
    
    @action(detail=True, methods=['post'])
    def convert_to_opportunity(self, request, pk=None):
        """Convert qualified lead to opportunity"""
        lead = self.get_object()
        
        if lead.status != 'qualified':
            return Response(
                {'error': 'Only qualified leads can be converted'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            opportunity = lead.convert_to_opportunity()
            return Response({
                'status': 'Lead converted to opportunity',
                'opportunity_id': opportunity.id
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def my_leads(self, request):
        """Get leads assigned to current user"""
        leads = self.get_queryset().filter(assigned_to=request.user)
        serializer = self.get_serializer(leads, many=True)
        return Response(serializer.data)


class SalesOpportunityViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing sales opportunities.
    Staff: Full access
    Sellers: Can view opportunities for their company
    """
    queryset = SalesOpportunity.objects.all()
    permission_classes = [IsAuthenticated, IsStaffOrSellerOwner]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SalesOpportunityCreateSerializer
        return SalesOpportunitySerializer
    
    def get_queryset(self):
        # equipment is a M2M (equipment_items) so prefetch it; created_by not defined
        queryset = SalesOpportunity.objects.select_related(
            'lead', 'company', 'customer', 'assigned_to', 'won_rental'
        ).prefetch_related('equipment_items')
        
        # Filter by company for sellers
        if not self.request.user.is_staff and hasattr(self.request.user, 'company_profile'):
            queryset = queryset.filter(company=self.request.user.company_profile)
        
        # Filters
        stage_filter = self.request.query_params.get('stage')
        if stage_filter:
            queryset = queryset.filter(stage=stage_filter)
        
        assigned_to_me = self.request.query_params.get('assigned_to_me')
        if assigned_to_me == 'true':
            queryset = queryset.filter(assigned_to=self.request.user)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_won(self, request, pk=None):
        """Mark opportunity as won"""
        opportunity = self.get_object()
        actual_amount = request.data.get('actual_amount')
        opportunity.mark_won(actual_amount=actual_amount)
        return Response({'status': 'Opportunity marked as won'})
    
    @action(detail=True, methods=['post'])
    def mark_lost(self, request, pk=None):
        """Mark opportunity as lost"""
        opportunity = self.get_object()
        reason = request.data.get('reason', '')
        opportunity.mark_lost(reason=reason)
        return Response({'status': 'Opportunity marked as lost'})
    
    @action(detail=False, methods=['get'])
    def pipeline(self, request):
        """Get pipeline summary"""
        queryset = self.get_queryset()
        
        pipeline_data = {}
        stages = ['prospecting', 'qualification', 'proposal', 'negotiation', 'closed_won', 'closed_lost']
        
        for stage in stages:
            opportunities = queryset.filter(stage=stage)
            pipeline_data[stage] = {
                'count': opportunities.count(),
                'total_value': sum(opp.estimated_amount for opp in opportunities),
                'weighted_value': sum(opp.weighted_value for opp in opportunities)
            }
        
        return Response(pipeline_data)


class CustomerInteractionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing customer interactions/activities.
    Staff: Full access
    Sellers: Can view interactions related to their leads/opportunities
    """
    queryset = CustomerInteraction.objects.all()
    serializer_class = CustomerInteractionSerializer
    permission_classes = [IsAuthenticated, IsStaffUser]
    
    def get_queryset(self):
        # map to actual model FK names: lead, customer, company, handled_by
        queryset = CustomerInteraction.objects.select_related(
            'lead', 'customer', 'company', 'handled_by'
        )
        
        # Filter by lead
        lead_id = self.request.query_params.get('lead_id')
        if lead_id:
            queryset = queryset.filter(related_to_lead_id=lead_id)
        
        # Filter by opportunity
        opportunity_id = self.request.query_params.get('opportunity_id')
        if opportunity_id:
            queryset = queryset.filter(related_to_opportunity_id=opportunity_id)
        
        # Filter by customer
        customer_id = self.request.query_params.get('customer_id')
        if customer_id:
            queryset = queryset.filter(related_to_customer_id=customer_id)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(performed_by=self.request.user)


class SupportTicketViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing support tickets.
    Staff: Full access
    Sellers: Can view tickets related to their rentals
    Customers: Can view and create their own tickets
    """
    queryset = SupportTicket.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        # Customers get limited serializer (no internal notes)
        if not self.request.user.is_staff and hasattr(self.request.user, 'customer_profile'):
            return SupportTicketCustomerSerializer
        
        if self.action in ['create', 'update', 'partial_update']:
            return SupportTicketCreateSerializer
        
        if self.request.GET.get('mobile') == 'true':
            return TicketMobileSerializer
        
        return SupportTicketSerializer
    
    def get_queryset(self):
        # created_by not present on SupportTicket; use resolved_by where appropriate
        queryset = SupportTicket.objects.select_related(
            'customer__user', 'company', 'related_rental',
            'related_equipment', 'assigned_to', 'resolved_by'
        ).prefetch_related('comments')
        
        # Customers can only see their own tickets
        if not self.request.user.is_staff and hasattr(self.request.user, 'customer_profile'):
            queryset = queryset.filter(customer=self.request.user.customer_profile)
        
        # Sellers can see tickets related to their company
        elif not self.request.user.is_staff and hasattr(self.request.user, 'company_profile'):
            queryset = queryset.filter(company=self.request.user.company_profile)
        
        # Filters
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        priority_filter = self.request.query_params.get('priority')
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
        
        category_filter = self.request.query_params.get('category')
        if category_filter:
            queryset = queryset.filter(category=category_filter)
        
        assigned_to_me = self.request.query_params.get('assigned_to_me')
        if assigned_to_me == 'true':
            queryset = queryset.filter(assigned_to=self.request.user)
        
        return queryset
    
    def perform_create(self, serializer):
        # Auto-assign customer if creating from customer account
        customer = None
        if hasattr(self.request.user, 'customer_profile'):
            customer = self.request.user.customer_profile
        
        serializer.save(
            created_by=self.request.user,
            customer=customer or serializer.validated_data.get('customer')
        )
    
    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        """Add a comment to the ticket"""
        ticket = self.get_object()
        
        comment_text = request.data.get('comment')
        is_internal = request.data.get('is_internal', False)
        attachment = request.data.get('attachment')
        
        # Customers cannot add internal comments
        if not request.user.is_staff and is_internal:
            is_internal = False
        
        comment = TicketComment.objects.create(
            ticket=ticket,
            comment=comment_text,
            is_internal=is_internal,
            attachment=attachment,
            created_by=request.user
        )
        
        serializer = TicketCommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def mark_resolved(self, request, pk=None):
        """Mark ticket as resolved"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Only staff can mark tickets as resolved'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        ticket = self.get_object()
        resolution_text = request.data.get('resolution', '')
        ticket.mark_resolved(resolution_text=resolution_text)
        return Response({'status': 'Ticket marked as resolved'})
    
    @action(detail=True, methods=['post'])
    def mark_closed(self, request, pk=None):
        """Mark ticket as closed"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Only staff can close tickets'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        ticket = self.get_object()
        ticket.mark_closed()
        return Response({'status': 'Ticket marked as closed'})
    
    @action(detail=False, methods=['get'])
    def my_tickets(self, request):
        """Get tickets for current user (customer view)"""
        if hasattr(request.user, 'customer_profile'):
            tickets = self.get_queryset().filter(customer=request.user.customer_profile)
            serializer = self.get_serializer(tickets, many=True)
            return Response(serializer.data)
        
        return Response({'error': 'Not a customer account'}, status=status.HTTP_400_BAD_REQUEST)


class TicketCommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing ticket comments.
    """
    queryset = TicketComment.objects.all()
    serializer_class = TicketCommentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # TicketComment uses `author` FK (not created_by)
        queryset = TicketComment.objects.select_related(
            'ticket', 'author'
        )
        
        # Filter by ticket
        ticket_id = self.request.query_params.get('ticket_id')
        if ticket_id:
            queryset = queryset.filter(ticket_id=ticket_id)
            
            # Customers can't see internal comments
            if not self.request.user.is_staff and hasattr(self.request.user, 'customer_profile'):
                queryset = queryset.filter(is_internal=False)
        
        return queryset
    
    def perform_create(self, serializer):
        # Customers cannot add internal comments
        is_internal = serializer.validated_data.get('is_internal', False)
        if not self.request.user.is_staff and is_internal:
            is_internal = False
        
        serializer.save(
            created_by=self.request.user,
            is_internal=is_internal
        )


class CustomerNoteViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing customer notes.
    Staff: Full access
    Sellers: Can add notes for customers who rented from them
    """
    queryset = CustomerNote.objects.all()
    serializer_class = CustomerNoteSerializer
    permission_classes = [IsAuthenticated, IsStaffOrSellerOwner]
    
    def get_queryset(self):
        queryset = CustomerNote.objects.select_related(
            'customer__user', 'created_by', 'company'
        )
        
        # Filter by company for sellers
        if not self.request.user.is_staff and hasattr(self.request.user, 'company_profile'):
            queryset = queryset.filter(company=self.request.user.company_profile)
        
        # Filter by customer
        customer_id = self.request.query_params.get('customer_id')
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)
        
        # Filter important notes
        important_only = self.request.query_params.get('important')
        if important_only == 'true':
            queryset = queryset.filter(is_important=True)
        
        return queryset
    
    def perform_create(self, serializer):
        # Auto-assign company if creating from seller account
        company = None
        if hasattr(self.request.user, 'company_profile'):
            company = self.request.user.company_profile
        
        serializer.save(
            created_by=self.request.user,
            company=company or serializer.validated_data.get('company')
        )


class CustomerSegmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing customer segments.
    Staff only.
    """
    queryset = CustomerSegment.objects.all()
    serializer_class = CustomerSegmentSerializer
    permission_classes = [IsAuthenticated, IsStaffUser]
    
    def get_queryset(self):
        return CustomerSegment.objects.prefetch_related('customers__user')
