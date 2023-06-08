from fastapi import APIRouter

from . import auth
from . import users
from . import images
from . import image_formats
from . import image_comments
from . import image_ratings
from . import tags



router = APIRouter()

router.include_router(auth.router)
router.include_router(users.router)
router.include_router(images.router)
router.include_router(image_formats.router)
router.include_router(image_comments.router)
router.include_router(image_ratings.router)
router.include_router(tags.router)



__all__ = (
    'router',
)