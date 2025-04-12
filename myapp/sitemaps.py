from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from datetime import datetime

class StaticViewSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9
    protocol = 'https'

    def items(self):
        return ['home', 'about', 'privacy', 'terms', 'contact', 'faq', 'blog']  # 사이트의 정적 페이지 목록 확장

    def location(self, item):
        return reverse(item)
    
    def lastmod(self, item):
        # 페이지별로 다른 최종 수정일 반환
        if item == 'home':
            return datetime.now()  # 홈페이지는 항상 최신으로 표시
        elif item in ['blog', 'faq']:
            return datetime(2024, 5, 1)  # 블로그, FAQ는 최근 업데이트 날짜
        else:
            return datetime(2024, 4, 1)  # 나머지 정적 페이지

class BlogSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8
    protocol = 'https'
    
    def items(self):
        # 여기서는 예시로 하드코딩된 블로그 글 ID를 사용
        # 실제로는 Blog 모델에서 가져올 수 있음
        # from blog.models import BlogPost
        # return BlogPost.objects.filter(is_published=True)
        return ['blog-post-1', 'blog-post-2', 'blog-post-3']
    
    def location(self, item):
        # 실제 구현 시에는 블로그 포스트 객체의 get_absolute_url 사용
        return f'/blog/{item}/'
    
    def lastmod(self, item):
        # 예시 날짜, 실제 구현에서는 블로그 포스트의 업데이트 날짜 사용
        dates = {
            'blog-post-1': datetime(2024, 5, 10),
            'blog-post-2': datetime(2024, 5, 5),
            'blog-post-3': datetime(2024, 4, 28),
        }
        return dates.get(item, datetime.now()) 