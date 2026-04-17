"""Context processors untuk inject school info ke semua templates"""

from academic.models import School


def school_context(request):
    """Add school information to template context"""
    try:
        # Get the first active school
        school = School.objects.filter(is_active=True).first()
        if not school:
            # Fallback to any school if no active one found
            school = School.objects.first()
    except Exception:
        school = None
    
    return {
        'school': school,
    }
