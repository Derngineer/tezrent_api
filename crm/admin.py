from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import (
    Lead, CustomerInteraction, SalesOpportunity, 
    SupportTicket, TicketComment, CustomerNote, CustomerSegment
)


class CustomerInteractionInline(admin.TabularInline):
    model = CustomerInteraction
    extra = 0
    fields = ['interaction_type', 'subject', 'interaction_date', 'outcome', 'handled_by']
    readonly_fields = ['interaction_date']
    can_delete = False


class TicketCommentInline(admin.TabularInline):
    model = TicketComment
    extra = 1
    fields = ['author', 'comment', 'is_internal', 'attachment']
    readonly_fields = ['created_at']


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = [
        'full_name', 'email', 'phone_number', 'company_name',
        'source', 'status_badge', 'interest_level_badge',
        'assigned_to', 'next_follow_up', 'is_overdue_badge',
        'created_at'
    ]
    list_filter = [
        'status', 'interest_level', 'source', 
        'assigned_to', 'created_at', 'country'
    ]
    search_fields = [
        'first_name', 'last_name', 'email', 'phone_number',
        'company_name', 'notes'
    ]
    readonly_fields = [
        'created_at', 'updated_at', 'converted_at',
        'last_contacted', 'is_overdue_follow_up'
    ]
    filter_horizontal = ['interested_equipment']
    inlines = [CustomerInteractionInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                ('first_name', 'last_name'),
                ('email', 'phone_number'),
                'company_name'
            )
        }),
        ('Lead Details', {
            'fields': (
                ('source', 'status', 'interest_level'),
                'interested_category',
                'interested_equipment',
                ('estimated_budget', 'rental_duration_needed'),
                'project_description'
            )
        }),
        ('Location', {
            'fields': (('country', 'city'),)
        }),
        ('Assignment & Follow-up', {
            'fields': (
                'assigned_to',
                ('next_follow_up', 'last_contacted'),
                'is_overdue_follow_up'
            )
        }),
        ('Conversion', {
            'fields': (
                'converted_to_customer',
                'converted_at'
            ),
            'classes': ('collapse',)
        }),
        ('Loss Tracking', {
            'fields': (
                'lost_reason',
                'competitor_name'
            ),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        })
    )
    
    actions = ['mark_as_contacted', 'mark_as_qualified', 'assign_to_me']
    
    def status_badge(self, obj):
        colors = {
            'new': '#3498db',
            'contacted': '#9b59b6',
            'qualified': '#f39c12',
            'proposal_sent': '#e67e22',
            'negotiation': '#d35400',
            'converted': '#27ae60',
            'lost': '#95a5a6',
            'unqualified': '#7f8c8d',
        }
        color = colors.get(obj.status, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def interest_level_badge(self, obj):
        colors = {'hot': '#e74c3c', 'warm': '#f39c12', 'cold': '#3498db'}
        color = colors.get(obj.interest_level, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, obj.get_interest_level_display()
        )
    interest_level_badge.short_description = 'Interest'
    
    def is_overdue_badge(self, obj):
        if obj.is_overdue_follow_up:
            return format_html('<span style="color: red;">⚠ Overdue</span>')
        return ''
    is_overdue_badge.short_description = 'Follow-up Status'
    
    def mark_as_contacted(self, request, queryset):
        queryset.update(status='contacted', last_contacted=timezone.now())
    mark_as_contacted.short_description = "Mark selected as contacted"
    
    def mark_as_qualified(self, request, queryset):
        queryset.update(status='qualified')
    mark_as_qualified.short_description = "Mark selected as qualified"
    
    def assign_to_me(self, request, queryset):
        queryset.update(assigned_to=request.user)
    assign_to_me.short_description = "Assign selected to me"


@admin.register(CustomerInteraction)
class CustomerInteractionAdmin(admin.ModelAdmin):
    list_display = [
        'interaction_date', 'interaction_type', 'subject',
        'contact_name', 'handled_by', 'outcome',
        'requires_follow_up', 'follow_up_date'
    ]
    list_filter = [
        'interaction_type', 'outcome', 'requires_follow_up',
        'interaction_date', 'handled_by'
    ]
    search_fields = [
        'subject', 'description',
        'lead__first_name', 'lead__last_name',
        'customer__user__email', 'company__company_name'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Contact Information', {
            'fields': (
                'lead',
                'customer',
                'company'
            )
        }),
        ('Interaction Details', {
            'fields': (
                ('interaction_type', 'interaction_date'),
                'subject',
                'description',
                ('outcome', 'duration_minutes')
            )
        }),
        ('Staff Assignment', {
            'fields': ('handled_by',)
        }),
        ('Follow-up', {
            'fields': (
                'requires_follow_up',
                'follow_up_date',
                'follow_up_completed'
            )
        }),
        ('Attachment', {
            'fields': ('attachment',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def contact_name(self, obj):
        if obj.lead:
            return obj.lead.full_name
        elif obj.customer:
            return obj.customer.user.get_full_name() or obj.customer.user.email
        elif obj.company:
            return obj.company.company_name
        return "N/A"
    contact_name.short_description = 'Contact'


@admin.register(SalesOpportunity)
class SalesOpportunityAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'contact_name', 'stage_badge',
        'probability', 'estimated_value', 'weighted_value',
        'expected_close_date', 'is_overdue_badge', 'assigned_to'
    ]
    list_filter = [
        'stage', 'probability', 'assigned_to',
        'expected_close_date', 'created_at'
    ]
    search_fields = [
        'name', 'description',
        'lead__first_name', 'lead__last_name',
        'customer__user__email', 'company__company_name'
    ]
    readonly_fields = [
        'created_at', 'updated_at', 'weighted_value',
        'actual_close_date', 'is_overdue'
    ]
    filter_horizontal = ['equipment_items']
    
    fieldsets = (
        ('Opportunity Information', {
            'fields': (
                'name',
                'description'
            )
        }),
        ('Related Entities', {
            'fields': (
                'lead',
                'customer',
                'company'
            )
        }),
        ('Rental Details', {
            'fields': (
                'equipment_items',
                'estimated_value',
                ('rental_start_date', 'rental_end_date'),
                'rental_duration_months'
            )
        }),
        ('Sales Progress', {
            'fields': (
                ('stage', 'probability'),
                'assigned_to',
                ('expected_close_date', 'actual_close_date'),
                ('weighted_value', 'is_overdue')
            )
        }),
        ('Outcome', {
            'fields': (
                'won_rental',
                'lost_reason',
                'competitor_name'
            ),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['move_to_proposal', 'move_to_negotiation']
    
    def contact_name(self, obj):
        if obj.lead:
            return obj.lead.full_name
        elif obj.customer:
            return obj.customer.user.get_full_name() or obj.customer.user.email
        elif obj.company:
            return obj.company.company_name
        return "N/A"
    contact_name.short_description = 'Contact'
    
    def stage_badge(self, obj):
        colors = {
            'prospecting': '#95a5a6',
            'qualification': '#3498db',
            'needs_analysis': '#9b59b6',
            'proposal': '#f39c12',
            'negotiation': '#e67e22',
            'closed_won': '#27ae60',
            'closed_lost': '#e74c3c',
        }
        color = colors.get(obj.stage, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, obj.get_stage_display()
        )
    stage_badge.short_description = 'Stage'
    
    def is_overdue_badge(self, obj):
        if obj.is_overdue:
            return format_html('<span style="color: red;">⚠ Overdue</span>')
        return ''
    is_overdue_badge.short_description = 'Status'
    
    def move_to_proposal(self, request, queryset):
        queryset.update(stage='proposal', probability=75)
    move_to_proposal.short_description = "Move to Proposal stage"
    
    def move_to_negotiation(self, request, queryset):
        queryset.update(stage='negotiation', probability=90)
    move_to_negotiation.short_description = "Move to Negotiation stage"


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = [
        'ticket_number', 'subject', 'category',
        'priority_badge', 'status_badge', 'contact_info',
        'assigned_to', 'is_overdue_badge', 'created_at'
    ]
    list_filter = [
        'status', 'priority', 'category',
        'assigned_to', 'created_at'
    ]
    search_fields = [
        'ticket_number', 'subject', 'description',
        'contact_email', 'customer__user__email',
        'company__company_name'
    ]
    readonly_fields = [
        'ticket_number', 'created_at', 'updated_at',
        'resolved_at', 'closed_at', 'first_response_at',
        'response_time', 'resolution_time', 'is_overdue'
    ]
    inlines = [TicketCommentInline]
    
    fieldsets = (
        ('Ticket Information', {
            'fields': (
                'ticket_number',
                ('subject', 'category'),
                'description',
                ('priority', 'status')
            )
        }),
        ('Customer Information', {
            'fields': (
                'customer',
                'company',
                ('contact_email', 'contact_phone')
            )
        }),
        ('Related Objects', {
            'fields': (
                'related_rental',
                'related_equipment'
            )
        }),
        ('Assignment', {
            'fields': ('assigned_to',)
        }),
        ('Resolution', {
            'fields': (
                'resolution',
                ('resolved_at', 'resolved_by')
            )
        }),
        ('Customer Feedback', {
            'fields': (
                'customer_rating',
                'customer_feedback'
            ),
            'classes': ('collapse',)
        }),
        ('SLA Tracking', {
            'fields': (
                ('response_due', 'first_response_at', 'response_time'),
                ('resolution_due', 'resolution_time'),
                'is_overdue'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
                'closed_at'
            ),
            'classes': ('collapse',)
        })
    )
    
    actions = ['assign_to_me', 'mark_in_progress', 'mark_resolved']
    
    def contact_info(self, obj):
        if obj.customer:
            return obj.customer.user.email
        elif obj.company:
            return obj.company.company_name
        return obj.contact_email
    contact_info.short_description = 'Contact'
    
    def priority_badge(self, obj):
        colors = {
            'low': '#95a5a6',
            'medium': '#3498db',
            'high': '#f39c12',
            'urgent': '#e74c3c',
        }
        color = colors.get(obj.priority, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, obj.get_priority_display()
        )
    priority_badge.short_description = 'Priority'
    
    def status_badge(self, obj):
        colors = {
            'open': '#3498db',
            'in_progress': '#f39c12',
            'waiting_customer': '#9b59b6',
            'waiting_internal': '#e67e22',
            'resolved': '#27ae60',
            'closed': '#95a5a6',
            'reopened': '#e74c3c',
        }
        color = colors.get(obj.status, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def is_overdue_badge(self, obj):
        if obj.is_overdue:
            return format_html('<span style="color: red;">⚠ Overdue</span>')
        return ''
    is_overdue_badge.short_description = 'SLA Status'
    
    def assign_to_me(self, request, queryset):
        queryset.update(assigned_to=request.user)
    assign_to_me.short_description = "Assign selected to me"
    
    def mark_in_progress(self, request, queryset):
        queryset.update(status='in_progress')
    mark_in_progress.short_description = "Mark as In Progress"
    
    def mark_resolved(self, request, queryset):
        queryset.update(status='resolved', resolved_at=timezone.now(), resolved_by=request.user)
    mark_resolved.short_description = "Mark as Resolved"


@admin.register(TicketComment)
class TicketCommentAdmin(admin.ModelAdmin):
    list_display = [
        'ticket', 'author', 'comment_preview',
        'is_internal', 'created_at'
    ]
    list_filter = ['is_internal', 'created_at', 'author']
    search_fields = ['ticket__ticket_number', 'comment']
    readonly_fields = ['created_at', 'updated_at']
    
    def comment_preview(self, obj):
        return obj.comment[:100] + '...' if len(obj.comment) > 100 else obj.comment
    comment_preview.short_description = 'Comment'


@admin.register(CustomerNote)
class CustomerNoteAdmin(admin.ModelAdmin):
    list_display = [
        'subject', 'note_type', 'entity_name',
        'is_important', 'created_by', 'created_at'
    ]
    list_filter = [
        'note_type', 'is_important', 'created_by', 'created_at'
    ]
    search_fields = [
        'subject', 'content',
        'customer__user__email', 'company__company_name'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Entity', {
            'fields': (
                'customer',
                'company'
            )
        }),
        ('Note Details', {
            'fields': (
                'note_type',
                'subject',
                'content',
                'is_important'
            )
        }),
        ('Metadata', {
            'fields': (
                'created_by',
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        })
    )
    
    def entity_name(self, obj):
        if obj.customer:
            return f"Customer: {obj.customer.user.email}"
        elif obj.company:
            return f"Company: {obj.company.company_name}"
        return "N/A"
    entity_name.short_description = 'Related To'


@admin.register(CustomerSegment)
class CustomerSegmentAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'total_customers', 'is_active', 'created_at'
    ]
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    filter_horizontal = ['preferred_categories', 'customers', 'companies']
    readonly_fields = ['created_at', 'updated_at', 'total_customers']
    
    fieldsets = (
        ('Segment Information', {
            'fields': (
                'name',
                'description',
                'is_active'
            )
        }),
        ('Criteria', {
            'fields': (
                ('min_rental_count', 'min_total_spent'),
                'preferred_categories'
            )
        }),
        ('Members', {
            'fields': (
                'customers',
                'companies',
                'total_customers'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
