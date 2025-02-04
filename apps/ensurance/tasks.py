from celery import shared_task
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.ensurance.constants import ContractType, DocumentType, FileTypes
from apps.ensurance.helpers import insert_image_into_pdf
from apps.ensurance.models import File
from apps.ensurance.rca import RcaExportServiceClient


@shared_task
def download_rcai_document(document_id):
    response = RcaExportServiceClient().get_file(
        DocumentId=document_id, DocumentType=DocumentType.CONTRACT, ContractType=ContractType.RCAI
    )
    content = insert_image_into_pdf(response.FileContent)
    file = File.objects.create(
        external_id=document_id,
        type=FileTypes.RCA,
        file=SimpleUploadedFile(f"{document_id}.pdf", content, content_type="application/pdf"),
    )
    return file.id


@shared_task
def download_rcae_document(document_id):
    response = RcaExportServiceClient().get_file(
        DocumentId=document_id, DocumentType=DocumentType.CONTRACT, ContractType=ContractType.CV
    )
    content = insert_image_into_pdf(response.FileContent)
    file = File.objects.create(
        external_id=document_id,
        type=FileTypes.GREEN_CARD,
        file=SimpleUploadedFile(f"{document_id}.pdf", content, content_type="application/pdf"),
    )
    return file.id
