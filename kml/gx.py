from kml import _CompoundElement, _SimpleElement

class _GXCompoundElement(_CompoundElement):

    def name(self):
        return 'gx:' + _CompoundElement.name(self)


class _GXSimpleElement(_SimpleElement):

    def name(self):
        return 'gx:' + _SimpleElement.name(self)


class coord(_GXSimpleElement):

    def __init__(self, coord):
        _GXSimpleElement.__init__(self, ' '.join(map(str, coord)))


class MultiTrack(_GXCompoundElement): pass
class SimpleArrayData(_GXCompoundElement): pass
class SimpleArrayField(_GXCompoundElement): pass
class Track(_GXCompoundElement): pass
class value(_GXSimpleElement): pass
