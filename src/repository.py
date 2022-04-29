from typing import Type

class Position(object):
    x: float
    y: float

class Label(object):
    anchor_top: Position
    anchor_bottom: Position
    anchor_left: Position
    anchor_right: Position

    darts = []

class Throw(object):
    throw_id: str
    series_id: str
    dart: str
    label: Label