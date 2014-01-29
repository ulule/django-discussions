from . import base


class Folder(base.Folder):
    class Meta(base.Folder.Meta):
        abstract = False
