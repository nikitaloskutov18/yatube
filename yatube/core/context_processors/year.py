from datetime import datetime


def year(request):
    dt_now = datetime.now().year
    return {
        'year': dt_now
    }
