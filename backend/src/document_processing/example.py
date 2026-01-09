from .pipeline import DocumentPipeline, DocumentProcessor

def example_document_processing():
    """Example usage of document processing pipeline"""
    print("=== Document Processing Example ===")

    # Create pipeline
    pipeline = DocumentPipeline()

    # Process a sample text file
    sample_text = """
    This is a sample document for testing the document processing pipeline.
    It contains multiple sentences that will be chunked and processed.

    The pipeline should handle text extraction, chunking, and metadata generation.
    """

    # Create a temporary file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(sample_text)
        temp_file = f.name

    try:
        # Process the file
        result = pipeline.process_file(temp_file)

        print(f"\nProcessing Result:")
        print(f"Status: {result['status']}")
        print(f"File: {result['file_path']}")
        print(f"Chunk Count: {result['chunk_count']}")

        if result['status'] == 'success':
            print("\nSample Chunks:")
            for i, chunk in enumerate(result['chunks'][:2]):  # Show first 2 chunks
                print(f"\nChunk {i+1}:")
                print(f"Text: {chunk['text'][:100]}...")
                print(f"Metadata: {chunk['metadata']}")

    finally:
        # Clean up
        import os
        os.unlink(temp_file)

if __name__ == "__main__":
    example_document_processing()
