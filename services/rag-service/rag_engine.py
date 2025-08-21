import openai
import time
from typing import List, Dict, Any, Optional
from .vector_store import VectorStore, DocumentChunker

class RAGEngine:
    """RAG (Retrieval-Augmented Generation) 엔진"""
    
    def __init__(self, vector_store: VectorStore, api_key: str):
        self.vector_store = vector_store
        self.chunker = DocumentChunker()
        openai.api_key = api_key
    
    def process_document(self,
                        document_id: int,
                        content: str,
                        metadata: Dict[str, Any],
                        collection_name: str = "default",
                        chunk_method: str = "words") -> List[str]:
        """문서 처리 및 벡터화"""
        
        # 청킹
        if chunk_method == "sentences":
            chunks = self.chunker.chunk_by_sentences(content, metadata)
        else:
            chunks = self.chunker.chunk_text(content, metadata)
        
        # 벡터 저장소에 추가
        chunk_ids = []
        for i, chunk in enumerate(chunks):
            chunk_id = f"doc_{document_id}_chunk_{i}"
            
            # 메타데이터에 문서 정보 추가
            chunk_metadata = {
                **chunk['metadata'],
                'document_id': document_id,
                'chunk_id': chunk_id,
                'total_chunks': len(chunks)
            }
            
            # 벡터 저장소에 추가
            ids = self.vector_store.add_documents(
                collection_name=collection_name,
                documents=[chunk['content']],
                metadatas=[chunk_metadata],
                ids=[chunk_id]
            )
            chunk_ids.extend(ids)
        
        return chunk_ids
    
    def search_and_generate(self,
                           query: str,
                           collection_name: str = "default",
                           max_results: int = 5,
                           similarity_threshold: float = 0.7,
                           model: str = "gpt-3.5-turbo",
                           max_tokens: int = 1000,
                           temperature: float = 0.7,
                           system_prompt: Optional[str] = None,
                           filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """검색 기반 응답 생성"""
        
        start_time = time.time()
        
        # 1. 문서 검색
        search_start = time.time()
        search_results = self.vector_store.search_documents(
            collection_name=collection_name,
            query=query,
            n_results=max_results,
            where=filters,
            similarity_threshold=similarity_threshold
        )
        search_time = time.time() - search_start
        
        # 2. 컨텍스트 구성
        context_chunks = []
        for result in search_results:
            context_chunks.append({
                'content': result['content'],
                'source': result['metadata'].get('title', 'Unknown'),
                'similarity': result['similarity_score']
            })
        
        # 3. 프롬프트 생성
        context_text = "\n\n".join([
            f"[출처: {chunk['source']} (유사도: {chunk['similarity']:.2f})]\n{chunk['content']}"
            for chunk in context_chunks
        ])
        
        if not system_prompt:
            system_prompt = """당신은 음악 이론과 MIDI에 특화된 AI 어시스턴트입니다. 
제공된 문서들을 바탕으로 정확하고 도움이 되는 답변을 제공하세요.
답변은 한국어로 작성하고, 출처를 명시해주세요."""
        
        user_prompt = f"""다음 문서들을 참고하여 질문에 답해주세요:

문서 내용:
{context_text}

질문: {query}

답변:"""
        
        # 4. LLM을 통한 응답 생성
        generation_start = time.time()
        try:
            response = openai.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            generated_text = response.choices[0].message.content
            
        except Exception as e:
            generated_text = f"응답 생성 중 오류가 발생했습니다: {str(e)}"
        
        generation_time = time.time() - generation_start
        total_time = time.time() - start_time
        
        # 5. 결과 반환
        return {
            'query': query,
            'response': generated_text,
            'search_results': [
                {
                    'document_id': result['metadata'].get('document_id'),
                    'chunk_id': result['metadata'].get('chunk_id'),
                    'content': result['content'],
                    'similarity_score': result['similarity_score'],
                    'document_title': result['metadata'].get('title', 'Unknown'),
                    'document_type': result['metadata'].get('document_type', 'unknown'),
                    'category': result['metadata'].get('category'),
                    'metadata': result['metadata'] if 'include_metadata' in filters else None
                }
                for result in search_results
            ],
            'total_results': len(search_results),
            'search_time': search_time,
            'generation_time': generation_time,
            'total_time': total_time,
            'model_used': model
        }
    
    def get_recommendations(self,
                           user_interests: List[str],
                           collection_name: str = "default",
                           difficulty_level: Optional[str] = None,
                           document_types: Optional[List[str]] = None,
                           limit: int = 10) -> List[Dict[str, Any]]:
        """사용자 관심사 기반 문서 추천"""
        
        # 관심사를 쿼리로 변환
        query = " ".join(user_interests)
        
        # 필터 구성
        filters = {}
        if difficulty_level:
            filters['difficulty_level'] = difficulty_level
        if document_types:
            filters['document_type'] = {"$in": document_types}
        
        # 검색 실행
        search_results = self.vector_store.search_documents(
            collection_name=collection_name,
            query=query,
            n_results=limit,
            where=filters,
            similarity_threshold=0.5  # 추천은 낮은 임계값 사용
        )
        
        # 문서별로 그룹화 (중복 제거)
        seen_documents = set()
        recommendations = []
        
        for result in search_results:
            doc_id = result['metadata'].get('document_id')
            if doc_id not in seen_documents:
                seen_documents.add(doc_id)
                recommendations.append({
                    'document_id': doc_id,
                    'title': result['metadata'].get('title', 'Unknown'),
                    'document_type': result['metadata'].get('document_type'),
                    'category': result['metadata'].get('category'),
                    'difficulty_level': result['metadata'].get('difficulty_level'),
                    'similarity_score': result['similarity_score'],
                    'snippet': result['content'][:200] + "..." if len(result['content']) > 200 else result['content']
                })
        
        return recommendations
    
    def find_similar_documents(self,
                              document_id: int,
                              collection_name: str = "default",
                              similarity_threshold: float = 0.8,
                              limit: int = 5) -> List[Dict[str, Any]]:
        """유사 문서 찾기"""
        
        # 문서의 첫 번째 청크를 기준으로 검색
        chunk_id = f"doc_{document_id}_chunk_0"
        
        original_chunk = self.vector_store.get_document(collection_name, chunk_id)
        if not original_chunk:
            return []
        
        # 유사 문서 검색
        search_results = self.vector_store.search_documents(
            collection_name=collection_name,
            query=original_chunk['content'],
            n_results=limit + 5,  # 원본 문서 청크들 제외하기 위해 여유분 추가
            similarity_threshold=similarity_threshold
        )
        
        # 원본 문서 제외하고 문서별로 그룹화
        seen_documents = {document_id}  # 원본 문서 제외
        similar_docs = []
        
        for result in search_results:
            doc_id = result['metadata'].get('document_id')
            if doc_id not in seen_documents and len(similar_docs) < limit:
                seen_documents.add(doc_id)
                similar_docs.append({
                    'document_id': doc_id,
                    'title': result['metadata'].get('title', 'Unknown'),
                    'document_type': result['metadata'].get('document_type'),
                    'category': result['metadata'].get('category'),
                    'similarity_score': result['similarity_score'],
                    'snippet': result['content'][:200] + "..." if len(result['content']) > 200 else result['content']
                })
        
        return similar_docs
    
    def update_document(self,
                       document_id: int,
                       new_content: str,
                       metadata: Dict[str, Any],
                       collection_name: str = "default") -> bool:
        """문서 업데이트"""
        
        try:
            # 기존 청크들 삭제
            # ChromaDB에서 특정 문서의 모든 청크를 찾아 삭제
            existing_chunks = self.vector_store.search_documents(
                collection_name=collection_name,
                query="",  # 빈 쿼리로 모든 문서 검색
                n_results=1000,  # 충분히 큰 수
                where={'document_id': document_id}
            )
            
            for chunk in existing_chunks:
                chunk_id = chunk['metadata'].get('chunk_id')
                if chunk_id:
                    self.vector_store.delete_document(collection_name, chunk_id)
            
            # 새로운 청크들 추가
            self.process_document(document_id, new_content, metadata, collection_name)
            
            return True
            
        except Exception as e:
            print(f"Document update error: {str(e)}")
            return False
    
    def delete_document(self, document_id: int, collection_name: str = "default") -> bool:
        """문서 삭제"""
        
        try:
            # 문서의 모든 청크 찾기 및 삭제
            existing_chunks = self.vector_store.search_documents(
                collection_name=collection_name,
                query="",
                n_results=1000,
                where={'document_id': document_id}
            )
            
            for chunk in existing_chunks:
                chunk_id = chunk['metadata'].get('chunk_id')
                if chunk_id:
                    self.vector_store.delete_document(collection_name, chunk_id)
            
            return True
            
        except Exception as e:
            print(f"Document deletion error: {str(e)}")
            return False