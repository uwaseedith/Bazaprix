
import time
import logging

logger = logging.getLogger(__name__)

class TimingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        duration = (time.time() - start_time) * 1000  # milliseconds
        logger.info(f"Request {request.path} took {duration:.2f} ms")
        return response
