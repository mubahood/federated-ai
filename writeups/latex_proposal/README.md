# LaTeX Research Proposal

This folder contains the LaTeX source files for the research proposal.

## Quick Start

### Compile the PDF

```bash
./compile.sh
```

This will:
- Clean previous build files
- Run pdflatex three times (for proper TOC and references)
- Generate `main.pdf`
- Automatically open the PDF

### Manual Compilation

If you prefer to compile manually:

```bash
# Update PATH to include LaTeX
eval "$(/usr/libexec/path_helper)"

# Compile (run 3 times for proper references)
pdflatex main.tex
pdflatex main.tex
pdflatex main.tex

# View the PDF
open main.pdf
```

## File Structure

```
latex_proposal/
├── main.tex          # Main LaTeX document
├── compile.sh        # Compilation script
└── README.md         # This file
```

## Requirements

- LaTeX distribution (MacTeX or BasicTeX)
- Already installed on this system: TeX Live 2025

## Document Features

- Professional academic formatting
- Automatic table of contents
- Proper section numbering
- Citation management
- Hyperlinked references
- Page headers and footers
- Abstract with keywords
- Professional title page

## Customization

Edit `main.tex` to modify:
- Content sections
- Bibliography entries
- Document formatting
- Hyperlink colors
- Page layout

## Common Issues

**Issue:** `pdflatex: command not found`  
**Solution:** Run `eval "$(/usr/libexec/path_helper)"` to update PATH

**Issue:** Compilation errors  
**Solution:** Check `main.log` for detailed error messages

**Issue:** Missing packages  
**Solution:** Install with: `sudo tlmgr install <package-name>`

## Output

The compilation produces:
- `main.pdf` - The final document
- `main.aux`, `main.log`, `main.toc` - Auxiliary files (can be deleted)

---

**Author:** Muhindo Mubaraka  
**Date:** November 2025
