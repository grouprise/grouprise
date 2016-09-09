from core import signals


connections = [
    signals.include('features.articles.signals'),
    signals.include('features.conversations.signals'),
    signals.include('features.events.signals'),
    signals.include('features.galleries.signals'),
]
