"""
Page extraction and export functionality.
Extracts high-density pages and creates summary reports.
"""

import fitz  # PyMuPDF
import pandas as pd
from typing import List, Optional
from pathlib import Path
from pdf_analyzer import PageScore
import io


class PageExtractor:
    """Extract and export high-density pages from PDFs."""
    
    def __init__(self):
        pass
    
    def extract_pages_to_pdf(
        self,
        source_pdf_path: str,
        page_scores: List[PageScore],
        output_pdf_path: str
    ) -> bool:
        """
        Extract selected pages and save as a new PDF.
        
        Args:
            source_pdf_path: Path to original PDF
            page_scores: List of PageScore objects to extract
            output_pdf_path: Path for output PDF
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Open source PDF
            source_doc = fitz.open(source_pdf_path)
            
            # Create new PDF
            output_doc = fitz.open()
            
            # Sort pages by original page number for logical order
            sorted_pages = sorted(page_scores, key=lambda x: x.page_num)
            
            # Extract each page
            for page_score in sorted_pages:
                # Page numbers are 1-indexed, but PyMuPDF uses 0-indexed
                page_idx = page_score.page_num - 1
                
                if 0 <= page_idx < len(source_doc):
                    # Insert page into output document
                    output_doc.insert_pdf(
                        source_doc,
                        from_page=page_idx,
                        to_page=page_idx
                    )
            
            # Save output PDF
            output_doc.save(output_pdf_path)
            
            # Close documents
            output_doc.close()
            source_doc.close()
            
            return True
            
        except Exception as e:
            print(f"Error extracting pages: {str(e)}")
            return False
    
    def create_summary_csv(
        self,
        page_scores: List[PageScore],
        output_csv_path: str
    ) -> bool:
        """
        Create CSV summary of extracted pages with scores and keywords.
        
        Args:
            page_scores: List of PageScore objects
            output_csv_path: Path for output CSV
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Prepare data for DataFrame
            data = []
            
            for ps in page_scores:
                # Format keywords as comma-separated string
                keywords_str = ', '.join([f"{word}({count})" for word, count in ps.keywords[:5]])
                
                data.append({
                    'Page': ps.page_num,
                    'Total Score': round(ps.total_score, 4),
                    'TF-IDF Score': round(ps.tfidf_score, 4),
                    'Formula Score': round(ps.formula_score, 4),
                    'Definition Score': round(ps.definition_score, 4),
                    'Vocabulary Score': round(ps.vocabulary_score, 4),
                    'Is Filler': ps.is_filler,
                    'Top Keywords': keywords_str,
                })
            
            # Create DataFrame
            df = pd.DataFrame(data)
            
            # Save to CSV
            df.to_csv(output_csv_path, index=False)
            
            return True
            
        except Exception as e:
            print(f"Error creating summary CSV: {str(e)}")
            return False
    
    def create_summary_report(
        self,
        page_scores: List[PageScore],
        statistics: dict,
        percentage: float
    ) -> str:
        """
        Create a text summary report of the extraction.
        
        Args:
            page_scores: List of extracted PageScore objects
            statistics: Statistics dictionary from PDFAnalyzer
            percentage: Percentage threshold used
        
        Returns:
            Formatted summary text
        """
        report_lines = []
        
        report_lines.append("=" * 60)
        report_lines.append("NightReader - Extraction Summary")
        report_lines.append("=" * 60)
        report_lines.append("")
        
        # Overall statistics
        report_lines.append("📊 Document Statistics")
        report_lines.append("-" * 60)
        report_lines.append(f"Total Pages: {statistics.get('total_pages', 0)}")
        report_lines.append(f"Filler Pages: {statistics.get('filler_pages', 0)}")
        report_lines.append(f"Content Pages: {statistics.get('content_pages', 0)}")
        report_lines.append(f"Average Score: {statistics.get('avg_score', 0):.4f}")
        report_lines.append(f"Median Score: {statistics.get('median_score', 0):.4f}")
        report_lines.append("")
        
        # Extraction info
        report_lines.append("📄 Extraction Details")
        report_lines.append("-" * 60)
        report_lines.append(f"Threshold: Top {percentage}%")
        report_lines.append(f"Pages Extracted: {len(page_scores)}")
        report_lines.append("")
        
        # Top pages
        report_lines.append("🏆 Top Extracted Pages")
        report_lines.append("-" * 60)
        
        # Sort by score for display
        sorted_scores = sorted(page_scores, key=lambda x: x.total_score, reverse=True)
        
        for i, ps in enumerate(sorted_scores[:10], 1):  # Show top 10
            keywords_str = ', '.join([word for word, _ in ps.keywords[:5]])
            report_lines.append(
                f"{i:2d}. Page {ps.page_num:3d} | Score: {ps.total_score:.4f} | "
                f"Keywords: {keywords_str}"
            )
        
        if len(sorted_scores) > 10:
            report_lines.append(f"... and {len(sorted_scores) - 10} more pages")
        
        report_lines.append("")
        report_lines.append("=" * 60)
        
        return '\n'.join(report_lines)
    
    def extract_pages_to_bytes(
        self,
        source_pdf_path: str,
        page_scores: List[PageScore]
    ) -> Optional[bytes]:
        """
        Extract selected pages and return as bytes (for Streamlit download).
        
        Args:
            source_pdf_path: Path to original PDF
            page_scores: List of PageScore objects to extract
        
        Returns:
            PDF bytes if successful, None otherwise
        """
        try:
            # Open source PDF
            source_doc = fitz.open(source_pdf_path)
            
            # Create new PDF
            output_doc = fitz.open()
            
            # Sort pages by original page number
            sorted_pages = sorted(page_scores, key=lambda x: x.page_num)
            
            # Extract each page
            for page_score in sorted_pages:
                page_idx = page_score.page_num - 1
                
                if 0 <= page_idx < len(source_doc):
                    output_doc.insert_pdf(
                        source_doc,
                        from_page=page_idx,
                        to_page=page_idx
                    )
            
            # Save to bytes
            pdf_bytes = output_doc.tobytes()
            
            # Close documents
            output_doc.close()
            source_doc.close()
            
            return pdf_bytes
            
        except Exception as e:
            print(f"Error extracting pages to bytes: {str(e)}")
            return None
