-- PostgreSQL 초기화 스크립트
-- 데이터베이스 생성 (이미 생성되어 있으므로 스킵)

-- 한국어 텍스트 검색을 위한 확장 설치
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- 인덱스 최적화를 위한 설정
-- 사용자 테이블 인덱스 (user-service에서 자동 생성되지만 추가 최적화)
-- MIDI 파일 검색을 위한 인덱스
-- RAG 문서 검색을 위한 인덱스

-- 기본 데이터 삽입 (선택사항)
-- 예: 음악 장르, 악기 목록 등

-- 성능 튜닝
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET log_statement = 'all';
ALTER SYSTEM SET log_min_duration_statement = 1000;

-- 커밋
SELECT pg_reload_conf();