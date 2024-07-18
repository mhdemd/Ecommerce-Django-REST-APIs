import os

from django.conf import settings
from django.http import FileResponse


def download_cv(request):
    file_path = os.path.join(
        settings.BASE_DIR, "portfolio", "static", "cv", "Resume-Mehdi-Emadi.pdf"
    )

    response = FileResponse(open(file_path, "rb"), content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="Resume-Mehdi-Emadi.pdf"'

    return response
