import fitz


def insert_image_into_pdf(input_pdf_path, output_pdf_path, image_path, x=50, y=50, w=200, h=200):
    """
    Inserts an image on the last page of a PDF file at the provided coordinates and size.

    :param input_pdf_path: Path to the original PDF.
    :param output_pdf_path: Path where the modified PDF will be saved.
    :param image_path: Path to the image to insert.
    :param x: X-coordinate (from left) of where to place the image.
    :param y: Y-coordinate (from top) of where to place the image.
    :param w: Width of the image.
    :param h: Height of the image.
    """
    # Open the PDF
    doc = fitz.open(input_pdf_path)

    # Select the last page
    last_page = doc[-1]

    # Create a rectangle specifying position/size
    # (top-left at (x, y), bottom-right at (x + w, y + h))
    image_rect = fitz.Rect(x, y, x + w, y + h)

    # Insert the image into the rectangle
    last_page.insert_image(image_rect, filename=image_path)

    # Save the modified PDF
    doc.save(output_pdf_path)
    doc.close()


# Example usage:
if __name__ == "__main__":
    insert_image_into_pdf(
        input_pdf_path="test.pdf",
        output_pdf_path="with_image.pdf",
        image_path="stamp.png",
        x=470,  # position from left
        y=650,  # position from top
        w=150,  # width of the image
        h=150,  # height of the image
    )
