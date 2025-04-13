from django.contrib import admin
from django.urls import path, include
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from myapp.sitemaps import StaticViewSitemap, BlogSitemap, ImageSitemap
from django.http import HttpResponse

sitemaps = {
    'static': StaticViewSitemap,
    'blog': BlogSitemap,
    'images': ImageSitemap,
}

# 네이버 사이트맵 생성 함수
def naver_sitemap(request):
    return HttpResponse("""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:news="http://www.google.com/schemas/sitemap-news/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml" xmlns:mobile="http://www.google.com/schemas/sitemap-mobile/1.0" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1" xmlns:video="http://www.google.com/schemas/sitemap-video/1.1" xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">
<url>
<loc>https://cvfactory.kr/</loc>
<lastmod>2024-05-15T15:30:00+09:00</lastmod>
<priority>1.0</priority>
</url>
<url>
<loc>https://cvfactory.kr/about/</loc>
<lastmod>2024-05-15T15:30:00+09:00</lastmod>
<priority>0.8</priority>
</url>
<url>
<loc>https://cvfactory.kr/privacy/</loc>
<lastmod>2024-05-15T15:30:00+09:00</lastmod>
<priority>0.7</priority>
</url>
<url>
<loc>https://cvfactory.kr/terms/</loc>
<lastmod>2024-05-15T15:30:00+09:00</lastmod>
<priority>0.7</priority>
</url>
</urlset>""", content_type='application/xml')

# 네이버 인증 파일 직접 제공 함수
def naver_verification_file(request):
    with open(settings.BASE_DIR / 'static' / 'naverfa4a8963f8244f93b2866e495ea0c431.html', 'r') as f:
        content = f.read()
    return HttpResponse(content, content_type='text/html')

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),  # API 앱의 URL 연결
    
    # SEO 관련 URL 패턴
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    path('naver-sitemap.xml', naver_sitemap, name='naver-sitemap'),
    path('rss', TemplateView.as_view(template_name='rss.xml', content_type='application/rss+xml'), name='rss'),
    
    # 네이버 인증 파일
    path('naverfa4a8963f8244f93b2866e495ea0c431.html', naver_verification_file, name='naver-verification'),
    
    # 기본 페이지들을 위한 URL 패턴
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
    path('privacy/', TemplateView.as_view(template_name='privacy.html'), name='privacy'),
    path('terms/', TemplateView.as_view(template_name='terms.html'), name='terms'),
    path('contact/', TemplateView.as_view(template_name='contact.html'), name='contact'),
    path('faq/', TemplateView.as_view(template_name='faq.html'), name='faq'),
    
    # 블로그 관련 URL 패턴
    path('blog/', TemplateView.as_view(template_name='blog/index.html'), name='blog'),
    path('blog/<slug:slug>/', TemplateView.as_view(template_name='blog/detail.html'), name='blog-detail'),
]

# 정적 파일과 미디어 파일을 제공하기 위한 설정 (개발 환경용)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
