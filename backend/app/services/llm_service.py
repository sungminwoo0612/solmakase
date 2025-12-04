"""
LLM/RAG 서비스
"""
from typing import Dict, Any, List, Optional
from uuid import UUID
import os

from app.core.config import settings
from app.repositories.interfaces.requirement_repository import IRequirementRepository
from app.repositories.interfaces.document_repository import IDocumentRepository


class LLMService:
    """
    LLM 및 RAG 서비스
    """
    
    def __init__(
        self,
        requirement_repository: Optional[IRequirementRepository] = None,
        document_repository: Optional[IDocumentRepository] = None
    ):
        self.requirement_repository = requirement_repository
        self.document_repository = document_repository
        self._vector_store = None
        self._llm = None
    
    def _get_llm(self):
        """LLM 인스턴스 가져오기"""
        if self._llm is None:
            try:
                from langchain_openai import ChatOpenAI
                
                if not settings.OPENAI_API_KEY:
                    raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다")
                
                self._llm = ChatOpenAI(
                    model=settings.OPENAI_MODEL,
                    temperature=0,
                    openai_api_key=settings.OPENAI_API_KEY,
                    timeout=settings.LLM_TIMEOUT,
                )
            except ImportError:
                raise ImportError("langchain-openai가 설치되지 않았습니다. pip install langchain-openai")
        
        return self._llm
    
    def _get_vector_store(self):
        """벡터 스토어 인스턴스 가져오기"""
        if self._vector_store is None:
            try:
                import chromadb
                from langchain_community.vectorstores import Chroma
                from langchain_openai import OpenAIEmbeddings
                
                if not settings.OPENAI_API_KEY:
                    raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다")
                
                # ChromaDB 클라이언트 생성
                chroma_client = chromadb.PersistentClient(
                    path=os.path.join(settings.UPLOAD_DIR, "chroma_db")
                )
                
                # 임베딩 모델
                embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
                
                # 벡터 스토어 생성 또는 로드
                collection_name = "infrastructure_knowledge"
                self._vector_store = Chroma(
                    client=chroma_client,
                    collection_name=collection_name,
                    embedding_function=embeddings,
                )
            except ImportError:
                raise ImportError("chromadb가 설치되지 않았습니다. pip install chromadb")
        
        return self._vector_store
    
    async def analyze_requirement(self, requirement_id: UUID) -> Dict[str, Any]:
        """
        요구사항 분석 (RAG + LLM)
        """
        if not self.requirement_repository:
            raise ValueError("Requirement repository is not initialized")
        
        requirement = self.requirement_repository.get_by_id(requirement_id)
        if not requirement:
            raise ValueError(f"Requirement {requirement_id} not found")
        
        # 요구사항 정보 수집
        requirement_text = self._build_requirement_text(requirement)
        
        # RAG를 통한 관련 문서 검색
        relevant_docs = await self._search_relevant_documents(requirement_text)
        
        # LLM을 통한 요구사항 분석
        analysis_result = await self._analyze_with_llm(requirement_text, relevant_docs)
        
        return analysis_result
    
    def _build_requirement_text(self, requirement) -> str:
        """요구사항을 텍스트로 변환"""
        parts = []
        
        if requirement.service_type:
            parts.append(f"서비스 종류: {requirement.service_type}")
        if requirement.deployment_type:
            parts.append(f"배포 유형: {requirement.deployment_type}")
        if requirement.scale:
            parts.append(f"규모: {requirement.scale}")
        if requirement.budget:
            parts.append(f"예산: {requirement.budget}")
        if requirement.has_ops_team is not None:
            parts.append(f"운영 인력: {'있음' if requirement.has_ops_team else '없음'}")
        if requirement.special_requirements:
            parts.append(f"특이사항: {requirement.special_requirements}")
        
        # 구조화된 데이터가 있으면 추가
        if requirement.structured_data and isinstance(requirement.structured_data, dict):
            if "text" in requirement.structured_data:
                parts.append(f"문서 내용:\n{requirement.structured_data['text']}")
        
        return "\n".join(parts)
    
    async def _search_relevant_documents(self, query: str, k: int = 3) -> List[str]:
        """RAG를 통한 관련 문서 검색"""
        try:
            vector_store = self._get_vector_store()
            
            # 유사 문서 검색
            docs = vector_store.similarity_search(query, k=k)
            
            # 문서 텍스트 추출
            return [doc.page_content for doc in docs]
        except Exception as e:
            # 벡터 스토어가 비어있거나 에러가 발생한 경우 빈 리스트 반환
            print(f"문서 검색 중 에러 발생: {str(e)}")
            return []
    
    async def _analyze_with_llm(self, requirement_text: str, relevant_docs: List[str]) -> Dict[str, Any]:
        """LLM을 통한 요구사항 분석"""
        from langchain.prompts import ChatPromptTemplate
        from langchain.schema import HumanMessage, SystemMessage
        
        llm = self._get_llm()
        
        # 프롬프트 구성
        context = "\n\n".join(relevant_docs) if relevant_docs else "관련 문서 없음"
        
        system_prompt = """당신은 인프라 아키텍처 전문가입니다. 사용자의 요구사항을 분석하여 구조화된 정보를 추출하세요.

다음 형식의 JSON으로 응답하세요:
{
    "service_type": "서비스 종류",
    "deployment_type": "onprem|cloud|hybrid",
    "scale": "small|medium|large",
    "required_features": ["기능1", "기능2"],
    "estimated_users": "예상 사용자 수",
    "performance_requirements": "성능 요구사항",
    "security_requirements": "보안 요구사항",
    "budget_range": "예산 범위",
    "technical_stack_suggestions": ["기술1", "기술2"]
}"""
        
        user_prompt = f"""요구사항:
{requirement_text}

참고 문서:
{context}

위 요구사항을 분석하여 JSON 형식으로 응답하세요."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        # LLM 호출
        response = llm(messages)
        
        # JSON 파싱 시도
        import json
        try:
            # 응답에서 JSON 추출
            response_text = response.content
            # JSON 부분만 추출 (마크다운 코드 블록 제거)
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            analysis_result = json.loads(response_text)
        except json.JSONDecodeError:
            # JSON 파싱 실패 시 기본 구조 반환
            analysis_result = {
                "raw_response": response.content,
                "error": "JSON 파싱 실패"
            }
        
        return analysis_result
    
    async def add_knowledge_document(self, text: str, metadata: Optional[Dict[str, Any]] = None):
        """지식 베이스에 문서 추가"""
        try:
            vector_store = self._get_vector_store()
            
            # 문서 추가
            vector_store.add_texts(
                texts=[text],
                metadatas=[metadata or {}]
            )
        except Exception as e:
            raise ValueError(f"지식 베이스에 문서 추가 실패: {str(e)}")

