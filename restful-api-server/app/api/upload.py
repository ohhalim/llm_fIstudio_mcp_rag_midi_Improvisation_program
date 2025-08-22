"""
파일 업로드 관련 API 엔드포인트
파일 업로드, 다운로드, 삭제 기능을 제공합니다.
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os

from app.db.database import get_db
from app.core.deps import get_current_active_user
from app.core.file_utils import save_upload_file, delete_file, get_file_category, format_file_size
from app.models.user import User
from app.schemas.post import PostCreate, PostResponse
from app.crud import post as post_crud

# 파일 업로드 관련 라우터
router = APIRouter(
    prefix="/files",
    tags=["파일 관리"]
)

class FileUploadResponse:
    """파일 업로드 응답 모델"""
    def __init__(self, filename: str, file_path: str, file_size: int, category: str):
        self.filename = filename
        self.file_path = file_path
        self.file_size = file_size
        self.file_size_formatted = format_file_size(file_size)
        self.category = category

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(..., description="업로드할 파일"),
    current_user: User = Depends(get_current_active_user)
):
    """
    단일 파일 업로드
    
    JWT 토큰이 필요합니다.
    최대 10MB까지 업로드 가능하며, 이미지, 문서, 아카이브 파일을 지원합니다.
    
    Args:
        file: 업로드할 파일
        current_user: 현재 로그인한 사용자
    
    Returns:
        dict: 업로드된 파일 정보
    """
    # 파일 저장
    file_path = await save_upload_file(file)
    
    # 파일 정보 반환
    file_info = FileUploadResponse(
        filename=file.filename,
        file_path=file_path,
        file_size=file.size,
        category=get_file_category(file.filename)
    )
    
    return {
        "message": "파일이 성공적으로 업로드되었습니다.",
        "file": {
            "filename": file_info.filename,
            "file_path": file_info.file_path,
            "file_size": file_info.file_size,
            "file_size_formatted": file_info.file_size_formatted,
            "category": file_info.category
        }
    }

@router.post("/upload-multiple", status_code=status.HTTP_201_CREATED)
async def upload_multiple_files(
    files: List[UploadFile] = File(..., description="업로드할 파일들 (최대 5개)"),
    current_user: User = Depends(get_current_active_user)
):
    """
    다중 파일 업로드
    
    한 번에 최대 5개 파일까지 업로드 가능합니다.
    
    Args:
        files: 업로드할 파일 리스트
        current_user: 현재 로그인한 사용자
    
    Returns:
        dict: 업로드된 파일들의 정보
    """
    # 파일 개수 제한 (5개)
    if len(files) > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="한 번에 최대 5개 파일까지만 업로드할 수 있습니다."
        )
    
    uploaded_files = []
    failed_files = []
    
    for file in files:
        try:
            # 각 파일 저장
            file_path = await save_upload_file(file)
            
            file_info = {
                "filename": file.filename,
                "file_path": file_path,
                "file_size": file.size,
                "file_size_formatted": format_file_size(file.size),
                "category": get_file_category(file.filename)
            }
            
            uploaded_files.append(file_info)
            
        except Exception as e:
            failed_files.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    return {
        "message": f"{len(uploaded_files)}개 파일이 성공적으로 업로드되었습니다.",
        "uploaded_files": uploaded_files,
        "failed_files": failed_files
    }

@router.post("/upload-with-post", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post_with_file(
    title: str,
    content: str,
    file: Optional[UploadFile] = File(None, description="게시글에 첨부할 파일 (선택사항)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    파일과 함께 게시글 작성
    
    게시글을 작성하면서 동시에 파일을 첨부할 수 있습니다.
    
    Args:
        title: 게시글 제목
        content: 게시글 내용
        file: 첨부파일 (선택사항)
        db: 데이터베이스 세션
        current_user: 현재 로그인한 사용자
    
    Returns:
        PostResponse: 생성된 게시글 정보
    """
    file_path = None
    
    # 파일이 있으면 저장
    if file and file.filename:
        file_path = await save_upload_file(file)
    
    # 게시글 생성 데이터
    post_data = PostCreate(title=title, content=content)
    
    # 게시글 생성 (파일 경로 포함)
    created_post = post_crud.create_post(
        db=db, 
        post=post_data, 
        author_id=current_user.id,
        file_path=file_path
    )
    
    return created_post

@router.get("/download/{file_path:path}")
async def download_file(file_path: str):
    """
    파일 다운로드
    
    저장된 파일을 다운로드합니다.
    모든 사용자가 접근 가능합니다. (공개 파일)
    
    Args:
        file_path: 다운로드할 파일 경로
    
    Returns:
        FileResponse: 파일 응답
    
    Raises:
        HTTPException: 파일을 찾을 수 없을 때
    """
    # 파일 존재 확인
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="파일을 찾을 수 없습니다."
        )
    
    # 파일명 추출
    filename = os.path.basename(file_path)
    
    # 파일 다운로드 응답
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/octet-stream'  # 브라우저가 다운로드하도록 강제
    )

@router.delete("/delete/{file_path:path}")
async def delete_uploaded_file(
    file_path: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    업로드된 파일 삭제
    
    서버에서 파일을 삭제합니다.
    (주의: 실제 운영에서는 관리자만 접근하도록 권한을 제한해야 합니다)
    
    Args:
        file_path: 삭제할 파일 경로
        current_user: 현재 로그인한 사용자
    
    Returns:
        dict: 삭제 결과
    """
    success = delete_file(file_path)
    
    if success:
        return {"message": "파일이 성공적으로 삭제되었습니다."}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="파일을 찾을 수 없거나 삭제할 수 없습니다."
        )