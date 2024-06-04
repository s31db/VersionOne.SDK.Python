from enum import Enum

from typing import Annotated


class AssetStates(Enum):
    """
    Asset states represent system-known life-cycle stage of an asset.
    The UI typically only show assets that are not "Dead".
    """

    Future: int = 0
    Active: Annotated[
        int, "The asset has been assigned to a user-defined workflow status."
    ] = 64
    Closed: Annotated[int, "The asset has been closed or quick-closed."] = 128
    Template_Dead: Annotated[
        int,
        "The asset is only used to create new copies as part of creating from Templates or Quick Add.",
    ] = 200
    BrokenDown_Dead: Annotated[
        int, "The asset was converted to an Epic for further break-down."
    ] = 208
    Deleted_Dead: Annotated[int, "The asset has been deleted."] = 255
