# NightReader — Intelligent PDF Page Selector

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11-green)
![License](https://img.shields.io/badge/license-MIT-orange)

Automatically extract high-information-density pages from PDFs using TF-IDF analysis and multi-factor content scoring. Perfect for students, researchers, and professionals who need to quickly identify the most valuable pages in textbooks, research papers, and technical documents.

## Features

### Content Scoring Engine
- **TF-IDF Analysis**: Compute term frequency-inverse document frequency for each page
- **Multi-Factor Scoring**: Combine TF-IDF (60%), formula detection (15%), definition patterns (15%), and vocabulary richness (10%)
- **Filler Detection**: Automatically identify and exclude low-value pages (TOC, references, blank pages)
- **Keyword Extraction**: Extract top keywords from each page

### Page Extraction
- **Smart Selection**: Extract top N% of pages by content density
- **Configurable Thresholds**: Set minimum score and percentage filters
- **Summary Reports**: Generate CSV summaries with scores and keywords
- **PDF Export**: Create new PDFs containing only high-value pages

### Interactive UI
- **Streamlit Dashboard**: Clean, modern web interface
- **PDF Viewer**: Preview uploaded documents
- **Density Visualizations**: Interactive bar charts and score breakdowns
- **Page Explorer**: Browse and analyze individual pages
- **One-Click Export**: Download extracted PDFs and summary CSVs

### Technical Highlights
- Fully Offline — No external APIs or cloud services
- Fast Processing — Handles 200+ page documents in seconds
- Versatile — Works with textbooks, research papers, lecture notes
- Accurate — Multi-factor scoring for robust content detection

## Installation

### Prerequisites
- Python 3.11 (recommended for NumPy compatibility)
- pip package manager

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/abhi3114-glitch/NightReader.git
   cd NightReader
   ```

2. **Install dependencies**
   ```bash
   py -3.11 -m pip install -r requirements.txt
   ```

## Usage

### Quick Start

1. **Launch the application**
   ```bash
   py -3.11 -m streamlit run app.py
   ```

2. **Upload your PDF**
   - Click "Browse files" in the sidebar
   - Select a PDF (textbook, paper, or notes)

3. **Analyze content**
   - Click "Analyze PDF" button
   - Wait for processing to complete

4. **Review results**
   - Examine density score visualizations
   - Browse top-ranked pages
   - Explore score components

5. **Export pages**
   - Adjust threshold slider (default: top 20%)
   - Set minimum score filter
   - Download extracted PDF and/or summary CSV

### Example Use Cases

#### Textbook Condensation
Extract key chapters with formulas and definitions from a 500-page textbook:
- Upload textbook PDF
- Set threshold to 15-25%
- Enable "Exclude Filler Pages"
- Download condensed PDF containing only high-density content

#### Research Paper Analysis
Identify core methodology and results sections from academic papers:
- Upload research paper
- Review score breakdown by page
- Extract pages with high definition and formula scores
- Focus reading on extracted pages

#### Lecture Notes Review
Find summary pages and key concept slides from course materials:
- Upload lecture notes PDF
- Set threshold to 30% for broader coverage
- Export pages with highest vocabulary and definition scores
- Use for exam preparation

## How It Works

### 1. Text Extraction
Uses PyMuPDF (fitz) to extract text content from each page with high accuracy.

### 2. TF-IDF Computation
Applies scikit-learn's TfidfVectorizer to calculate term importance:
- **TF (Term Frequency)**: How often terms appear on a page
- **IDF (Inverse Document Frequency)**: How unique terms are across the document
- Higher scores indicate pages with distinctive, information-rich vocabulary

### 3. Multi-Factor Scoring

Each page receives a composite score from four factors:

| Factor | Weight | Detection Method |
|--------|--------|------------------|
| **TF-IDF** | 60% | scikit-learn vectorization |
| **Formulas** | 15% | Regex patterns for math symbols, equations, LaTeX |
| **Definitions** | 15% | Pattern matching for "is defined as", "refers to", etc. |
| **Vocabulary** | 10% | Lexical diversity (unique words / total words) |

### 4. Page Ranking
Pages are sorted by total score, and top N% are selected for extraction.

### 5. Export
Selected pages are extracted into a new PDF while maintaining original formatting and quality.

## Project Structure

```
NightReader/
├── app.py                  # Streamlit UI application
├── pdf_analyzer.py         # Core TF-IDF analysis engine
├── page_extractor.py       # PDF extraction and export
├── text_analyzer.py        # Text analysis utilities
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Technical Architecture

### Core Components

#### PDFAnalyzer (pdf_analyzer.py)
- Extracts text from PDFs using PyMuPDF
- Computes TF-IDF scores using scikit-learn
- Integrates multi-factor content density scoring
- Ranks pages and provides statistics

#### TextAnalyzer (text_analyzer.py)
- Detects mathematical formulas via regex patterns
- Identifies definition patterns in text
- Calculates vocabulary richness (TTR)
- Extracts top keywords per page
- Filters filler content

#### PageExtractor (page_extractor.py)
- Extracts selected pages to new PDF
- Generates CSV summaries with scores
- Creates formatted text reports
- Provides byte output for downloads

#### Streamlit UI (app.py)
- File upload and processing
- Interactive Plotly visualizations
- Page detail explorer
- Export functionality

### Data Flow

```
PDF Upload → Text Extraction → TF-IDF Computation → Multi-Factor Scoring → 
Page Ranking → User Selection → Export (PDF/CSV)
```

## Configuration

### Extraction Thresholds
Adjust in the sidebar:
- **Top %**: 5-100% (default: 20%)
- **Minimum Score**: 0.0-1.0 (default: 0.0)
- **Exclude Filler**: Yes/No (default: Yes)

### Score Weights
Modify in `text_analyzer.py` line 119:
```python
weights = {
    'tfidf': 0.60,      # Adjust TF-IDF weight
    'formulas': 0.15,   # Adjust formula weight
    'definitions': 0.15, # Adjust definition weight
    'vocabulary': 0.10,  # Adjust vocabulary weight
}
```

### TF-IDF Parameters
Modify in `pdf_analyzer.py` line 68:
```python
self.tfidf_vectorizer = TfidfVectorizer(
    max_features=1000,    # Maximum vocabulary size
    stop_words='english', # Language
    ngram_range=(1, 2),   # Unigrams and bigrams
    min_df=1,             # Minimum document frequency
    max_df=0.8,           # Maximum document frequency
)
```

## Performance

### Benchmarks (200-page PDF)
- Text extraction: ~3-5 seconds
- TF-IDF computation: ~1-2 seconds
- Multi-factor scoring: ~2-3 seconds
- PDF export: ~1-2 seconds
- **Total**: ~7-12 seconds

### Memory Usage
- Typical 200-page PDF: ~50-100 MB RAM
- TF-IDF model: ~20-50 MB RAM
- Total estimated: ~100-200 MB RAM

## Troubleshooting

### Issue: "Error extracting text from PDF"
**Solution**: PDF may be image-based or encrypted. Try converting to text-based PDF first.

### Issue: "All pages have zero scores"
**Solution**: PDF contains non-text content or is very short. Check PDF quality and length.

### Issue: "Streamlit won't launch"
**Solution**: Ensure port 8501 is available or specify custom port:
```bash
py -3.11 -m streamlit run app.py --server.port 8502
```

### Issue: "Memory error with large PDFs"
**Solution**: Process PDFs in smaller chunks or increase available RAM.

### Issue: "NumPy compatibility warnings with Python 3.14"
**Solution**: Use Python 3.11 for stable operation:
```bash
py -3.11 -m pip install -r requirements.txt
py -3.11 -m streamlit run app.py
```

## Dependencies

- **PyMuPDF** (>=1.23.0): PDF text extraction
- **scikit-learn** (>=1.3.0): TF-IDF vectorization and NLP
- **numpy** (>=1.24.0): Numerical computations
- **pandas** (>=2.0.0): Data manipulation and CSV export
- **streamlit** (>=1.28.0): Web UI framework
- **plotly** (>=5.17.0): Interactive visualizations

## Future Enhancements

- OCR support for image-based PDFs
- Multi-language support beyond English
- Machine learning classification for content types
- Batch processing for multiple PDFs
- Custom score weight presets
- PDF annotation export

## License

MIT License - Feel free to use, modify, and distribute.

## Author

Built for students, researchers, and knowledge seekers.

---

**NightReader** — Read smarter, not harder.
