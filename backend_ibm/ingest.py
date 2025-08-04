"""
Data ingestion module for Relativity release notes.
Crawls the official release notes page and extracts structured content.
"""

import httpx
import time
import re
import urllib.parse as up
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import logging
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import json, os
import shutil

DB_DIR = "./chroma_db"
JSON_PATH = "relativity_releases.json"

def build_chroma(json_path=JSON_PATH, db_dir=DB_DIR):
    """Build Chroma vector store with improved embeddings and chunking."""
    
    # Remove existing DB to recreate with new settings
    if os.path.exists(db_dir):
        shutil.rmtree(db_dir)
        print(f"🗑️ Removed existing vector store: {db_dir}")
    
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Create documents with rich metadata
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
            # Create document with metadata
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

    # Improved text splitting
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    # Split documents
    split_docs = []
    for doc in documents:
        splits = splitter.split_documents([doc])
        split_docs.extend(splits)

    # Use multilingual embeddings with normalization
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        encode_kwargs={"normalize_embeddings": True}
    )
    
    # Create vector store
    vs = Chroma.from_documents(
        split_docs, 
        embeddings, 
        persist_directory=db_dir
    )
    vs.persist()
    
    print(f"✅ Vector store creado en: {db_dir}")
    print(f"📊 Documentos indexados: {len(split_docs)}")
    return vs

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base URL for Relativity release notes
BASE_URL = "https://help.relativity.com/RelativityOne/Content/What_s_New/Release_notes.htm"

class RelativityReleaseNotesCrawler:
    """Crawler for Relativity release notes and related pages."""
    
    def __init__(self, base_url: str = BASE_URL, delay: float = 0.5):
        self.base_url = base_url
        self.delay = delay
        self.session = httpx.Client(timeout=30.0)
        
    def fetch_page(self, url: str) -> str:
        """Fetch a single page with error handling."""
        try:
            logger.info(f"Fetching: {url}")
            response = self.session.get(url)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return ""
    
    def extract_links(self, html: str, base_url: str) -> List[str]:
        """Extract all relevant links from the page."""
        soup = BeautifulSoup(html, "html.parser")
        links = []
        
        for anchor in soup.find_all("a", href=True):
            href = anchor["href"]
            full_url = up.urljoin(base_url, href)
            
            # Only include links within the What's New section
            if "RelativityOne/Content/What_s_New" in full_url:
                links.append(full_url)
        
        return sorted(set(links))
    
    def extract_content_blocks(self, html: str, url: str) -> List[Dict[str, Any]]:
        """Extract structured content blocks from a page."""
        soup = BeautifulSoup(html, "html.parser")
        
        # Get page title
        title_elem = soup.find("h1") or soup.find("title")
        page_title = title_elem.get_text(strip=True) if title_elem else "Unknown"
        
        blocks = []
        
        # Extract content from headings and their following content
        for heading in soup.find_all(["h1", "h2", "h3", "h4"]):
            heading_text = heading.get_text(strip=True)
            if not heading_text:
                continue
                
            # Collect content following this heading until next heading
            content_parts = []
            current = heading.find_next_sibling()
            
            while current and current.name not in ["h1", "h2", "h3", "h4"]:
                if current.name in ["p", "ul", "ol", "table", "div"]:
                    text = current.get_text(strip=True)
                    if text:
                        content_parts.append(text)
                current = current.find_next_sibling()
            
            # Create block if we have content
            if content_parts:
                content = "\n".join(content_parts)
                blocks.append({
                    "title": page_title,
                    "heading": heading_text,
                    "content": content,
                    "url": url
                })
        
        # If no structured content found, create a general block
        if not blocks:
            main_content = soup.find("main") or soup.find("body")
            if main_content:
                content = main_content.get_text(strip=True)
                if content:
                    blocks.append({
                        "title": page_title,
                        "heading": "General Information",
                        "content": content,
                        "url": url
                    })
        
        return blocks
    
    def crawl_and_extract(self) -> List[Dict[str, Any]]:
        """Main method to crawl and extract all content."""
        logger.info("Starting crawl of Relativity release notes...")
        
        # Start with the base page
        base_html = self.fetch_page(self.base_url)
        if not base_html:
            logger.error("Failed to fetch base page")
            return []
        
        # Extract all relevant links
        all_urls = [self.base_url] + self.extract_links(base_html, self.base_url)
        logger.info(f"Found {len(all_urls)} pages to crawl")
        
        all_blocks = []
        
        for url in all_urls:
            html = self.fetch_page(url)
            if html:
                blocks = self.extract_content_blocks(html, url)
                all_blocks.extend(blocks)
                logger.info(f"Extracted {len(blocks)} blocks from {url}")
            
            # Respectful delay between requests
            time.sleep(self.delay)
        
        logger.info(f"Total extracted blocks: {len(all_blocks)}")
        return all_blocks
    
    def save_to_json(self, blocks: List[Dict[str, Any]], filename: str = "relativity_releases.json"):
        """Save extracted content to JSON file."""
        import json
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(blocks, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(blocks)} blocks to {filename}")
    
    def close(self):
        """Close the HTTP session."""
        self.session.close()

def main():
    """Main function to run the crawler."""
    crawler = RelativityReleaseNotesCrawler()
    try:
        blocks = crawler.crawl_and_extract()
        if blocks:
            crawler.save_to_json(blocks)
            build_chroma()
            print(f"Successfully extracted {len(blocks)} content blocks")
        else:
            print("No content extracted")
    finally:
        crawler.close()

if __name__ == "__main__":
    main() 