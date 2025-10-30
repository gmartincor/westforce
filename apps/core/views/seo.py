from django.http import HttpResponse
from django.views.decorators.http import require_GET


@require_GET
def robots_txt(request):
    lines = [
        "User-agent: *",
        "Allow: /",
        f"Sitemap: {request.scheme}://{request.get_host()}/sitemap.xml",
        "",
        "User-agent: Googlebot",
        "Allow: /",
        "",
        "User-agent: Googlebot-Image",
        "Allow: /",
        "",
        "Disallow: /admin/",
        "Disallow: /static/admin/",
        "Disallow: /media/private/",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")
