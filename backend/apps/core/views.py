from django.http import HttpResponse


def test_view(request):
    return HttpResponse("Test response", content_type="text/plain")
