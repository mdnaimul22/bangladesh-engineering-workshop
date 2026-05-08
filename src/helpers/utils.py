"""General utility functions for the BEW application."""
from src.config import Settings, setup_logger

logger = setup_logger(Settings.LOG_DIR / "helpers.log", name="bew.helpers.utils")


def parse_tags(tags_string: str) -> list[dict]:
    """Parse a comma-separated tags string into a list of dicts."""
    if not tags_string:
        return []
    return [{'type': 'tag', 'value': t.strip()} for t in tags_string.split(',') if t.strip()]


def parse_contact_info(value: str) -> dict:
    """Detect if contact info is email, website, or text."""
    if not value:
        return {'type': 'text', 'value': '-'}

    value_lower = value.lower()

    if '@' in value and any(x in value_lower for x in ['gmail', 'yahoo', 'hotmail', 'mail']):
        return {'type': 'email', 'value': value}

    if '.com' in value_lower or 'http' in value_lower or 'www.' in value_lower:
        return {'type': 'web', 'value': value}

    return {'type': 'text', 'value': value}


def is_truthy(value) -> bool:
    """Check if a form value represents a truthy boolean."""
    if not value:
        return False
    value_lower = str(value).lower().strip()
    return any(x in value_lower for x in ('true', '1', 'yes', 'on'))


def expand_designation(value: str) -> str:
    """Expand abbreviated designations to their full forms.

    Args:
        value: The raw designation string (e.g. 'pm', 'md', 'gm').

    Returns:
        The expanded designation, or the original value if no match found.
    """
    if not value:
        return ''

    mappings = {
        'pm': 'Production Manager',
        'p.m': 'Production Manager',
        'p.m.': 'Production Manager',

        'md': 'Managing Director',
        'm.d': 'Managing Director',
        'm.d.': 'Managing Director',

        'dgm': 'Deputy General Manager',
        'd.g.m': 'Deputy General Manager',
        'd.g.m.': 'Deputy General Manager',

        'gm': 'General Manager',
        'g.m': 'General Manager',
        'g.m.': 'General Manager',

        'ceo': 'Chief Executive Officer',
        'c.e.o': 'Chief Executive Officer',
        'c.e.o.': 'Chief Executive Officer',

        'cfo': 'Chief Financial Officer',
        'c.f.o': 'Chief Financial Officer',
        'c.f.o.': 'Chief Financial Officer',

        'coo': 'Chief Operating Officer',
        'c.o.o': 'Chief Operating Officer',
        'c.o.o.': 'Chief Operating Officer',

        'hr': 'Human Resources',
        'h.r': 'Human Resources',
        'h.r.': 'Human Resources',

        'agm': 'Assistant General Manager',
        'a.g.m': 'Assistant General Manager',
        'a.g.m.': 'Assistant General Manager',

        'mgr': 'Manager',
        'asst': 'Assistant',
        'sr': 'Senior',
        'jr': 'Junior',
        'exec': 'Executive',
        'dir': 'Director',
        'vp': 'Vice President',
        'v.p': 'Vice President',
        'v.p.': 'Vice President',
    }

    lower_val = value.lower().strip()
    if lower_val in mappings:
        return mappings[lower_val]

    return value
