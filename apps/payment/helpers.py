from PIL import Image, ImageDraw


def style_eyes(img):
    img_size = img.size[0]
    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rectangle((40, 40, 110, 110), fill=255)
    draw.rectangle((img_size - 110, 40, img_size - 40, 110), fill=255)
    draw.rectangle((40, img_size - 110, 110, img_size - 40), fill=255)
    return mask
