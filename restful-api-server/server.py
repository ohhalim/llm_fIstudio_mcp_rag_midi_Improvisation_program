"""
서버 시작 스크립트
개발 및 운영 환경에서 서버를 시작하기 위한 진입점입니다.
"""

import uvicorn
from app.main import app
from app.core.config import settings

if __name__ == "__main__":
    print("🚀 RESTful API 서버를 시작합니다...")
    print(f"📍 서버 주소: http://{settings.host}:{settings.port}")
    print(f"📖 API 문서: http://{settings.host}:{settings.port}/docs")
    print("=" * 50)
    
    # 서버 실행
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info" if settings.debug else "warning",
        access_log=settings.debug
    )


# import uvicorn 
# from app.main import app₩
# from app.core.config import settings

# if __name__ == "__main__":
#     '''
#     파이썬 스크립트가 직접실행될때만 아래의 코드를 샐행하라 
#     ''' 
#     print("🚀 RESTful API 서버를 시작합니다...")

#     uvicorn.run(
#         app,
#         host=settings.host,
#         port=settings.port,
#         reload=settings.debug,
#         log_level="info" if settings.debug else "warning",
#         access_log=settings.debug
#     )

# # server.py를 실행했을떄 settings에 정의 된 호스트와 포트등의 설정을 바탕르ㅗ uvicorn을 사용하여 app 실행