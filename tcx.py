from datetime import datetime
from builder import Builder, ObjectBuilder, SetAttrBuilder, Parser


class Base(object):

    def __init__(self, **attrs):
        for key, value in attrs.items():
            setattr(self, key, value)


class Creator(Base):

    __slots__ = ('name', 'unit_id', 'product_id', 'version_major', 'version_minor', 'build_major', 'build_minor')


class Trackpoint(Base):

    __slots__ = ('time', 'latitude_degrees', 'longitude_degrees', 'altitude_meters', 'distance_meters', 'heart_rate_bpm', 'sensor_state')


class Lap(Base):

    __slots__ = ('start_time', 'total_time_seconds', 'distance_meters', 'maximum_speed', 'calories', 'average_heart_rate_bpm', 'maximum_heart_rate_bpm', 'intensity', 'trigger_method', 'track')


class Activity(Base):

    __slots__ = ('sport', 'id', 'laps', 'creator')


class TCX(Base):

    __slots__ = ('activities')

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
            'SensorState': SetAttrBuilder('sensor_state')})

    def exit(self, object_stack, name):
        trackpoint = object_stack.pop()
        object_stack[-1].append(trackpoint)


class TrackBuilder(ObjectBuilder):

    def __init__(self):
        ObjectBuilder.__init__(self, list, {'Trackpoint': TrackpointBuilder()})

    def exit(self, object_stack, name):
        track = object_stack.pop()
        object_stack[-1].track = track


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
        object_stack.append(Lap(
                start_time=datetime.strptime(attrs.get('StartTime'), '%Y-%m-%dT%H:%M:%SZ'),
                track=[]))

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
        object_stack.append(Activity(
            sport=attrs.get('Sport'),
            laps=[]))

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
