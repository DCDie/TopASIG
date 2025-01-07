from io import BytesIO

import fitz


def insert_image_into_pdf(data: bytes, x: int = 380, y: int = 680, w: int = 200, h: int = 200) -> bytes:
    """
    Insert an image onto the last page of a PDF at a specified location and size.

    This function takes a PDF file represented as a byte stream, inserts an image
    located at a predefined path onto the last page of the PDF in a specific
    rectangle area defined by coordinates and dimensions, and returns the modified
    PDF as a byte stream.

    Parameters:
        data (bytes): The original PDF file as a byte stream.
        x (int): The x-coordinate of the top-left corner of the image's location on
            the last page. Defaults to 380.
        y (int): The y-coordinate of the top-left corner of the image's location on
            the last page. Defaults to 680.
        w (int): The width of the rectangle where the image is inserted. Defaults
            to 200.
        h (int): The height of the rectangle where the image is inserted. Defaults
            to 200.

    Returns:
        bytes: The modified PDF as a byte stream.
    """
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
