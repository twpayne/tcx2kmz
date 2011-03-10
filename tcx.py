#   tcx2kmz TCX functions
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


from datetime import datetime
from builder import Builder, ObjectBuilder, SetAttrBuilder, Parser


class Base(object):

    def __init__(self, **attrs):
        for key, value in attrs.items():
            setattr(self, key, value)


class Creator(Base):

    def __init__(self, **attrs):
        self.name = None
        self.unit_id = None
        self.product_id = None
        self.version_major = None
        self.version_minor = None
        self.build_major = None
        self.build_minor = None
        Base.__init__(self, **attrs)


class Trackpoint(Base):

    def __init__(self, **attrs):
        self.time = None
        self.latitude_degrees = None
        self.longitude_degrees = None
        self.altitude_meters = None
        self.distance_meters = None
        self.heart_rate_bpm = None
        self.cadence = None
        self.sensor_state = None
        Base.__init__(self, **attrs)


class Lap(Base):

    def __init__(self, **attrs):
        self.start_time = None
        self.total_time_seconds = None
        self.distance_meters = None
        self.maximum_speed = None
        self.calories = None
        self.average_heart_rate_bpm = None
        self.maximum_heart_rate_bpm = None
        self.intensity = None
        self.trigger_method = None
        self.track = []
        Base.__init__(self, **attrs)


class Activity(Base):

    def __init__(self, **attrs):
        self.sport = None
        self.id = None
        self.laps = []
        self.creator = None
        Base.__init__(self, **attrs)


class TCX(Base):

    def __init__(self, **attrs):
        self.activities = []
        Base.__init__(self, **attrs)

    @classmethod
    def parse(self, file):
        return Parser(Builder({'TrainingCenterDatabase': TrainingCenterDatabaseBuilder()})).run(file)


class TrackpointBuilder(ObjectBuilder):

    def __init__(self):
        ObjectBuilder.__init__(self, Trackpoint, {
            'Time': SetAttrBuilder('time', lambda s: datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ')),
            'Position': Builder({
                'LatitudeDegrees': SetAttrBuilder('latitude_degrees', float),
                'LongitudeDegrees': SetAttrBuilder('longitude_degrees', float)}),
            'AltitudeMeters': SetAttrBuilder('altitude_meters', float),
            'DistanceMeters': SetAttrBuilder('distance_meters', float),
            'HeartRateBpm': Builder({
                'Value': SetAttrBuilder('heart_rate_bpm', int)}),
            'Cadence': SetAttrBuilder('cadence', int),
            'SensorState': SetAttrBuilder('sensor_state', lambda s: s == 'Present')})

    def exit(self, object_stack, name):
        trackpoint = object_stack.pop()
        object_stack[-1].append(trackpoint)


class TrackBuilder(ObjectBuilder):

    def __init__(self):
        ObjectBuilder.__init__(self, list, {'Trackpoint': TrackpointBuilder()})

    def exit(self, object_stack, name):
        track = object_stack.pop()
        object_stack[-1].tracks.append(track)


class LapBuilder(Builder):

    def __init__(self):
        Builder.__init__(self, {
            'TotalTimeSeconds': SetAttrBuilder('total_time_seconds', float),
            'DistanceMeters': SetAttrBuilder('distance_meters', float),
            'MaximumSpeed': SetAttrBuilder('maximum_speed', float),
            'Calories': SetAttrBuilder('calories', int),
            'AverageHeartRateBpm': Builder({
                'Value': SetAttrBuilder('average_heart_rate_bpm', int)}),
            'MaximumHeartRateBpm': Builder({
                'Value': SetAttrBuilder('maximum_heart_rate_bpm', int)}),
            'Intensity': SetAttrBuilder('intensity'),
            'TriggerMethod': SetAttrBuilder('trigger_method'),
            'Track': TrackBuilder()})
    
    def enter(self, object_stack, name, attrs):
        object_stack.append(Lap(start_time=datetime.strptime(attrs.get('StartTime'), '%Y-%m-%dT%H:%M:%SZ'), tracks=[]))

    def exit(self, object_stack, name):
        lap = object_stack.pop()
        object_stack[-1].laps.append(lap)


class CreatorBuilder(ObjectBuilder):

    def __init__(self):
        ObjectBuilder.__init__(self, Creator, {
            'Name': SetAttrBuilder('name'),
            'UnitId': SetAttrBuilder('unit_id', int),
            'ProductId': SetAttrBuilder('product_id', int),
            'Version': Builder({
                'VersionMajor': SetAttrBuilder('version_major', int),
                'VersionMinor': SetAttrBuilder('version_minor', int),
                'BuildMajor': SetAttrBuilder('build_major', int),
                'BuildMinor': SetAttrBuilder('build_minor', int)})})

    def exit(self, object_stack, name):
        creator = object_stack.pop()
        object_stack[-1].creator = creator


class ActivityBuilder(Builder):

    def __init__(self):
        Builder.__init__(self, {
            'Id': SetAttrBuilder('id'),
            'Lap': LapBuilder(),
            'Creator': CreatorBuilder()})

    def enter(self, object_stack, name, attrs):
        object_stack.append(Activity(sport=attrs.get('Sport')))

    def exit(self, object_stack, name):
        activity = object_stack.pop()
        object_stack[-1].append(activity)


class ActivitiesBuilder(ObjectBuilder):

    def __init__(self):
        ObjectBuilder.__init__(self, list, {'Activity': ActivityBuilder()})

    def exit(self, object_stack, name):
        activities = object_stack.pop()
        object_stack[-1].activities = activities


class TrainingCenterDatabaseBuilder(ObjectBuilder):

    def __init__(self):
        ObjectBuilder.__init__(self, TCX, {'Activities': ActivitiesBuilder()})


if __name__ == '__main__':
    import sys
    import yaml
    print yaml.dump(TCX.parse(sys.stdin))
