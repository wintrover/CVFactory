from django.db import models

class Resume(models.Model):
    recruitment_notice_url = models.URLField(verbose_name="채용공고 URL")
    target_company_url = models.URLField(verbose_name="회사 URL", blank=True, null=True)
    job_description = models.TextField(verbose_name="채용공고 내용")
    company_info = models.TextField(verbose_name="회사 정보", blank=True, null=True)
    user_story = models.TextField(verbose_name="사용자 자기소개")
    generated_resume = models.TextField(verbose_name="생성된 자기소개서", max_length=10000)  # 최대 길이 10000자로 증가
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성 시간")
  
    def __str__(self):
        return f"Resume {self.id} - {self.recruitment_notice_url}"
