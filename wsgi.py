"""Production WSGI entry point.

gevent must monkey-patch the standard library (socket, ssl, threading, ...)
BEFORE anything imports them - notably the Anthropic SDK's HTTPS client. If the
patch runs afterwards (the default when gunicorn loads ``app:app`` directly),
the single gevent worker blocks on outbound SSL reads during long Stage runs,
its heartbeat stalls, and gunicorn kills it with WORKER TIMEOUT / SIGKILL.
Importing the Flask app through this module guarantees the patch runs first.

Start with: gunicorn wsgi:app --worker-class gevent ...
"""
from gevent import monkey

monkey.patch_all()

from app import app  # noqa: E402  (must import the app AFTER monkey.patch_all)

__all__ = ["app"]
