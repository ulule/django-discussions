from .base import Folder as BaseFolder


class Folder(BaseFolder):
    class Meta(BaseFolder.Meta):
        abstract = False
