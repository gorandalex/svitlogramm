from io import BytesIO

import qrcode


def create_qr_for_url(
        url: str,
        version: int,
        box_size: int,
        border: int,
        fit: bool = True
) -> BytesIO:
    """
    The create_qr_for_url function takes a URL and returns a QR code image of that URL.

    :param url: str: Pass in the url that will be encoded into the qr code
    :param version: int: Specify the size of the qr code
    :param box_size: int: Set the size of each box in the qr code
    :param border: int: Set the border width of the qr code
    :param fit: bool: Determine if the qr code should be fitted to the data
    :return: A bytesio object, which is a file-like
    """
    qr = qrcode.QRCode(
        version=version,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=box_size,
        border=border,
    )
    qr.add_data(url)
    qr.make(fit=fit)
    qr_img = qr.make_image(fill_color="red", back_color="white")

    buffer = BytesIO()
    qr_img.save(buffer)
    buffer.seek(0)

    return buffer
