"""
PDF analysis engine using TF-IDF and content density scoring.
Extracts and ranks pages by information density.
"""

import fitz  # PyMuPDF
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from text_analyzer import TextAnalyzer


@dataclass
class PageScore:
    """Container for page analysis results."""
    page_num: int
    text: str
    tfidf_score: float
    formula_score: float
    definition_score: float
    vocabulary_score: float
    total_score: float
    is_filler: bool
    keywords: List[Tuple[str, int]]


class PDFAnalyzer:
    """Analyze PDF documents for content density."""
    
    def __init__(self):
        self.text_analyzer = TextAnalyzer()
        self.tfidf_vectorizer = None
        self.page_scores: List[PageScore] = []
    
    def extract_text_from_pdf(self, pdf_path: str) -> List[Tuple[int, str]]:
        """
        Extract text from each page of a PDF.
        
        Args:
            pdf_path: Path to PDF file
        
        Returns:
            List of (page_number, text) tuples
        """
        pages = []
        
        try:
            doc = fitz.open(pdf_path)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                pages.append((page_num + 1, text))  # 1-indexed page numbers
            
            doc.close()
            
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
        
        return pages
    
    def compute_tfidf_scores(self, texts: List[str]) -> np.ndarray:
        """
        Compute TF-IDF scores for each page.
        
        Args:
            texts: List of page texts
        
        Returns:
            Array of normalized TF-IDF scores per page
        """
        if not texts or len(texts) == 0:
            return np.array([])
        
        # Initialize TF-IDF vectorizer
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),  # Unigrams and bigrams
            min_df=1,
            max_df=0.8,  # Ignore terms appearing in >80% of pages
        )
        
        try:
            # Fit and transform
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)
            
            # Sum TF-IDF scores across all terms for each page
            page_scores = np.array(tfidf_matrix.sum(axis=1)).flatten()
            
            # Normalize to 0-1 range
            if page_scores.max() > 0:
                page_scores = page_scores / page_scores.max()
            
            return page_scores
            
        except Exception as e:
            # If TF-IDF fails (e.g., all empty pages), return zeros
            return np.zeros(len(texts))
    
    def analyze_pdf(self, pdf_path: str) -> List[PageScore]:
        """
        Analyze a PDF and score each page by content density.
        
        Args:
            pdf_path: Path to PDF file
        
        Returns:
            List of PageScore objects, sorted by total score (descending)
        """
        # Extract text from all pages
        pages = self.extract_text_from_pdf(pdf_path)
        
        if not pages:
            return []
        
        # Separate page numbers and texts
        page_numbers = [p[0] for p in pages]
        page_texts = [p[1] for p in pages]
        
        # Compute TF-IDF scores
        tfidf_scores = self.compute_tfidf_scores(page_texts)
        
        # Analyze each page
        self.page_scores = []
        
        for i, (page_num, text) in enumerate(pages):
            # Get TF-IDF score
            tfidf_score = tfidf_scores[i] if i < len(tfidf_scores) else 0.0
            
            # Check if filler page
            is_filler = self.text_analyzer.is_filler_page(text)
            
            # Calculate multi-factor content density
            density_scores = self.text_analyzer.calculate_content_density(
                text, tfidf_score
            )
            
            # Extract keywords
            keywords = self.text_analyzer.extract_keywords(text, top_n=10)
            
            # Create PageScore object
            page_score = PageScore(
                page_num=page_num,
                text=text,
                tfidf_score=density_scores['tfidf'],
                formula_score=density_scores['formulas'],
                definition_score=density_scores['definitions'],
                vocabulary_score=density_scores['vocabulary'],
                total_score=density_scores['total'],
                is_filler=is_filler,
                keywords=keywords,
            )
            
            self.page_scores.append(page_score)
        
        # Sort by total score (descending)
        self.page_scores.sort(key=lambda x: x.total_score, reverse=True)
        
        return self.page_scores
    
    def get_top_pages(
        self,
        percentage: float = 20.0,
        min_score: float = 0.0,
        exclude_filler: bool = True
    ) -> List[PageScore]:
        """
        Get top N% of pages by content density.
        
        Args:
            percentage: Percentage of pages to return (0-100)
            min_score: Minimum score threshold
            exclude_filler: Whether to exclude detected filler pages
        
        Returns:
            List of top-scoring PageScore objects
        """
        if not self.page_scores:
            return []
        
        # Filter filler pages if requested
        if exclude_filler:
            candidates = [p for p in self.page_scores if not p.is_filler]
        else:
            candidates = self.page_scores
        
        # Filter by minimum score
        candidates = [p for p in candidates if p.total_score >= min_score]
        
        # Calculate number of pages to return
        num_pages = max(1, int(len(candidates) * percentage / 100))
        
        # Return top N pages (already sorted)
        return candidates[:num_pages]
    
    def get_statistics(self) -> Dict[str, any]:
        """
        Get overall statistics about the analyzed PDF.
        
        Returns:
            Dictionary with statistics
        """
        if not self.page_scores:
            return {}
        
        scores = [p.total_score for p in self.page_scores]
        filler_count = sum(1 for p in self.page_scores if p.is_filler)
        
        return {
            'total_pages': len(self.page_scores),
            'filler_pages': filler_count,
            'content_pages': len(self.page_scores) - filler_count,
            'avg_score': np.mean(scores),
            'median_score': np.median(scores),
            'max_score': np.max(scores),
            'min_score': np.min(scores),
            'std_score': np.std(scores),
        }
