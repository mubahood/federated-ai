#!/bin/bash
# Compile LaTeX document to PDF
# This script handles multiple compilation passes for proper references and TOC

echo "🚀 Starting LaTeX compilation..."

# Update PATH to include LaTeX binaries
eval "$(/usr/libexec/path_helper)"

# Change to the latex_proposal directory
cd "$(dirname "$0")"

# Clean previous build artifacts
echo "🧹 Cleaning previous build files..."
rm -f *.aux *.log *.out *.toc *.bbl *.blg *.pdf

# First pass - generate initial PDF and auxiliary files
echo "📄 First compilation pass..."
pdflatex -interaction=nonstopmode main.tex

# Second pass - resolve references and TOC
echo "📄 Second compilation pass..."
pdflatex -interaction=nonstopmode main.tex

# Third pass - finalize everything
echo "📄 Third compilation pass..."
pdflatex -interaction=nonstopmode main.tex

# Check if PDF was created
if [ -f "main.pdf" ]; then
    echo "✅ SUCCESS! PDF generated: main.pdf"
    echo "📊 File size: $(du -h main.pdf | cut -f1)"
    echo ""
    echo "🔍 Opening PDF..."
    open main.pdf 2>/dev/null || echo "Run 'open main.pdf' to view the document"
else
    echo "❌ ERROR: PDF generation failed!"
    echo "Check the log file for errors:"
    tail -n 50 main.log
    exit 1
fi

echo ""
echo "🎉 Compilation complete!"
