from typing import Optional

from libgravatar import Gravatar


async def get_gravatar(email: str) -> Optional[str]:
    """
    The get_gravatar function takes an email address and returns the URL of a gravatar image.
        If no gravatar is found, it returns None.
    
    :param email: str: Pass the email address to the gravatar class
    :return: A string containing the url of the gravatar image
    :doc-author: Trelent
    """
    try:
        return Gravatar(email).get_image()
    except Exception as e:
        print(e)
