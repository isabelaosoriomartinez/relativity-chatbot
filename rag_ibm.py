"""
RAG (Retrieval-Augmented Generation) pipeline for Relativity release notes with IBM watsonx.ai integration.
Handles vector storage, retrieval, and LLM interactions using IBM watsonx.ai models.
"""

import os
import json
from typing import List, Dict, Any, Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import EmbeddingsFilter
import logging
import requests
import json

logger = logging.getLogger(__name__)

class IBMWatsonXLLM:
    """Wrapper for IBM watsonx.ai LLM integration."""
    
    def __init__(self, model_name: str = "meta-llama/llama-2-13b-chat", api_key: str = None, project_id: str = None):
        self.model_name = model_name
        self.api_key = api_key or os.getenv("IBM_WATSONX_API_KEY")
        self.project_id = project_id or os.getenv("IBM_WATSONX_PROJECT_ID")
        self.base_url = "https://us-south.ml.cloud.ibm.com/ml/v1-beta/generation/text?version=2024-05-29"
        
        if not self.api_key:
            raise ValueError("IBM_WATSONX_API_KEY environment variable is required")
        if not self.project_id:
            raise ValueError("IBM_WATSONX_PROJECT_ID environment variable is required")
    
    def _get_iam_token(self) -> str:
        """Get IAM token from API key."""
        try:
            url = "https://iam.cloud.ibm.com/identity/token"
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json"
            }
            data = {
                "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
                "apikey": self.api_key
            }
            
            response = requests.post(url, headers=headers, data=data, timeout=30)
            response.raise_for_status()
            
            token_data = response.json()
            return token_data.get("access_token")
            
        except Exception as e:
            logger.error(f"Error getting IAM token: {e}")
            raise
    
    def __call__(self, prompt: str, temperature: float = 0.0, max_tokens: int = 1000) -> str:
        """Generate text using IBM watsonx.ai."""
        try:
            # Get IAM token
            access_token = self._get_iam_token()
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            payload = {
                "model_id": self.model_name,
                "input": prompt,
                "parameters": {
                    "temperature": temperature,
                    "max_new_tokens": max_tokens
                },
                "project_id": self.project_id
            }
            
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            return result.get("results", [{}])[0].get("generated_text", "")
            
        except Exception as e:
            logger.error(f"Error calling IBM watsonx.ai: {e}")
            raise

class RelativityRAGPipelineIBM:
    """RAG pipeline for Relativity release notes using IBM watsonx.ai."""
    
    def __init__(self, 
                 embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                 llm_model: str = "meta-llama/llama-2-13b-chat",
                 chunk_size: int = 1000,
                 chunk_overlap: int = 150,
                 k_retrieval: int = 8,
                 fetch_k: int = 40):
        
        self.embedding_model = embedding_model
        self.llm_model = llm_model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.k_retrieval = k_retrieval
        self.fetch_k = fetch_k
        
        # Initialize components with multilingual embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            encode_kwargs={"normalize_embeddings": True}
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
        
        # Initialize IBM watsonx.ai LLM
        self.llm = IBMWatsonXLLM(model_name=llm_model)
        
        # Vector store will be initialized when data is loaded
        self.vector_store = None
        self.qa_chain = None
        self.retriever = None
        
    def load_data_from_json(self, json_file: str) -> List[Document]:
        """Load data from JSON file and convert to LangChain Documents."""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            documents = []
            for block in data:
                # Combine content parts
                content_parts = [
                    block.get("title", ""),
                    block.get("heading", ""),
                    block.get("content", "")
                ]
                content = "\n".join([part for part in content_parts if part.strip()])
                
                if content.strip():
                    # Create document with rich metadata
                    doc = Document(
                        page_content=content,
                        metadata={
                            "title": block.get("title", ""),
                            "heading": block.get("heading", ""),
                            "url": block.get("url", ""),
                            "source": "relativity_release_notes"
                        }
                    )
                    documents.append(doc)
            
            logger.info(f"Loaded {len(documents)} documents from {json_file}")
            return documents
            
        except Exception as e:
            logger.error(f"Error loading data from {json_file}: {e}")
            return []
    
    def create_vector_store(self, documents: List[Document], persist_directory: str = "./chroma_db"):
        """Create vector store from documents."""
        try:
            # Split documents
            split_docs = []
            for doc in documents:
                splits = self.text_splitter.split_documents([doc])
                split_docs.extend(splits)
            
            # Create vector store
            self.vector_store = Chroma.from_documents(
                split_docs,
                self.embeddings,
                persist_directory=persist_directory
            )
            self.vector_store.persist()
            
            logger.info(f"Created vector store with {len(split_docs)} documents")
            return True
            
        except Exception as e:
            logger.error(f"Error creating vector store: {e}")
            return False
    
    def load_existing_vector_store(self, persist_directory: str = "./chroma_db"):
        """Load existing vector store."""
        try:
            self.vector_store = Chroma(
                persist_directory=persist_directory,
                embedding_function=self.embeddings
            )
            logger.info(f"Loaded existing vector store from {persist_directory}")
            return True
        except Exception as e:
            logger.error(f"Error loading vector store: {e}")
            return False
    
    def create_qa_chain(self):
        """Create the QA chain with improved retrieval and prompt."""
        if not self.vector_store:
            raise ValueError("Vector store not initialized. Call create_vector_store() first.")
        
        # Create base retriever with MMR
        base_retriever = self.vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": self.k_retrieval,
                "fetch_k": self.fetch_k,
                "lambda_mult": 0.5
            }
        )
        
        # Add contextual compression with embeddings filter
        compressor = EmbeddingsFilter(
            embeddings=self.embeddings,
            similarity_threshold=0.35
        )
        
        self.retriever = ContextualCompressionRetriever(
            base_compressor=compressor,
            base_retriever=base_retriever
        )
        
        # Improved prompt template with explicit language instruction
        prompt_template = """You are a helpful assistant that answers questions about Relativity software releases based on the official release notes.

IMPORTANT RULES:
1. ONLY answer questions using information found in the provided context
2. If the context doesn't contain enough information to answer the question, respond with "No tengo suficiente información para responder esa pregunta basándome en las notas de versión disponibles." (Spanish) or "I don't have enough information to answer that question based on the available release notes." (English)
3. Always provide citations by including the source URL and heading in your response
4. Be concise but informative
5. CRITICAL: You MUST respond in the EXACT SAME LANGUAGE as the question. If the question is in Spanish, respond in Spanish. If the question is in English, respond in English.
6. If asked about features not mentioned in the context, politely redirect to contact collection

Context information:
{context}

Question: {question}

IMPORTANT: Respond in the same language as the question above.
Answer:"""
        
        self.prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        logger.info("QA chain created successfully with MMR retrieval and contextual compression")
    
    def query(self, question: str) -> Dict[str, Any]:
        """Query the RAG pipeline with improved logic."""
        try:
            if not self.retriever:
                raise ValueError("QA chain not initialized. Call create_qa_chain() first.")
            
            # Retrieve relevant documents
            docs = self.retriever.get_relevant_documents(question)
            
            if not docs:
                # Detect language and respond accordingly
                is_spanish = any(word in question.lower() for word in ['qué', 'cuáles', 'cómo', 'dónde', 'cuándo', 'por qué', 'háblame', 'dime', 'explica', 'describe'])
                
                if is_spanish:
                    answer = "No tengo suficiente información para responder esa pregunta basándome en las notas de versión disponibles."
                else:
                    answer = "I don't have enough information to answer that question based on the available release notes."
                
                return {
                    "answer": answer,
                    "citations": [],
                    "has_sufficient_info": False,
                    "needs_contact": True
                }
            
            # Prepare context
            context = "\n\n".join([doc.page_content for doc in docs])
            
            # Create prompt
            prompt = self.prompt.format(context=context, question=question)
            
            # Generate answer using IBM watsonx.ai
            answer = self.llm(prompt, temperature=0.0, max_tokens=1000)
            
            # Extract citations from metadata
            citations = []
            for doc in docs:
                if doc.metadata.get("url") and (doc.metadata.get("heading") or doc.metadata.get("title")):
                    citations.append({
                        "url": doc.metadata["url"],
                        "title": doc.metadata.get("title", ""),
                        "heading": doc.metadata.get("heading", "")
                    })
            
            # Improved heurística for sufficient information
            answer_length = len(answer.strip())
            has_sufficient_info = (
                len(docs) > 0 and 
                answer_length >= 40 and
                not answer.lower().startswith("i don't have enough information") and
                not answer.lower().startswith("no tengo suficiente información")
            )
            
            return {
                "answer": answer,
                "citations": citations,
                "has_sufficient_info": has_sufficient_info,
                "needs_contact": not has_sufficient_info
            }
            
        except Exception as e:
            logger.error(f"Error querying RAG pipeline: {e}")
            return {
                "answer": "I encountered an error while processing your question. Please try again.",
                "citations": [],
                "has_sufficient_info": False,
                "needs_contact": True
            }
    
    def create_rag_pipeline():
        """Convenience function to create RAG pipeline."""
        return RelativityRAGPipelineIBM()

def create_rag_pipeline():
    """Convenience function to create RAG pipeline."""
    return RelativityRAGPipelineIBM() 