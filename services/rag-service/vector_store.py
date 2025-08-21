import chromadb
import uuid
from typing import List, Dict, Any, Optional, Tuple
from sentence_transformers import SentenceTransformer
import numpy as np
import json

class VectorStore:
    """ChromaDB를 사용한 벡터 저장소"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.embedding_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        self.collections = {}
    
    def get_or_create_collection(self, collection_name: str):
        """컬렉션 가져오기 또는 생성"""
        if collection_name not in self.collections:
            try:
                # 기존 컬렉션 가져오기
                collection = self.client.get_collection(collection_name)
            except ValueError:
                # 새 컬렉션 생성
                collection = self.client.create_collection(
                    name=collection_name,
                    metadata={"hnsw:space": "cosine"}
                )
            self.collections[collection_name] = collection
        
        return self.collections[collection_name]
    
    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """텍스트를 벡터로 변환"""
        embeddings = self.embedding_model.encode(texts)
        return embeddings.tolist()
    
    def add_documents(self, 
                     collection_name: str,
                     documents: List[str],
                     metadatas: List[Dict[str, Any]],
                     ids: Optional[List[str]] = None) -> List[str]:
        """문서를 벡터 저장소에 추가"""
        
        collection = self.get_or_create_collection(collection_name)
        
        # ID 생성
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in documents]
        
        # 임베딩 생성
        embeddings = self.create_embeddings(documents)
        
        # 컬렉션에 추가
        collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        return ids
    
    def search_documents(self,
                        collection_name: str,
                        query: str,
                        n_results: int = 5,
                        where: Optional[Dict[str, Any]] = None,
                        similarity_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """문서 검색"""
        
        try:
            collection = self.get_or_create_collection(collection_name)
            
            # 쿼리 임베딩 생성
            query_embedding = self.create_embeddings([query])[0]
            
            # 검색 실행
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where,
                include=['documents', 'metadatas', 'distances']
            )
            
            # 결과 포맷팅
            search_results = []
            if results['documents'] and results['documents'][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                )):
                    # 코사인 거리를 유사도로 변환 (1 - distance)
                    similarity = 1.0 - distance
                    
                    if similarity >= similarity_threshold:
                        search_results.append({
                            'id': results['ids'][0][i],
                            'content': doc,
                            'metadata': metadata,
                            'similarity_score': similarity,
                            'distance': distance
                        })
            
            return search_results
        
        except Exception as e:
            print(f"Search error: {str(e)}")
            return []
    
    def update_document(self,
                       collection_name: str,
                       document_id: str,
                       document: str,
                       metadata: Dict[str, Any]) -> bool:
        """문서 업데이트"""
        
        try:
            collection = self.get_or_create_collection(collection_name)
            
            # 임베딩 생성
            embedding = self.create_embeddings([document])[0]
            
            # 업데이트
            collection.update(
                ids=[document_id],
                embeddings=[embedding],
                documents=[document],
                metadatas=[metadata]
            )
            
            return True
        
        except Exception as e:
            print(f"Update error: {str(e)}")
            return False
    
    def delete_document(self, collection_name: str, document_id: str) -> bool:
        """문서 삭제"""
        
        try:
            collection = self.get_or_create_collection(collection_name)
            collection.delete(ids=[document_id])
            return True
        
        except Exception as e:
            print(f"Delete error: {str(e)}")
            return False
    
    def get_document(self, collection_name: str, document_id: str) -> Optional[Dict[str, Any]]:
        """특정 문서 조회"""
        
        try:
            collection = self.get_or_create_collection(collection_name)
            
            results = collection.get(
                ids=[document_id],
                include=['documents', 'metadatas', 'embeddings']
            )
            
            if results['documents'] and results['documents'][0]:
                return {
                    'id': document_id,
                    'content': results['documents'][0],
                    'metadata': results['metadatas'][0],
                    'embedding': results['embeddings'][0] if results['embeddings'] else None
                }
            
            return None
        
        except Exception as e:
            print(f"Get document error: {str(e)}")
            return None
    
    def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """컬렉션 통계 정보"""
        
        try:
            collection = self.get_or_create_collection(collection_name)
            count = collection.count()
            
            return {
                'name': collection_name,
                'document_count': count,
                'embedding_dimension': 384  # sentence-transformers 모델 차원
            }
        
        except Exception as e:
            print(f"Stats error: {str(e)}")
            return {'name': collection_name, 'document_count': 0, 'embedding_dimension': 384}
    
    def list_collections(self) -> List[str]:
        """모든 컬렉션 목록"""
        try:
            collections = self.client.list_collections()
            return [collection.name for collection in collections]
        except Exception as e:
            print(f"List collections error: {str(e)}")
            return []
    
    def delete_collection(self, collection_name: str) -> bool:
        """컬렉션 삭제"""
        try:
            self.client.delete_collection(collection_name)
            if collection_name in self.collections:
                del self.collections[collection_name]
            return True
        except Exception as e:
            print(f"Delete collection error: {str(e)}")
            return False
    
    def find_similar_documents(self,
                              collection_name: str,
                              document_id: str,
                              n_results: int = 5,
                              similarity_threshold: float = 0.8) -> List[Dict[str, Any]]:
        """특정 문서와 유사한 문서 찾기"""
        
        # 원본 문서 가져오기
        original_doc = self.get_document(collection_name, document_id)
        if not original_doc or not original_doc.get('content'):
            return []
        
        # 원본 문서 내용으로 검색
        return self.search_documents(
            collection_name=collection_name,
            query=original_doc['content'],
            n_results=n_results + 1,  # 원본 문서 제외하기 위해 +1
            similarity_threshold=similarity_threshold
        )


class DocumentChunker:
    """문서 청킹 클래스"""
    
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """텍스트를 청크로 분할"""
        
        if not text.strip():
            return []
        
        chunks = []
        words = text.split()
        
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = ' '.join(chunk_words)
            
            chunk_metadata = {
                'chunk_index': len(chunks),
                'start_position': i,
                'end_position': min(i + self.chunk_size, len(words)),
                'token_count': len(chunk_words),
                **(metadata or {})
            }
            
            chunks.append({
                'content': chunk_text,
                'metadata': chunk_metadata
            })
        
        return chunks
    
    def chunk_by_sentences(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """문장 단위로 청킹"""
        
        # 간단한 문장 분리 (실제로는 더 정교한 방법 사용 권장)
        sentences = text.replace('!', '.').replace('?', '.').split('.')
        sentences = [s.strip() for s in sentences if s.strip()]
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence.split())
            
            if current_length + sentence_length > self.chunk_size and current_chunk:
                # 현재 청크 완성
                chunk_text = '. '.join(current_chunk) + '.'
                chunk_metadata = {
                    'chunk_index': len(chunks),
                    'sentence_count': len(current_chunk),
                    'token_count': current_length,
                    **(metadata or {})
                }
                
                chunks.append({
                    'content': chunk_text,
                    'metadata': chunk_metadata
                })
                
                # 오버랩 적용
                overlap_sentences = current_chunk[-1:] if current_chunk else []
                current_chunk = overlap_sentences + [sentence]
                current_length = sum(len(s.split()) for s in current_chunk)
            else:
                current_chunk.append(sentence)
                current_length += sentence_length
        
        # 마지막 청크 처리
        if current_chunk:
            chunk_text = '. '.join(current_chunk) + '.'
            chunk_metadata = {
                'chunk_index': len(chunks),
                'sentence_count': len(current_chunk),
                'token_count': current_length,
                **(metadata or {})
            }
            
            chunks.append({
                'content': chunk_text,
                'metadata': chunk_metadata
            })
        
        return chunks