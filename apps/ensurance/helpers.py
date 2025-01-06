from io import BytesIO

import fitz


def insert_image_into_pdf(data: bytes, x: int = 380, y: int = 680, w: int = 200, h: int = 200) -> bytes:
    # Open the PDF
    doc = fitz.open(stream=data, filetype="pdf")

    # Select the last page
    last_page = doc[-1]

    # Create a rectangle specifying position/size
    # (top-left at (x, y), bottom-right at (x + w, y + h))
    image_rect = fitz.Rect(x, y, x + w, y + h)

    # Insert the image into the rectangle
    last_page.insert_image(image_rect, filename="./stamp.png")

    with BytesIO() as output:
        output.write(doc.write())
        return output.getvalue()
