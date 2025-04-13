from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from datetime import datetime

class StaticViewSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9
    protocol = 'https'

    def items(self):
        # 사이트의 정적 페이지 목록 확장
        return ['home', 'about', 'privacy', 'terms', 'contact', 'faq', 'blog']

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
        # 추후 실제 데이터베이스 연동을 위한 주석 제거 및 코드 구현
        # from blog.models import BlogPost
        # return BlogPost.objects.filter(is_published=True)
        
        # 현재는 예시로 하드코딩된 블로그 글 목록 반환
        return [
            {'slug': 'blog-post-1', 'title': '효과적인 자기소개서 작성법'},
            {'slug': 'blog-post-2', 'title': '취업 면접에서 자주 나오는 질문과 답변'},
            {'slug': 'blog-post-3', 'title': '신입 지원자를 위한 포트폴리오 작성 팁'},
            {'slug': 'blog-post-4', 'title': '취업 성공을 위한 이력서 작성 가이드'},
            {'slug': 'blog-post-5', 'title': '면접관이 중요하게 보는 자기소개서 포인트'}
        ]
    
    def location(self, item):
        # 실제 구현 시에는 블로그 포스트 객체의 get_absolute_url 사용
        # return item.get_absolute_url()
        return f'/blog/{item["slug"]}/'
    
    def lastmod(self, item):
        # 예시 날짜, 실제 구현에서는 블로그 포스트의 업데이트 날짜 사용
        dates = {
            'blog-post-1': datetime(2024, 5, 10),
            'blog-post-2': datetime(2024, 5, 5),
            'blog-post-3': datetime(2024, 4, 28),
            'blog-post-4': datetime(2024, 5, 15),
            'blog-post-5': datetime(2024, 5, 12),
        }
        return dates.get(item["slug"], datetime.now())

class ImageSitemap(Sitemap):
    """
    이미지 사이트맵 - Google 이미지 검색에 최적화
    """
    protocol = 'https'
    
    def items(self):
        # 추후 실제 데이터베이스 연동을 위한 주석 제거 및 코드 구현
        # from blog.models import BlogPost
        # return BlogPost.objects.filter(is_published=True, featured_image__isnull=False)
        
        # 현재는 예시로 하드코딩된 이미지가 있는 페이지 목록 반환
        return [
            {
                'slug': 'blog-post-1', 
                'title': '효과적인 자기소개서 작성법',
                'image_url': '/static/blog-images/effective-resume.jpg',
                'image_title': '효과적인 자기소개서 작성법',
                'image_caption': '자기소개서 작성 예시와 팁'
            },
            {
                'slug': 'blog-post-2', 
                'title': '취업 면접에서 자주 나오는 질문과 답변',
                'image_url': '/static/blog-images/interview-questions.jpg',
                'image_title': '취업 면접 질문과 답변',
                'image_caption': '면접 준비에 도움이 되는 질문 모음'
            }
        ]
    
    def location(self, item):
        # 이미지가 포함된 페이지의 URL
        return f'/blog/{item["slug"]}/'
        
    # Google 이미지 사이트맵 확장용 메서드들
    def image_location(self, item):
        # 이미지의 절대 URL
        return f'https://cvfactory.kr{item["image_url"]}'
        
    def image_title(self, item):
        # 이미지의 제목
        return item['image_title']
        
    def image_caption(self, item):
        # 이미지의 설명
        return item['image_caption'] 