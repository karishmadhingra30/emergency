#!/bin/bash
# Quick setup script for PDF-based RAG enhancement

echo "=============================================="
echo "PDF RAG Setup for Emergency First Aid Chatbot"
echo "=============================================="
echo ""

# Check if Docs folder exists
if [ ! -d "Docs" ]; then
    echo "❌ Docs folder not found. Creating it..."
    mkdir -p Docs
    echo "✓ Created Docs folder"
    echo ""
    echo "📝 Next steps:"
    echo "   1. Add your PDF files to the Docs/ folder"
    echo "   2. Run this script again to build the vector database"
    echo ""
    exit 0
fi

# Check if there are any PDFs
pdf_count=$(find Docs -name "*.pdf" -type f | wc -l)
if [ "$pdf_count" -eq 0 ]; then
    echo "⚠️  No PDF files found in Docs/ folder"
    echo ""
    echo "📝 Next steps:"
    echo "   1. Add your first aid PDF files to the Docs/ folder"
    echo "   2. Recommended sources:"
    echo "      - Red Cross First Aid Manual"
    echo "      - WHO Emergency Care Guidelines"
    echo "      - NDMA Disaster Management Handbooks"
    echo "   3. Run this script again"
    echo ""
    exit 0
fi

echo "📚 Found $pdf_count PDF file(s) in Docs/ folder"
echo ""

# Check dependencies
echo "🔍 Checking dependencies..."
python3 -c "import PyPDF2" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  PyPDF2 not installed. Installing dependencies..."
    pip install -q PyPDF2 sentence-transformers faiss-cpu numpy
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies. Please run:"
        echo "   pip install PyPDF2 sentence-transformers faiss-cpu numpy"
        exit 1
    fi
    echo "✓ Dependencies installed"
else
    echo "✓ Dependencies already installed"
fi
echo ""

# Build vector database
echo "🏗️  Building vector database..."
echo "   (This may take a few minutes...)"
echo ""
python3 pdf_processor.py --build

if [ $? -eq 0 ]; then
    echo ""
    echo "=============================================="
    echo "✅ PDF RAG Setup Complete!"
    echo "=============================================="
    echo ""
    echo "📊 Statistics:"
    echo "   - PDF documents: $pdf_count"
    echo "   - Vector database: vectordb/"
    echo ""
    echo "🚀 To start using the enhanced chatbot:"
    echo "   python app.py"
    echo ""
    echo "📖 For more information, see PDF_RAG_GUIDE.md"
else
    echo ""
    echo "❌ Failed to build vector database"
    echo "   Please check the error messages above"
    exit 1
fi
