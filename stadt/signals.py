from core import signals


connections = [
    signals.include('features.groups.signals'),
    signals.include('features.memberships.signals'),
]
