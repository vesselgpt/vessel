from typing import Dict, List, Any
from prefect import flow, task
import base64
import json
from .vessel_client import VesselClient


@task(name="process_input")
async def process_input(input_data: Dict) -> Dict:
    """
    Processes and validates input data
    """
    # Extract and validate input parameters
    if 'document' not in input_data:
        raise ValueError("Document data is required")

    # Get extraction parameters - it's already a dict, no need to parse
    extraction_params = input_data.get('extraction_params', {})

    return {
        'document': input_data['document'],
        'filename': input_data.get('filename', 'unknown'),
        'content_type': input_data.get('content_type', 'application/octet-stream'),
        'extract_tables': extraction_params.get('extract_tables', True),
        'extract_forms': extraction_params.get('extract_forms', True),
        'extract_all': extraction_params.get('extract_all', True)
    }


@task(name="split_document")
async def split_document(document_data: str) -> List[bytes]:
    """
    Splits a base64 encoded document into pages
    """
    # Decode base64 document
    document_bytes = base64.b64decode(document_data)

    # Implementation depends on your document format
    # For example, if it's PDF:
    # from pdf2image import convert_from_bytes
    # pages = convert_from_bytes(document_bytes)

    # Placeholder implementation
    return [document_bytes]  # Return as single page for now


@task(name="extract_data")
async def extract_data(page: bytes, params: Dict, vessel_client: VesselClient) -> Dict:
    """
    Extracts data from a page using Vessel API
    """
    results = {}

    if params.get('extract_tables', True):
        results['table_data'] = await vessel_client.extract_table(page)

    if params.get('extract_forms', True):
        results['form_data'] = await vessel_client.extract_form(page)

    return results


class DocumentProcessingAgent:
    """
    Agent for processing documents using Vessel API.
    """

    def __init__(self):
        self.name = "document_processing"
        self.capabilities = {"document_analysis", "data_extraction"}
        self.vessel_client = VesselClient()

    @flow(name="document_processing_flow")
    async def execute(self, input_data: Dict) -> Dict:
        """
        Main document processing flow
        """
        # Process and validate input
        processed_input = await process_input(input_data)

        # Split document into pages
        pages = await split_document(processed_input['document'])

        # Process each page
        results = []
        for page_num, page in enumerate(pages, 1):
            page_result = await extract_data(
                page,
                processed_input,
                self.vessel_client
            )

            results.append({
                'page_number': page_num,
                'extractions': page_result
            })

        return {
            'filename': processed_input['filename'],
            'total_pages': len(pages),
            'results': results
        }