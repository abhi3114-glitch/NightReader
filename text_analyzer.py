"""
Text analysis utilities for content density scoring.
Provides formula detection, definition pattern matching, and vocabulary analysis.
"""

import re
from typing import List, Dict, Tuple
from collections import Counter
import math


class TextAnalyzer:
    """Advanced text analysis for academic/technical content."""
    
    # Patterns for mathematical formulas
    FORMULA_PATTERNS = [
        r'[∫∑∏∂∇±≤≥≠≈√∞]',  # Mathematical symbols
        r'\b[a-zA-Z]\s*[=<>≤≥]\s*[0-9a-zA-Z\+\-\*/\^]+',  # Equations
        r'\([a-zA-Z0-9\+\-\*/\^]+\)\s*[\+\-\*/\^]',  # Algebraic expressions
        r'\b\d+\s*[×·]\s*\d+',  # Multiplication
        r'\b[a-zA-Z]\^\d+',  # Exponents
        r'\\\w+\{[^}]*\}',  # LaTeX-like syntax
        r'\$[^$]+\$',  # LaTeX math mode
    ]
    
    # Definition patterns
    DEFINITION_PATTERNS = [
        r'\bis\s+defined\s+as\b',
        r'\brefers\s+to\b',
        r'\bknown\s+as\b',
        r'\bcalled\b',
        r'\bdenotes\b',
        r'\brepresents\b',
        r'\bmeans\b',
        r'\b(?:Definition|Theorem|Lemma|Corollary|Proposition)[:.]',
        r'\bwhere\s+\w+\s+is\b',
    ]
    
    # Common filler words/phrases
    FILLER_INDICATORS = [
        'table of contents',
        'references',
        'bibliography',
        'index',
        'appendix',
        'acknowledgments',
        'preface',
        'about the author',
    ]
    
    def __init__(self):
        self.formula_regex = re.compile('|'.join(self.FORMULA_PATTERNS), re.IGNORECASE)
        self.definition_regex = re.compile('|'.join(self.DEFINITION_PATTERNS), re.IGNORECASE)
    
    def detect_formulas(self, text: str) -> float:
        """
        Detect mathematical formulas in text.
        Returns a score between 0 and 1 based on formula density.
        """
        if not text:
            return 0.0
        
        matches = self.formula_regex.findall(text)
        # Normalize by text length (per 1000 characters)
        density = len(matches) / max(len(text) / 1000, 1)
        # Cap at 1.0
        return min(density / 10, 1.0)
    
    def detect_definitions(self, text: str) -> float:
        """
        Detect definition patterns in text.
        Returns a score between 0 and 1 based on definition density.
        """
        if not text:
            return 0.0
        
        matches = self.definition_regex.findall(text)
        # Normalize by text length (per 1000 characters)
        density = len(matches) / max(len(text) / 1000, 1)
        # Cap at 1.0
        return min(density / 5, 1.0)
    
    def calculate_vocabulary_richness(self, text: str) -> float:
        """
        Calculate lexical diversity (unique words / total words).
        Returns a score between 0 and 1.
        """
        if not text:
            return 0.0
        
        # Tokenize and clean
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        if len(words) < 10:
            return 0.0
        
        unique_words = len(set(words))
        total_words = len(words)
        
        # Type-Token Ratio (TTR)
        ttr = unique_words / total_words
        
        # Normalize TTR (typically 0.4-0.8 for academic text)
        # Higher TTR suggests more varied, information-dense content
        return min(ttr / 0.6, 1.0)
    
    def is_filler_page(self, text: str) -> bool:
        """
        Detect if a page is likely filler content (TOC, references, etc.).
        """
        text_lower = text.lower()
        
        # Check for filler indicators
        for indicator in self.FILLER_INDICATORS:
            if indicator in text_lower:
                return True
        
        # Very short pages are likely filler
        if len(text.strip()) < 100:
            return True
        
        # Pages with very low word count but many newlines (likely TOC)
        words = re.findall(r'\b\w+\b', text)
        lines = text.split('\n')
        if len(words) < 50 and len(lines) > 20:
            return True
        
        return False
    
    def extract_keywords(self, text: str, top_n: int = 10) -> List[Tuple[str, int]]:
        """
        Extract top N keywords from text based on frequency.
        Returns list of (word, count) tuples.
        """
        if not text:
            return []
        
        # Tokenize and clean
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        
        # Common stop words to exclude
        stop_words = {
            'that', 'this', 'with', 'from', 'have', 'will', 'been',
            'were', 'said', 'each', 'which', 'their', 'there', 'would',
            'about', 'into', 'than', 'them', 'these', 'only', 'some',
            'could', 'other', 'then', 'more', 'very', 'when', 'much',
            'such', 'also', 'many', 'most', 'over', 'well', 'even',
        }
        
        # Filter stop words
        filtered_words = [w for w in words if w not in stop_words]
        
        # Count frequencies
        word_counts = Counter(filtered_words)
        
        return word_counts.most_common(top_n)
    
    def calculate_content_density(
        self,
        text: str,
        tfidf_score: float
    ) -> Dict[str, float]:
        """
        Calculate multi-factor content density score.
        
        Args:
            text: Page text content
            tfidf_score: Pre-calculated TF-IDF score (0-1 normalized)
        
        Returns:
            Dictionary with component scores and total score
        """
        formula_score = self.detect_formulas(text)
        definition_score = self.detect_definitions(text)
        vocab_score = self.calculate_vocabulary_richness(text)
        
        # Weighted combination
        weights = {
            'tfidf': 0.60,
            'formulas': 0.15,
            'definitions': 0.15,
            'vocabulary': 0.10,
        }
        
        total_score = (
            tfidf_score * weights['tfidf'] +
            formula_score * weights['formulas'] +
            definition_score * weights['definitions'] +
            vocab_score * weights['vocabulary']
        )
        
        return {
            'tfidf': tfidf_score,
            'formulas': formula_score,
            'definitions': definition_score,
            'vocabulary': vocab_score,
            'total': total_score,
        }
