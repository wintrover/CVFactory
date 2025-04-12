from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from datetime import datetime

class StaticViewSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9
    protocol = 'https'

    def items(self):
        return ['home', 'about', 'privacy', 'terms']  # 사이트의 정적 페이지 목록

    def location(self, item):
        return reverse(item)
    
    def lastmod(self, item):
        return datetime.now()  # 마지막 수정일 