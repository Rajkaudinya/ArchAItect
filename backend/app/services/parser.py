import os
import re
from typing import Dict, Any, List

class DocumentParser:
    @staticmethod
    def parse_txt(file_content: bytes) -> Dict[str, Any]:
        """
        Parses raw text/markdown file, segmenting into logical sections.
        """
        text = file_content.decode("utf-8", errors="ignore")
        
        # Simple heading-based segmentation
        sections = {}
        current_section = "Introduction"
        current_lines = []
        
        lines = text.split("\n")
        for line in lines:
            line_strip = line.strip()
            # Match Markdown headers like #, ##, ###
            header_match = re.match(r"^#{1,6}\s+(.+)$", line_strip)
            if header_match:
                if current_lines:
                    sections[current_section] = "\n".join(current_lines).strip()
                current_section = header_match.group(1)
                current_lines = []
            else:
                current_lines.append(line)
                
        if current_lines:
            sections[current_section] = "\n".join(current_lines).strip()
            
        # Clean empty sections
        sections = {k: v for k, v in sections.items() if v}
        
        if not sections:
            sections["Core Content"] = text
            
        return {
            "success": True,
            "text": text,
            "sections": sections,
            "char_count": len(text),
            "word_count": len(text.split())
        }

    @staticmethod
    def parse_pdf(file_content: bytes) -> Dict[str, Any]:
        """
        Parses PDF files. Falls back if pymupdf is not configured fully, 
        but uses rule-based extraction.
        """
        try:
            import fitz # PyMuPDF
            doc = fitz.open(stream=file_content, filetype="pdf")
            text = ""
            for page in doc:
                text += page.get_text()
            return DocumentParser.parse_txt(text.encode("utf-8"))
        except Exception as e:
            # Fallback/Mock behavior in case PyMuPDF isn't built yet
            return {
                "success": False,
                "error": f"PDF parsing error or PyMuPDF unavailable: {str(e)}",
                "text": "Fallback PDF Text content..."
            }

    @staticmethod
    def parse_docx(file_content: bytes) -> Dict[str, Any]:
        """
        Parses DOCX files using python-docx.
        """
        try:
            import io
            from docx import Document
            doc = Document(io.BytesIO(file_content))
            text = []
            for para in doc.paragraphs:
                text.append(para.text)
            full_text = "\n".join(text)
            return DocumentParser.parse_txt(full_text.encode("utf-8"))
        except Exception as e:
            return {
                "success": False,
                "error": f"DOCX parsing error: {str(e)}",
                "text": "Fallback DOCX text content..."
            }
