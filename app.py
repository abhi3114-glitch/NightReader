"""
NightReader - Intelligent PDF Page Selector
Streamlit UI for analyzing and extracting high-density pages from PDFs.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from pdf_analyzer import PDFAnalyzer, PageScore
from page_extractor import PageExtractor
from typing import List, Optional
import tempfile
import os
from pathlib import Path


# Page configuration
st.set_page_config(
    page_title="NightReader - PDF Page Selector",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = PDFAnalyzer()
    if 'extractor' not in st.session_state:
        st.session_state.extractor = PageExtractor()
    if 'page_scores' not in st.session_state:
        st.session_state.page_scores = []
    if 'pdf_path' not in st.session_state:
        st.session_state.pdf_path = None
    if 'statistics' not in st.session_state:
        st.session_state.statistics = {}


def plot_density_scores(page_scores: List[PageScore], threshold_percentage: float):
    """Create interactive bar chart of page density scores."""
    if not page_scores:
        return None
    
    # Sort by page number for visualization
    sorted_scores = sorted(page_scores, key=lambda x: x.page_num)
    
    page_nums = [ps.page_num for ps in sorted_scores]
    total_scores = [ps.total_score for ps in sorted_scores]
    
    # Calculate threshold line
    num_pages_to_extract = max(1, int(len(page_scores) * threshold_percentage / 100))
    scores_copy = sorted([ps.total_score for ps in page_scores], reverse=True)
    threshold_score = scores_copy[min(num_pages_to_extract - 1, len(scores_copy) - 1)]
    
    # Create bar chart
    fig = go.Figure()
    
    # Color bars based on whether they're above threshold
    colors = ['#2ecc71' if score >= threshold_score else '#95a5a6' for score in total_scores]
    
    fig.add_trace(go.Bar(
        x=page_nums,
        y=total_scores,
        marker_color=colors,
        hovertemplate='<b>Page %{x}</b><br>Score: %{y:.4f}<extra></extra>',
        name='Content Density Score'
    ))
    
    # Add threshold line
    fig.add_hline(
        y=threshold_score,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Threshold (Top {threshold_percentage}%)",
        annotation_position="right"
    )
    
    fig.update_layout(
        title="Content Density Score per Page",
        xaxis_title="Page Number",
        yaxis_title="Density Score",
        hovermode='closest',
        height=400,
        showlegend=False
    )
    
    return fig


def plot_score_components(page_scores: List[PageScore], selected_page: Optional[int] = None):
    """Create stacked bar chart showing score components for top pages."""
    if not page_scores:
        return None
    
    # Get top 20 pages by total score
    top_pages = sorted(page_scores, key=lambda x: x.total_score, reverse=True)[:20]
    
    page_nums = [f"Page {ps.page_num}" for ps in top_pages]
    tfidf = [ps.tfidf_score * 0.60 for ps in top_pages]  # Scale by weight
    formulas = [ps.formula_score * 0.15 for ps in top_pages]
    definitions = [ps.definition_score * 0.15 for ps in top_pages]
    vocabulary = [ps.vocabulary_score * 0.10 for ps in top_pages]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(name='TF-IDF (60%)', x=page_nums, y=tfidf, marker_color='#3498db'))
    fig.add_trace(go.Bar(name='Formulas (15%)', x=page_nums, y=formulas, marker_color='#e74c3c'))
    fig.add_trace(go.Bar(name='Definitions (15%)', x=page_nums, y=definitions, marker_color='#f39c12'))
    fig.add_trace(go.Bar(name='Vocabulary (10%)', x=page_nums, y=vocabulary, marker_color='#9b59b6'))
    
    fig.update_layout(
        title="Score Components for Top 20 Pages",
        xaxis_title="Page",
        yaxis_title="Weighted Score",
        barmode='stack',
        height=400,
        hovermode='x unified'
    )
    
    return fig


def render_page_details(page_score: PageScore):
    """Render detailed information for a single page."""
    st.subheader(f"Page {page_score.page_num} Details")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Score", f"{page_score.total_score:.4f}")
        st.metric("TF-IDF Score", f"{page_score.tfidf_score:.4f}")
    
    with col2:
        st.metric("Formula Score", f"{page_score.formula_score:.4f}")
        st.metric("Definition Score", f"{page_score.definition_score:.4f}")
    
    with col3:
        st.metric("Vocabulary Score", f"{page_score.vocabulary_score:.4f}")
        st.metric("Filler Page", "Yes" if page_score.is_filler else "No")
    
    # Keywords
    if page_score.keywords:
        st.markdown("**Top Keywords:**")
        keywords_text = " • ".join([f"{word} ({count})" for word, count in page_score.keywords[:10]])
        st.info(keywords_text)
    
    # Text preview
    with st.expander("View Page Text"):
        st.text_area(
            "Page Content",
            page_score.text[:2000] + ("..." if len(page_score.text) > 2000 else ""),
            height=300,
            disabled=True
        )


def main():
    """Main Streamlit application."""
    initialize_session_state()
    
    # Header
    st.title("📚 NightReader")
    st.markdown("**Intelligent PDF Page Selector** — Extract high-density pages using TF-IDF analysis")
    
    st.divider()
    
    # Sidebar
    with st.sidebar:
        st.header("Upload PDF")
        
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type=['pdf'],
            help="Upload a textbook, research paper, or notes PDF"
        )
        
        if uploaded_file is not None:
            # Save uploaded file to temporary location
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(uploaded_file.read())
                tmp_path = tmp_file.name
                st.session_state.pdf_path = tmp_path
            
            st.success(f"Uploaded: {uploaded_file.name}")
            
            # Analyze button
            if st.button("🔍 Analyze PDF", type="primary", use_container_width=True):
                with st.spinner("Analyzing PDF content..."):
                    try:
                        # Analyze PDF
                        page_scores = st.session_state.analyzer.analyze_pdf(tmp_path)
                        st.session_state.page_scores = page_scores
                        st.session_state.statistics = st.session_state.analyzer.get_statistics()
                        
                        st.success(f"✅ Analyzed {len(page_scores)} pages!")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error analyzing PDF: {str(e)}")
        
        st.divider()
        
        # Settings
        if st.session_state.page_scores:
            st.header("Extraction Settings")
            
            threshold_percentage = st.slider(
                "Select Top %",
                min_value=5,
                max_value=100,
                value=20,
                step=5,
                help="Extract top N% of pages by content density"
            )
            
            min_score = st.slider(
                "Minimum Score",
                min_value=0.0,
                max_value=1.0,
                value=0.0,
                step=0.05,
                help="Exclude pages below this score"
            )
            
            exclude_filler = st.checkbox(
                "Exclude Filler Pages",
                value=True,
                help="Automatically exclude TOC, references, etc."
            )
            
            st.divider()
            
            # Export section
            st.header("Export")
            
            # Get selected pages
            selected_pages = st.session_state.analyzer.get_top_pages(
                percentage=threshold_percentage,
                min_score=min_score,
                exclude_filler=exclude_filler
            )
            
            st.info(f"📄 {len(selected_pages)} pages will be extracted")
            
            if st.button("📥 Download Extracted PDF", use_container_width=True):
                if selected_pages:
                    with st.spinner("Creating PDF..."):
                        pdf_bytes = st.session_state.extractor.extract_pages_to_bytes(
                            st.session_state.pdf_path,
                            selected_pages
                        )
                        
                        if pdf_bytes:
                            st.download_button(
                                label="💾 Save PDF",
                                data=pdf_bytes,
                                file_name=f"nightreader_extracted_{uploaded_file.name}",
                                mime="application/pdf",
                                use_container_width=True
                            )
                else:
                    st.warning("No pages selected for extraction")
            
            if st.button("📊 Download Summary CSV", use_container_width=True):
                if selected_pages:
                    with st.spinner("Creating CSV..."):
                        # Create temporary CSV file
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv', mode='w') as tmp_csv:
                            csv_path = tmp_csv.name
                        
                        success = st.session_state.extractor.create_summary_csv(
                            selected_pages,
                            csv_path
                        )
                        
                        if success:
                            with open(csv_path, 'rb') as f:
                                st.download_button(
                                    label="💾 Save CSV",
                                    data=f.read(),
                                    file_name=f"nightreader_summary_{uploaded_file.name}.csv",
                                    mime="text/csv",
                                    use_container_width=True
                                )
                            
                            # Clean up temp file
                            os.unlink(csv_path)
                else:
                    st.warning("No pages selected for extraction")
    
    # Main content area
    if not st.session_state.page_scores:
        # Welcome screen
        st.info("👆 Upload a PDF in the sidebar to get started")
        
        st.markdown("""
        ### How It Works
        
        1. **Upload** your PDF (textbook, research paper, or notes)
        2. **Analyze** the content using TF-IDF and multi-factor scoring
        3. **Review** the density scores and visualizations
        4. **Extract** the highest-value pages
        5. **Download** your optimized PDF and summary
        
        ### Scoring Factors
        
        - **TF-IDF (60%)**: Term frequency-inverse document frequency
        - **Formulas (15%)**: Mathematical expressions and equations
        - **Definitions (15%)**: Key concepts and terminology
        - **Vocabulary (10%)**: Lexical diversity and richness
        
        ### Features
        
        ✅ Fully offline — No external APIs  
        ✅ Works with textbooks, papers, and notes  
        ✅ Interactive visualizations  
        ✅ Automatic filler page detection  
        ✅ Export to PDF and CSV  
        """)
    
    else:
        # Analysis results
        stats = st.session_state.statistics
        
        # Statistics overview
        st.header("📊 Document Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Pages", stats.get('total_pages', 0))
        
        with col2:
            st.metric("Content Pages", stats.get('content_pages', 0))
        
        with col3:
            st.metric("Filler Pages", stats.get('filler_pages', 0))
        
        with col4:
            st.metric("Avg Score", f"{stats.get('avg_score', 0):.4f}")
        
        st.divider()
        
        # Visualizations
        st.header("📈 Content Density Analysis")
        
        # Get current threshold from sidebar (default to 20 if not set)
        threshold_percentage = 20
        if st.session_state.page_scores:
            # This will be updated when user interacts with slider
            pass
        
        # Density score chart
        fig1 = plot_density_scores(st.session_state.page_scores, threshold_percentage)
        if fig1:
            st.plotly_chart(fig1, use_container_width=True)
        
        # Score components chart
        fig2 = plot_score_components(st.session_state.page_scores)
        if fig2:
            st.plotly_chart(fig2, use_container_width=True)
        
        st.divider()
        
        # Page details browser
        st.header("🔍 Page Explorer")
        
        # Get top pages for selection
        top_pages = sorted(
            st.session_state.page_scores,
            key=lambda x: x.total_score,
            reverse=True
        )[:50]  # Show top 50 for selection
        
        page_options = {
            f"Page {ps.page_num} (Score: {ps.total_score:.4f})": ps
            for ps in top_pages
        }
        
        selected_page_label = st.selectbox(
            "Select a page to view details",
            options=list(page_options.keys())
        )
        
        if selected_page_label:
            selected_page = page_options[selected_page_label]
            render_page_details(selected_page)


if __name__ == "__main__":
    main()
