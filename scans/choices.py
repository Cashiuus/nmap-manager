

# Status for Both Host and Service models
# This choices syntax is preferred style of doing it re: Two Scoops of Django
# Usage in models: choices=STATE_CHOICES
# Usage in queries: Host.objects.filter(state=Host.LIVE)
LIVE = 'up'
DOWN = 'dn'

STATE_CHOICES = (
    (LIVE, 'Live'),
    (DOWN, 'Down'),
)