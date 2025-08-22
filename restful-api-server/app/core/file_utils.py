"""
파일 업로드 관련 유틸리티 함수
파일 저장, 검증, 삭제 등의 기능을 제공합니다.
"""

import os
import uuid
from typing import Optional, List
from fastapi import UploadFile, HTTPException, status
import aiofiles
from app.core.config import settings

# 허용되는 파일 확장자 (보안상 제한)
ALLOWED_EXTENSIONS = {
    'images': {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'},
    'documents': {'.pdf', '.doc', '.docx', '.txt', '.rtf'},
    'archives': {'.zip', '.rar', '.7z'},
    'others': {'.csv', '.xlsx', '.xls'}
}

# 모든 허용 확장자를 하나의 세트로 합치기
ALL_ALLOWED_EXTENSIONS = set()
for extensions in ALLOWED_EXTENSIONS.values():
    ALL_ALLOWED_EXTENSIONS.update(extensions)

def validate_file(file: UploadFile) -> None:
    """
    업로드된 파일의 유효성 검사
    
    Args:
        file: 업로드된 파일 객체
    
    Raises:
        HTTPException: 파일이 유효하지 않을 때
    """
    # 파일 크기 검사 (설정에서 지정한 최대 크기)
    if file.size and file.size > settings.max_file_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"파일 크기가 너무 큽니다. 최대 {settings.max_file_size // 1024 // 1024}MB까지 허용됩니다."
        )
    
    # 파일 확장자 검사
    if file.filename:
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in ALL_ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"허용되지 않는 파일 형식입니다. 허용되는 확장자: {', '.join(ALL_ALLOWED_EXTENSIONS)}"
            )

def generate_unique_filename(original_filename: str) -> str:
    """
    고유한 파일명 생성
    원본 파일명 + UUID를 사용하여 중복을 방지합니다.
    
    Args:
        original_filename: 원본 파일명
    
    Returns:
        str: 고유한 파일명
    """
    # 파일 확장자 추출
    file_extension = os.path.splitext(original_filename)[1]
    
    # UUID를 사용하여 고유한 파일명 생성
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    return unique_filename

async def save_upload_file(file: UploadFile, upload_dir: str = None) -> str:
    """
    업로드된 파일을 서버에 저장
    
    Args:
        file: 업로드된 파일 객체
        upload_dir: 파일을 저장할 디렉토리 (None이면 기본 디렉토리 사용)
    
    Returns:
        str: 저장된 파일의 경로
    """
    # 파일 유효성 검사
    validate_file(file)
    
    # 업로드 디렉토리 설정
    if upload_dir is None:
        upload_dir = settings.upload_dir
    
    # 디렉토리가 없으면 생성
    os.makedirs(upload_dir, exist_ok=True)
    
    # 고유한 파일명 생성
    unique_filename = generate_unique_filename(file.filename)
    file_path = os.path.join(upload_dir, unique_filename)
    
    try:
        # 비동기적으로 파일 저장
        async with aiofiles.open(file_path, 'wb') as f:
            # 파일을 청크 단위로 읽어서 저장 (메모리 효율성)
            while chunk := await file.read(1024 * 1024):  # 1MB씩 읽기
                await f.write(chunk)
        
        # 상대 경로 반환 (데이터베이스에 저장할 때 사용)
        relative_path = os.path.relpath(file_path, start=".")
        return relative_path
        
    except Exception as e:
        # 저장 실패 시 파일 삭제 (정리)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"파일 저장 중 오류가 발생했습니다: {str(e)}"
        )
    finally:
        # 업로드 파일 스트림 닫기
        await file.close()

def delete_file(file_path: str) -> bool:
    """
    서버에서 파일 삭제
    
    Args:
        file_path: 삭제할 파일 경로
    
    Returns:
        bool: 삭제 성공 여부
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception:
        return False

def get_file_category(filename: str) -> str:
    """
    파일 확장자로 카테고리 판별
    
    Args:
        filename: 파일명
    
    Returns:
        str: 파일 카테고리 ('images', 'documents', 'archives', 'others')
    """
    file_extension = os.path.splitext(filename)[1].lower()
    
    for category, extensions in ALLOWED_EXTENSIONS.items():
        if file_extension in extensions:
            return category
    
    return 'others'

def format_file_size(size_bytes: int) -> str:
    """
    바이트를 읽기 쉬운 형태로 변환
    
    Args:
        size_bytes: 바이트 크기
    
    Returns:
        str: 형식화된 크기 (예: "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"