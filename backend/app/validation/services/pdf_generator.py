"""
Troy — Pure Python PDF Generator
Generates a basic, valid PDF document from raw text streams without external dependencies.
"""

from __future__ import annotations


def generate_pdf(title: str, sections: list[dict[str, str]]) -> bytes:
    """
    Manually compile text data into a valid PDF-1.4 binary stream.
    
    Args:
        title: Title of the document
        sections: List of dicts, each with "heading" and "text" keys.
    """
    text_lines = []
    text_lines.append("BT")
    text_lines.append("/F1 16 Tf")
    text_lines.append("18 TL")
    text_lines.append("50 780 Td")
    
    # Escaped title
    escaped_title = title.upper().replace("(", "\\(").replace(")", "\\)")
    text_lines.append(f"({escaped_title}) Tj T*")
    text_lines.append("18 TL T*")  # spacing
    
    text_lines.append("/F1 10 Tf")
    text_lines.append("12 TL")
    
    for section in sections:
        heading = section.get("heading", "")
        text = section.get("text", "")
        
        if heading:
            text_lines.append("/F1 12 Tf")
            text_lines.append("14 TL T*")
            escaped_h = heading.replace("(", "\\(").replace(")", "\\)")
            text_lines.append(f"({escaped_h}) Tj T*")
            text_lines.append("/F1 10 Tf")
            text_lines.append("12 TL")
            
        for line in text.split("\n"):
            line = line.strip()
            if not line:
                text_lines.append("T*")
                continue
            
            # Wrap lines very simplistically (e.g. 80 chars max)
            chunks = [line[i:i+80] for i in range(0, len(line), 80)]
            for chunk in chunks:
                escaped_c = chunk.replace("(", "\\(").replace(")", "\\)")
                text_lines.append(f"({escaped_c}) Tj T*")
                
    text_lines.append("ET")
    
    stream_content = "\n".join(text_lines)
    stream_bytes = stream_content.encode("utf-8")
    
    # Construct PDF structure objects
    objects = []
    # 1: Catalog
    objects.append("1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj")
    # 2: Pages list
    objects.append("2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj")
    # 3: Page resource definitions
    objects.append("3 0 obj\n<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 5 0 R >> >> /MediaBox [0 0 595 842] /Contents 4 0 R >>\nendobj")
    # 4: Stream content object
    objects.append(f"4 0 obj\n<< /Length {len(stream_bytes)} >>\nstream\n{stream_content}\nendstream\nendobj")
    # 5: Standard Helvetica font object
    objects.append("5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj")
    
    # Compile document and record file byte offsets for cross-reference tables
    pdf_header = "%PDF-1.4\n"
    pdf_data = pdf_header.encode("utf-8")
    
    offsets = []
    for obj in objects:
        offsets.append(len(pdf_data))
        pdf_data += (obj + "\n").encode("utf-8")
        
    xref_offset = len(pdf_data)
    
    # Cross-reference table
    xref_text = f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n"
    for offset in offsets:
        xref_text += f"{offset:010d} 00000 n \n"
        
    xref_text += f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n"
    
    pdf_data += xref_text.encode("utf-8")
    return pdf_data
