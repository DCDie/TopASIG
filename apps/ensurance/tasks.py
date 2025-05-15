import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO

import PyPDF2
from celery import shared_task
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.ensurance.constants import DocumentType, FileTypes
from apps.ensurance.donaris import MedicinaAPI
from apps.ensurance.models import File
from apps.ensurance.rca import RcaExportServiceClient


@shared_task
def download_and_merge_documents(document_id, ContractType: str, data: dict | None = None) -> int:
    """
    Download three types of documents (CONTRACT, DEMAND, INSURANCE_POLICY)
    for a given document_id in parallel, merge them into one PDF, and store
    them as a single File instance in the database.
    """
    # The DocumentTypes you want to fetch and merge
    doc_types = [
        DocumentType.CONTRACT,
        DocumentType.DEMAND,
        DocumentType.INSURANCE_POLICY,
    ]

    # Helper function to download and process a single document
    def fetch_and_process(doc_type):
        response = RcaExportServiceClient().get_file(
            DocumentId=document_id,
            DocumentType=doc_type,
            ContractType=ContractType,
        )
        # Insert your watermark/image here
        # processed_pdf_content = insert_image_into_pdf(response.FileContent)
        return doc_type, response.FileContent

    # Download all documents in parallel using a thread pool
    results = {}
    with ThreadPoolExecutor(max_workers=len(doc_types)) as executor:
        future_to_doc_type = {executor.submit(fetch_and_process, dt): dt for dt in doc_types}
        for future in as_completed(future_to_doc_type):
            doc_type = future_to_doc_type[future]
            # future.result() returns (doc_type, processed_pdf_content)
            _, processed_pdf_content = future.result()
            results[doc_type] = processed_pdf_content

    # Initialize a PDF writer to collect/merge pages
    pdf_writer = PyPDF2.PdfWriter()

    # Merge the downloaded PDFs in the specified order
    for dt in doc_types:
        processed_pdf_content = results[dt]
        pdf_reader = PyPDF2.PdfReader(BytesIO(processed_pdf_content))
        for page in pdf_reader.pages:
            pdf_writer.add_page(page)

    # Now, write out the merged PDF to a BytesIO buffer
    merged_stream = BytesIO()
    pdf_writer.write(merged_stream)
    merged_stream.seek(0)  # reset to the beginning

    # Create a Django File object from the merged PDF
    file_content = merged_stream.getvalue()
    merged_file = SimpleUploadedFile(
        f"{document_id}_merged.pdf",
        file_content,
        content_type="application/pdf",
    )

    # Finally, create the File record in your database
    file_obj = File.objects.create(
        external_id=document_id,
        type=FileTypes.RCA if ContractType == "RCAI" else FileTypes.GREEN_CARD,
        file=merged_file,
        # data=json.loads(json.dumps(data, default=lambda o: o.isoformat() if hasattr(o, "isoformat") else o))
        # if data
        # else None,
    )

    return file_obj.id


@shared_task
def download_insurance_policy(document_id) -> int:
    """
    Download the INSURANCE_POLICY document for a given document_id and
    store it as a single File instance in the database.
    """

    # Download the INSURANCE_POLICY document
    response = MedicinaAPI().get_print_forms(
        {
            "DogMEDPH": [
                {
                    "UIN_Dokumenta": document_id,
                }
            ]
        }
    )

    # Extract the files content from the response
    files_content: list = response["Rezulitat_Metoda_medicina_forme_printate"]

    if not files_content:
        raise ValueError("No files found in the response.")

    # Extract files, merge them, and save
    pdf_writer = PyPDF2.PdfWriter()
    for file_content in files_content:
        # Assuming file_content is a base64 string in field "BASE64Str"
        pdf_reader = PyPDF2.PdfReader(BytesIO(base64.b64decode(file_content["BASE64Str"])))
        for page in pdf_reader.pages:
            pdf_writer.add_page(page)
    # Now, write out the merged PDF to a BytesIO buffer
    merged_stream = BytesIO()
    pdf_writer.write(merged_stream)
    merged_stream.seek(0)

    # Create a Django File object from the merged PDF
    file_content = merged_stream.getvalue()
    insurance_policy_file = SimpleUploadedFile(
        f"{document_id}_insurance_policy.pdf",
        file_content,
        content_type="application/pdf",
    )
    # Create a Django File object from the merged PDF
    file_obj = File.objects.create(
        external_id=document_id,
        type=FileTypes.MEDICAL_INSURANCE,
        file=insurance_policy_file,
        data=response["Rezulitat_Metoda_medicina_forme_printate"],
    )

    return file_obj.id
