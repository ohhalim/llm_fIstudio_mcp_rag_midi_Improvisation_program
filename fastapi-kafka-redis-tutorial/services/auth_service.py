"""
services/auth_service.py - 인증 및 보안 서비스

이 파일에서 배울 수 있는 개념들:
1. JWT 토큰 생성 및 검증
2. 비밀번호 해싱 및 검증 (bcrypt)
3. 보안 모범 사례
4. 인증 미들웨어 패턴
5. 토큰 기반 인증 시스템
"""

from datetime import datetime, timedelta
from typing import Optional, Union
import bcrypt
from jose import JWTError, jwt
from fastapi import HTTPException, status
import logging
from config import settings

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AuthService:
    """
    인증 및 보안 관련 서비스 클래스
    
    JWT 토큰 생성/검증, 비밀번호 해싱 등의 보안 기능을 제공합니다.
    """
    
    def __init__(self):
        """
        인증 서비스 초기화
        """
        self.secret_key = settings.secret_key
        self.algorithm = settings.algorithm
        self.access_token_expire_minutes = settings.access_token_expire_minutes
        self.password_rounds = settings.password_hash_rounds
        
        logger.info("✅ 인증 서비스 초기화 완료")
    
    def hash_password(self, password: str) -> str:
        """
        비밀번호 해싱
        
        bcrypt를 사용하여 비밀번호를 안전하게 해싱합니다.
        솔트가 자동으로 생성되어 레인보우 테이블 공격을 방지합니다.
        
        Args:
            password (str): 원본 비밀번호
            
        Returns:
            str: 해싱된 비밀번호
        """
        try:
            # 비밀번호를 bytes로 인코딩
            password_bytes = password.encode('utf-8')
            
            # bcrypt로 해싱 (자동으로 솔트 생성)
            hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt(rounds=self.password_rounds))
            
            # bytes를 string으로 변환하여 반환
            return hashed.decode('utf-8')
            
        except Exception as e:
            logger.error(f"❌ 비밀번호 해싱 중 오류: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="비밀번호 처리 중 오류가 발생했습니다"
            )
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        비밀번호 검증
        
        입력된 평문 비밀번호가 해싱된 비밀번호와 일치하는지 확인합니다.
        
        Args:
            plain_password (str): 평문 비밀번호
            hashed_password (str): 해싱된 비밀번호
            
        Returns:
            bool: 일치하면 True, 불일치하면 False
        """
        try:
            # 비밀번호들을 bytes로 인코딩
            plain_bytes = plain_password.encode('utf-8')
            hashed_bytes = hashed_password.encode('utf-8')
            
            # bcrypt로 검증
            return bcrypt.checkpw(plain_bytes, hashed_bytes)
            
        except Exception as e:
            logger.error(f"❌ 비밀번호 검증 중 오류: {e}")
            return False
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        JWT 액세스 토큰 생성
        
        사용자 정보를 포함한 JWT 토큰을 생성합니다.
        토큰에는 만료 시간이 포함되어 자동으로 만료됩니다.
        
        Args:
            data (dict): 토큰에 포함할 데이터 (사용자 ID, 이메일 등)
            expires_delta (Optional[timedelta]): 토큰 만료 시간 (기본값 사용하려면 None)
            
        Returns:
            str: JWT 토큰 문자열
        """
        try:
            # 토큰에 포함할 데이터 복사
            to_encode = data.copy()
            
            # 만료 시간 설정
            if expires_delta:
                expire = datetime.utcnow() + expires_delta
            else:
                expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
            
            # 만료 시간을 토큰 데이터에 추가
            to_encode.update({"exp": expire})
            
            # JWT 토큰 생성
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            
            logger.info(f"✅ JWT 토큰 생성 완료 (만료: {expire})")
            return encoded_jwt
            
        except Exception as e:
            logger.error(f"❌ JWT 토큰 생성 중 오류: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="토큰 생성 중 오류가 발생했습니다"
            )
    
    def verify_token(self, token: str) -> Optional[dict]:
        """
        JWT 토큰 검증 및 디코딩
        
        JWT 토큰의 유효성을 검증하고 포함된 데이터를 반환합니다.
        
        Args:
            token (str): JWT 토큰 문자열
            
        Returns:
            Optional[dict]: 토큰이 유효하면 포함된 데이터, 무효하면 None
        """
        try:
            # JWT 토큰 디코딩 및 검증
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # 만료 시간 확인 (자동으로 처리되지만 명시적 확인)
            exp = payload.get("exp")
            if exp and datetime.utcnow().timestamp() > exp:
                logger.warning("⚠️ 만료된 토큰 사용 시도")
                return None
            
            logger.debug("✅ JWT 토큰 검증 성공")
            return payload
            
        except JWTError as e:
            logger.warning(f"⚠️ JWT 토큰 검증 실패: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ 토큰 검증 중 예상치 못한 오류: {e}")
            return None
    
    def create_refresh_token(self, user_id: int) -> str:
        """
        리프레시 토큰 생성
        
        액세스 토큰보다 긴 만료 시간을 가진 리프레시 토큰을 생성합니다.
        
        Args:
            user_id (int): 사용자 ID
            
        Returns:
            str: 리프레시 토큰
        """
        try:
            # 리프레시 토큰 데이터 (최소한의 정보만 포함)
            refresh_data = {
                "user_id": user_id,
                "token_type": "refresh"
            }
            
            # 긴 만료 시간 (7일)
            expires_delta = timedelta(days=7)
            
            return self.create_access_token(refresh_data, expires_delta)
            
        except Exception as e:
            logger.error(f"❌ 리프레시 토큰 생성 중 오류: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="리프레시 토큰 생성 중 오류가 발생했습니다"
            )
    
    def validate_refresh_token(self, token: str) -> Optional[int]:
        """
        리프레시 토큰 검증 및 사용자 ID 반환
        
        Args:
            token (str): 리프레시 토큰
            
        Returns:
            Optional[int]: 유효하면 사용자 ID, 무효하면 None
        """
        try:
            payload = self.verify_token(token)
            
            if not payload:
                return None
            
            # 리프레시 토큰인지 확인
            if payload.get("token_type") != "refresh":
                logger.warning("⚠️ 잘못된 토큰 타입")
                return None
            
            user_id = payload.get("user_id")
            if not user_id:
                logger.warning("⚠️ 토큰에 사용자 ID가 없습니다")
                return None
            
            return user_id
            
        except Exception as e:
            logger.error(f"❌ 리프레시 토큰 검증 중 오류: {e}")
            return None
    
    def generate_password_reset_token(self, email: str) -> str:
        """
        비밀번호 재설정 토큰 생성
        
        이메일 주소를 기반으로 비밀번호 재설정용 토큰을 생성합니다.
        
        Args:
            email (str): 사용자 이메일
            
        Returns:
            str: 비밀번호 재설정 토큰
        """
        try:
            # 재설정 토큰 데이터
            reset_data = {
                "email": email,
                "token_type": "password_reset",
                "purpose": "reset_password"
            }
            
            # 짧은 만료 시간 (15분)
            expires_delta = timedelta(minutes=15)
            
            return self.create_access_token(reset_data, expires_delta)
            
        except Exception as e:
            logger.error(f"❌ 비밀번호 재설정 토큰 생성 중 오류: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="재설정 토큰 생성 중 오류가 발생했습니다"
            )
    
    def validate_password_reset_token(self, token: str) -> Optional[str]:
        """
        비밀번호 재설정 토큰 검증 및 이메일 반환
        
        Args:
            token (str): 비밀번호 재설정 토큰
            
        Returns:
            Optional[str]: 유효하면 이메일 주소, 무효하면 None
        """
        try:
            payload = self.verify_token(token)
            
            if not payload:
                return None
            
            # 재설정 토큰인지 확인
            if payload.get("token_type") != "password_reset":
                logger.warning("⚠️ 잘못된 토큰 타입")
                return None
            
            email = payload.get("email")
            if not email:
                logger.warning("⚠️ 토큰에 이메일이 없습니다")
                return None
            
            return email
            
        except Exception as e:
            logger.error(f"❌ 비밀번호 재설정 토큰 검증 중 오류: {e}")
            return None
    
    def get_password_strength(self, password: str) -> dict:
        """
        비밀번호 강도 확인
        
        비밀번호의 보안 강도를 평가하고 개선 제안을 제공합니다.
        
        Args:
            password (str): 확인할 비밀번호
            
        Returns:
            dict: 강도 평가 결과
        """
        try:
            score = 0
            suggestions = []
            
            # 길이 확인
            if len(password) >= 8:
                score += 1
            else:
                suggestions.append("8자 이상으로 설정하세요")
            
            if len(password) >= 12:
                score += 1
            else:
                suggestions.append("12자 이상을 권장합니다")
            
            # 문자 종류 확인
            has_lower = any(c.islower() for c in password)
            has_upper = any(c.isupper() for c in password)
            has_digit = any(c.isdigit() for c in password)
            has_special = any(not c.isalnum() for c in password)
            
            if has_lower:
                score += 1
            else:
                suggestions.append("소문자를 포함하세요")
            
            if has_upper:
                score += 1
            else:
                suggestions.append("대문자를 포함하세요")
            
            if has_digit:
                score += 1
            else:
                suggestions.append("숫자를 포함하세요")
            
            if has_special:
                score += 1
            else:
                suggestions.append("특수문자를 포함하세요")
            
            # 연속 문자 확인
            has_sequence = False
            for i in range(len(password) - 2):
                if (ord(password[i]) == ord(password[i+1]) - 1 == ord(password[i+2]) - 2):
                    has_sequence = True
                    break
            
            if has_sequence:
                suggestions.append("연속된 문자를 피하세요 (예: abc, 123)")
            else:
                score += 1
            
            # 강도 레벨 결정
            if score >= 6:
                strength = "strong"
                level = "강함"
            elif score >= 4:
                strength = "medium"
                level = "보통"
            else:
                strength = "weak"
                level = "약함"
            
            return {
                "strength": strength,
                "level": level,
                "score": score,
                "max_score": 7,
                "suggestions": suggestions
            }
            
        except Exception as e:
            logger.error(f"❌ 비밀번호 강도 확인 중 오류: {e}")
            return {
                "strength": "unknown",
                "level": "알 수 없음",
                "score": 0,
                "max_score": 7,
                "suggestions": ["비밀번호 확인 중 오류가 발생했습니다"]
            }


# 싱글톤 인스턴스 생성
auth_service = AuthService()


# 편의 함수들
def hash_password(password: str) -> str:
    """비밀번호 해싱 편의 함수"""
    return auth_service.hash_password(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호 검증 편의 함수"""
    return auth_service.verify_password(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """JWT 토큰 생성 편의 함수"""
    return auth_service.create_access_token(data, expires_delta)


def verify_token(token: str) -> Optional[dict]:
    """JWT 토큰 검증 편의 함수"""
    return auth_service.verify_token(token)


if __name__ == "__main__":
    """
    인증 서비스 테스트
    """
    print("인증 서비스 테스트 시작...")
    
    # 비밀번호 해싱 테스트
    test_password = "mySecurePassword123!"
    hashed = auth_service.hash_password(test_password)
    print(f"원본 비밀번호: {test_password}")
    print(f"해싱된 비밀번호: {hashed}")
    
    # 비밀번호 검증 테스트
    is_valid = auth_service.verify_password(test_password, hashed)
    print(f"비밀번호 검증: {'성공' if is_valid else '실패'}")
    
    # 잘못된 비밀번호 테스트
    wrong_password = "wrongPassword"
    is_wrong = auth_service.verify_password(wrong_password, hashed)
    print(f"잘못된 비밀번호 검증: {'성공' if is_wrong else '실패 (정상)'}")
    
    # JWT 토큰 테스트
    token_data = {"user_id": 123, "email": "test@example.com"}
    token = auth_service.create_access_token(token_data)
    print(f"생성된 JWT 토큰: {token[:50]}...")
    
    # 토큰 검증 테스트
    decoded = auth_service.verify_token(token)
    print(f"토큰 디코딩 결과: {decoded}")
    
    # 비밀번호 강도 테스트
    strength = auth_service.get_password_strength(test_password)
    print(f"비밀번호 강도: {strength}")
    
    print("인증 서비스 테스트 완료! 🔐")