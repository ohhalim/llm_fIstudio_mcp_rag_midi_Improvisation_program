"""
모델 패키지 초기화 파일
모든 데이터베이스 모델을 한 곳에서 import할 수 있도록 합니다.
"""

from .user import User
from .post import Post

# 모든 모델을 외부에서 쉽게 import할 수 있도록 __all__ 정의
__all__ = ["User", "Post"]