"""
Custom validators for file uploads and data validation
"""
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
import os


def validate_image_size(image):
    """Validate image file size (max 5MB)"""
    max_size_mb = 5
    if image.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f'Image file too large. Maximum size is {max_size_mb}MB')


def validate_document_size(file):
    """Validate document file size (max 10MB)"""
    max_size_mb = 10
    if file.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f'Document file too large. Maximum size is {max_size_mb}MB')


def validate_image_extension(image):
    """Validate image file extension"""
    valid_extensions = ['jpg', 'jpeg', 'png', 'webp']
    ext = os.path.splitext(image.name)[1][1:].lower()
    if ext not in valid_extensions:
        raise ValidationError(
            f'Invalid image format. Allowed formats: {", ".join(valid_extensions)}'
        )


def validate_document_extension(file):
    """Validate document file extension"""
    valid_extensions = ['pdf', 'doc', 'docx']
    ext = os.path.splitext(file.name)[1][1:].lower()
    if ext not in valid_extensions:
        raise ValidationError(
            f'Invalid document format. Allowed formats: {", ".join(valid_extensions)}'
        )


# Combined validator for images
image_validators = [validate_image_size, validate_image_extension]
document_validators = [validate_document_size, validate_document_extension]
