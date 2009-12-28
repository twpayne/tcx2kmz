#   tcx2kmz builder functions
#   Copyright (C) 2009  Tom Payne
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.


from xml.parsers.expat import ParserCreate


class Builder(object):

    def __init__(self, parsers={}):
        self.parsers = parsers

    def enter(self, object_stack, name, attrs):
        pass

    def start_element(self, object_stack, name, attrs):
        return self.parsers.get(name)

    def character_data(self, object_stack, data):
        pass

    def exit(self, object_stack, name):
        pass


class ObjectBuilder(Builder):

    def __init__(self, klass=object, parsers={}):
        Builder.__init__(self, parsers)
        self.klass = klass

    def enter(self, object_stack, name, attrs):
        object_stack.append(self.klass())


class SetAttrBuilder(Builder):

    def __init__(self, attr, transform=str):
        Builder.__init__(self)
        self.attr = attr
        self.transform = transform

    def enter(self, object_stack, name, attrs):
        self.data = []

    def character_data(self, object_stack, data):
        self.data.append(data)

    def exit(self, object_stack, name):
        setattr(object_stack[-1], self.attr, self.transform(''.join(self.data)))


class Parser(object):

    def __init__(self, root_builder):
        self.root_builder = root_builder
        self.parser = ParserCreate()
        self.parser.StartElementHandler = self.start_element
        self.parser.CharacterDataHandler = self.character_data
        self.parser.EndElementHandler = self.end_element

    def start_element(self, name, attrs):
        builder = self.builder_stack[-1]
        if builder:
            builder = builder.start_element(self.object_stack, name, attrs)
        self.builder_stack.append(builder)
        if builder:
            builder.enter(self.object_stack, name, attrs)

    def character_data(self, data):
        builder = self.builder_stack[-1]
        if builder:
            builder.character_data(self.object_stack, data)

    def end_element(self, name):
        builder = self.builder_stack.pop()
        if builder:
            builder.exit(self.object_stack, name)

    def run(self, file):
        self.object_stack = []
        self.builder_stack = [self.root_builder]
        self.parser.ParseFile(file)
        return self.object_stack[-1]
