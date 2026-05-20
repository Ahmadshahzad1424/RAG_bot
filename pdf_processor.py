# ========================================
# PART 1: IMPORTS (Tools we need)
# ========================================
from PyPDF2 import PdfReader
# ^ This tool reads PDF files and extracts text

class PDFProcessor:
    """
    This class does ONE job: Read PDFs and break them into chunks
    Think of it like: Read Book → Extract Text → Cut into Paragraphs
    """
    
    def __init__(self, chunk_size=500, overlap=100):
        """
        __init__ = initialization (setup when we create the object)
        
        chunk_size = how many characters in each piece
        Example: 500 means each chunk is ~500 characters (like a paragraph)
        
        overlap = how many characters repeat between chunks
        Why? So we don't lose meaning at chunk boundaries
        
        Example:
        Chunk 1: "This is the beginning of a sentence that"
        Chunk 2: "that continues here and goes further..."
        ^^ "that" appears in both (overlap = shared context)
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def load_pdf(self, pdf_path):
        """
        JOB: Read a PDF file and extract ALL text
        
        INPUT: pdf_path = path to your PDF file (like "sample.pdf")
        OUTPUT: All text from the PDF as one big string
        """
        
        try:
            # Create a PdfReader object that knows how to read PDFs
            reader = PdfReader(pdf_path)
            
            # Empty string to store all text
            text = ""
            
            # Loop through EVERY page in the PDF
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                # Extract text from this page and add to our text
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
                    
            return text  # Give back all the text
        except Exception as e:
            raise ValueError(f"Failed to read PDF file: {str(e)}")
    
    def chunk_text(self, text):
        """
        JOB: Break large text into overlapping chunks
        
        INPUT: text = one big string (from the PDF)
        OUTPUT: list of smaller text pieces
        
        Example:
        If text = "Hello world this is a test"
        chunk_size = 5, overlap = 2
        
        Chunk 1: "Hello" (chars 0-5)
        Chunk 2: "o wo" (chars 3-8, overlaps with chunk 1)
        Chunk 3: "orld" (chars 6-11)
        """
        
        chunks = []  # Empty list to store all chunks
        
        # Loop through the text, jumping by (chunk_size - overlap)
        # Why subtract? Because we want overlap between chunks
        for i in range(0, len(text), self.chunk_size - self.overlap):
            
            # Take a piece from position i to i+chunk_size
            # text[start:end] = grab characters from start to end
            chunk = text[i : i + self.chunk_size]
            
            # Only add if it has actual content
            # chunk.strip() = remove spaces and check if something is left
            if chunk.strip():
                chunks.append(chunk)
        
        return chunks  # Give back list of all chunks
    
    def process(self, pdf_path):
        """
        JOB: Full pipeline - Load PDF → Extract Text → Create Chunks
        
        This is the MAIN function you'll use
        """
        
        print(f"📖 Loading PDF: {pdf_path}")
        text = self.load_pdf(pdf_path)
        print(f"   ✓ Extracted {len(text)} characters")
        
        print(f"\n✂️  Chunking text...")
        chunks = self.chunk_text(text)
        print(f"   ✓ Created {len(chunks)} chunks")
        
        return chunks


# ========================================
# PART 2: TEST IT
# ========================================
if __name__ == "__main__":
    # This code only runs if you run this file directly
    # (not if someone imports it in another file)
    
    # Create a PDFProcessor object
    processor = PDFProcessor(chunk_size=500, overlap=100)
    
    # Process your PDF file
    # Change "sample.pdf" to whatever PDF you have
    chunks = processor.process("sample.pdf")
    
    # Print first 2 chunks so you can see what they look like
    print("\n" + "="*50)
    print("FIRST 2 CHUNKS (preview):")
    print("="*50)
    
    for i, chunk in enumerate(chunks[:2]):
        # Show first 150 characters of each chunk
        print(f"\n--- Chunk {i+1} ---")
        print(chunk[:150] + "...")