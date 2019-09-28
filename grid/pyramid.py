from typing import Iterable, Iterator, List, Optional, Type

from color import Color, RGB
from model.base import ModelBase

from .cell import Cell, Direction
from .geom import Address, Coordinate, Geometry, Universe
from .grid import Grid, Pixel, Selector
from .face import Face, FULL_FACE_SPEC


class Pyramid:
    """
    Pyramid represents the whole pyramid.

    Shows can access whichever view of the pyramid they like:
    - an individual panel, where the image will be replicated
      on every panel of every face
    - a face (side) of the pyramid, where the image will be
      mirrored on the other side
    """

    faces: List[Face]

    # synthesized grids
    panel: Grid
    face: Grid

    @classmethod
    def build_single(cls,
              model: Type[ModelBase],
              start: Address = Address(Universe(1, 1), 4)) -> "Pyramid":
        face = Face.build(model, [[0]], start)

        return cls([face])


    @classmethod
    def build(cls,
              model: Type[ModelBase],
              start: Address = Address(Universe(1, 1), 4)) -> "Pyramid":
        left_face = Face.build(model, FULL_FACE_SPEC, start)
        right_face = Face.build(model, FULL_FACE_SPEC, left_face.next_address)
        back_face = Face.build(model, [[0]], right_face.next_address)

        return cls([left_face, right_face, back_face])

    def __init__(self, faces: Iterable[Face]):
        # faces: [left, right, back]

        self.faces = list(faces)

        if len(self.faces) == 1:
            pass#            raise ValueError("don't you know a Pyramid has three sides")

        self.panel = PanelReplicator(self.faces)
        self.face = FaceMirror(self.faces[:2])

    @property
    def cells(self) -> List[Cell]:
        cells = []
        for face in self.faces:
            cells.extend(face.cells)
        return cells

    def go(self):
        # there should only really be one model
        self.faces[0].model.go()

    def clear(self, color: Color = RGB(0, 0, 0)):
        for face in self.faces:
            face.clear(color)


class PanelReplicator(Grid):
    """
    Exposes a single panel as a grid, and replicates pixels on every
    panel of every face.
    """

    faces: List[Face]

    _exemplar_face: Face
    _exemplar_panel_geom: Geometry

    def __init__(self, faces: Iterable[Face]):
        self.faces = list(faces)
        if not self.faces:
            raise ValueError('no faces provided to PanelReplicator')

        self.geom = Geometry(origin=Coordinate(0, 0),
                             rows=self.faces[0].panels[0].geom.rows)

        # TODO(lyra): assumes each face has a panel at <0, 0>
        self._exemplar_face = self.faces[0]
        self._exemplar_panel_geom = min(self._exemplar_face.panels,
                                        key=lambda panel: panel.geom.origin).geom
        if self._exemplar_panel_geom.origin != Coordinate(0, 0):
            raise ValueError(
                'Each face must have a panel whose origin is <0, 0>')

        self.model = self._exemplar_face.model
        self.geom = Geometry(origin=Coordinate(0, 0),
                             rows=self._exemplar_panel_geom.rows)

    @property
    def cells(self) -> List[Cell]:
        return [cell
                for cell in self._exemplar_face.cells
                if cell in self._exemplar_panel_geom]

    def _cell(self, coordinate: Coordinate) -> Optional[Cell]:
        if coordinate not in self.geom:
            return None

        return self._exemplar_face._cell(coordinate)

    def pixels(self, sel: Selector, direction: Direction = Direction.NATURAL) -> Iterator[Pixel]:
        for cell in self.select(sel):
            coord = cell.coordinate

            for face in self.faces:
                for panel in face.panels:
                    yield from face.pixels(coord.adjust(*panel.origin), direction)


class FaceReplicator(Grid):
    """
    Treats any number of identically-sized faces as one.
    """

    primary: Face
    replicas: List[Face]

    def __init__(self, faces: Iterable[Face]):
        face_list = list(faces)

        if len({face.geom.rows for face in face_list}) != 1:
            raise ValueError(
                'each replicated Face must have the same geometry')

        self.primary = face_list[0]
        self.replicas = face_list[1:]

    @property
    def geom(self):
        return self.primary.geom

    @property
    def model(self) -> Type[ModelBase]:
        return self.primary.model

    @property
    def cells(self) -> List[Cell]:
        return self.primary.cells

    def _cell(self, coordinate: Coordinate) -> Optional[Cell]:
        return self.primary._cell(coordinate)


class FaceMirror(FaceReplicator):
    """
    Flips the x-coordinate and pixel enumeration direction on all
    mirror faces.
    """

    def pixels(self, sel: Selector, direction: Direction = Direction.NATURAL) -> Iterator[Pixel]:
        for cell in self.primary.select(sel):
            yield from self.primary.pixels(cell, direction)

            mirror_coord = Coordinate(self.geom.width - cell.x - 1, cell.y)
            for face in self.replicas:
                yield from face.pixels(mirror_coord, direction.invert())
