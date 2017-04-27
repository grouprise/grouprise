from core import signals


connections = [
    signals.include('features.articles.signals'),
    signals.include('features.events.signals'),
    signals.include('features.galleries.signals'),
    signals.include('features.groups.signals'),
    signals.include('features.memberships.signals'),
]
