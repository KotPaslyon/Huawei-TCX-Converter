# Huawei_TCX_Converter

# Imports
import xml.etree.cElementTree as ET
import math, sys, urllib.request
from datetime import datetime as dt
try:
    import xmlschema
    xmlschema_found = True
except ModuleNotFoundError:
    xmlschema_found = False

def parse_filename():
    input_file = sys.argv[1]

    # Observations
    # TODO: Check that these apply to files generated by other devices
    assert input_file[0:8] == 'HiTrack_' # always starts with HiTrack_
    assert len(input_file[8:]) == 31 # then a couple of timestamps
    assert input_file[34:] == '30001' # then ends with this ???

    # Calculations
    start_time = input_file[8:18]
    end_time = input_file[21:31]
    duration = str(int(end_time)-int(start_time))
    start_time = dt.utcfromtimestamp(int(start_time)).isoformat()+'.000Z'
    end_time = dt.utcfromtimestamp(int(end_time)).isoformat()+'.000Z'
    duration = int(duration)

    # print
    print('---- Information extracted from filename ----')
    print('start: ', end='')
    print(start_time)
    print('end: ', end='')
    print(end_time)
    print('duration: ', end='')
    print(dt.utcfromtimestamp(int(duration)).strftime('%H:%M:%S'))

    return input_file, (start_time, duration)

def read_file(input_file):
    data = []
    with open(input_file) as f:
# Extract useful information from file
# File is made up of 5 sections, but for the moment we're only interested in the
# sections that have associated location data (tp=lbs). We can interpolate heart
# rate, speed, pace etc at these points in the future if we care enough.
#
#    lbs   |   p-m   |   b-p-m   |   h-r   |   rs
# --------------------------------------------------
# location |  pace   |     ?     |  pulse  | speed
#
       for line in f:
           if line[0:6] == 'tp=lbs':

               holding_list = []
               for x in [3,4,6]:
                   holding_list.append(line.split('=')[x].split(';')[0])
               data.append(holding_list)

    return data

def vincenty(point1, point2):
    # WGS 84
    a = 6378137
    f = 1 / 298.257223563
    b = 6356752.314245
    MAX_ITERATIONS = 200
    CONVERGENCE_THRESHOLD = 1e-12
    if point1[0] == point2[0] and point1[1] == point2[1]:
        return 0.0
    U1 = math.atan((1 - f) * math.tan(math.radians(point1[0])))
    U2 = math.atan((1 - f) * math.tan(math.radians(point2[0])))
    L = math.radians(point2[1] - point1[1])
    Lambda = L
    sinU1 = math.sin(U1)
    cosU1 = math.cos(U1)
    sinU2 = math.sin(U2)
    cosU2 = math.cos(U2)
    for iteration in range(MAX_ITERATIONS):
        sinLambda = math.sin(Lambda)
        cosLambda = math.cos(Lambda)
        sinSigma = math.sqrt((cosU2 * sinLambda) ** 2 +
                             (cosU1 * sinU2 - sinU1 * cosU2 * cosLambda) ** 2)
        if sinSigma == 0:
            return 0.0
        cosSigma = sinU1 * sinU2 + cosU1 * cosU2 * cosLambda
        sigma = math.atan2(sinSigma, cosSigma)
        sinAlpha = cosU1 * cosU2 * sinLambda / sinSigma
        cosSqAlpha = 1 - sinAlpha ** 2
        try:
            cos2SigmaM = cosSigma - 2 * sinU1 * sinU2 / cosSqAlpha
        except ZeroDivisionError:
            cos2SigmaM = 0
        C = f / 16 * cosSqAlpha * (4 + f * (4 - 3 * cosSqAlpha))
        LambdaPrev = Lambda
        Lambda = L + (1 - C) * f * sinAlpha * (sigma + C * sinSigma *
                                               (cos2SigmaM + C * cosSigma *
                                                (-1 + 2 * cos2SigmaM ** 2)))
        if abs(Lambda - LambdaPrev) < CONVERGENCE_THRESHOLD:
            break
    else:
        raise ValueError('Error in GPS Coordinates')
        return None  # TODO: Improve handling of convergence failure
    uSq = cosSqAlpha * (a ** 2 - b ** 2) / (b ** 2)
    A = 1 + uSq / 16384 * (4096 + uSq * (-768 + uSq * (320 - 175 * uSq)))
    B = uSq / 1024 * (256 + uSq * (-128 + uSq * (74 - 47 * uSq)))
    deltaSigma = B * sinSigma * (cos2SigmaM + B / 4 * (cosSigma *
                 (-1 + 2 * cos2SigmaM ** 2) - B / 6 * cos2SigmaM *
                 (-3 + 4 * sinSigma ** 2) * (-3 + 4 * cos2SigmaM ** 2)))
    s = b * A * (sigma - deltaSigma)

    return round(s, 6)

def process_data(data, stats):
    total_distance = 0
    # Loop through data line by line
    for n, entry in enumerate(data):
        # Calculate distances between points based on vincenty distances
        # TODO: There must be a better way to do this
        if n == 0:
            entry.append(0)
        else:
            entry.append(vincenty((float(entry[0]),float(entry[1])),
                (float(data[n-1][0]),float(data[n-1][1]))))
        total_distance += entry[-1]
        # Convert timestamps into 2002-05-30T09:30:10Z format
        time = int(float(entry[2])/1000)
        entry[2] = dt.utcfromtimestamp(int(time)).isoformat()+'.000Z'

    print('---- Information extracted from file ----')
    print('location data points: ', end='')
    print(len(data))
    print('distance (approx): ', end='')
    print(int(total_distance), end=' m\n')

    return data, (stats[0], stats[1], int(total_distance))

def generate_xml(data, stats):
    print('---- XML file ----')
    print('generating: ', end='')
    # TrainingCenterDatabase
    TrainingCenterDatabase = ET.Element('TrainingCenterDatabase')
    TrainingCenterDatabase.set('xsi:schemaLocation','http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd')
    TrainingCenterDatabase.set('xmlns', 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2')
    TrainingCenterDatabase.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')

    ## Activities
    Activities = ET.SubElement(TrainingCenterDatabase,'Activities')

    ### Activity
    Activity = ET.SubElement(Activities,'Activity')
    Activity.set('Sport','Running') # TODO: Make an option to change sports?
    Id = ET.SubElement(Activity,'Id')
    Id.text = stats[0] # The StartTime timestamp

    #### Lap
    # TODO: Work out how to split exercises up into laps (by distance?)
    Lap = ET.SubElement(Activity,'Lap')
    Lap.set('StartTime',stats[0]) # start_time
    TotalTimeSeconds = ET.SubElement(Lap,'TotalTimeSeconds')
    TotalTimeSeconds.text = str(stats[1]) # duration
    DistanceMeters = ET.SubElement(Lap,'DistanceMeters')
    DistanceMeters.text = str(stats[2]) # total_distance
    Calories = ET.SubElement(Lap,'Calories')
    Calories.text = '0' # TODO: Can we nullify or get rid of this?
    Intensity = ET.SubElement(Lap,'Intensity')
    Intensity.text = 'Active' # TODO: Can we nullify or get rid of this?
    TriggerMethod = ET.SubElement(Lap,'TriggerMethod')
    TriggerMethod.text = 'Manual' # TODO: How are Laps (or Tracks?) split?
    Track = ET.SubElement(Lap,'Track')

    ##### Track
    distance_holder = 0
    for line in data:
        Trackpoint = ET.SubElement(Track,'Trackpoint')
        Time = ET.SubElement(Trackpoint,'Time')
        Time.text = line[2]
        Position = ET.SubElement(Trackpoint,'Position')
        LatitudeDegrees = ET.SubElement(Position,'LatitudeDegrees')
        LatitudeDegrees.text = line[0]
        LongitudeDegrees = ET.SubElement(Position,'LongitudeDegrees')
        LongitudeDegrees.text = line[1]
        AltitudeMeters = ET.SubElement(Trackpoint,'AltitudeMeters')
        AltitudeMeters.text = '0.0'
        # TODO: Some (all?) Huawei devices don't collect Altitude data, but in that
        # case can we call on some open API to estimate it?
        DistanceMeters = ET.SubElement(Trackpoint,'DistanceMeters')
        distance_holder += line[3]
        DistanceMeters.text = str(distance_holder)
        # TODO: Some Huawei devices might collect the distance between points?

        # TODO: Implement HeartRateBpm
        #HeartRateBpm = ET.SubElement(Trackpoint,'HeartRateBpm')
        #HeartRateBpm.text = '84'

    #### Creator
    # TODO: See if we can scrape this data from other files in the .tar
    Creator = ET.SubElement(Activity,'Creator')
    Creator.set('xsi:type','Device_t')
    Name = ET.SubElement(Creator,'Name')
    Name.text = 'Huawei Fitness Tracking Device'
    UnitId = ET.SubElement(Creator,'UnitId')
    UnitId.text = '0000000000'
    ProductID = ET.SubElement(Creator,'ProductID')
    ProductID.text = '0000'
    Version = ET.SubElement(Creator,'Version')
    VersionMajor = ET.SubElement(Version,'VersionMajor')
    VersionMajor.text = '0'
    VersionMinor = ET.SubElement(Version,'VersionMinor')
    VersionMinor.text = '0'
    BuildMajor = ET.SubElement(Version,'BuildMajor')
    BuildMajor.text = '0'
    BuildMinor = ET.SubElement(Version,'BuildMinor')
    BuildMinor.text = '0'

    ## Author
    Author = ET.SubElement(TrainingCenterDatabase,'Author')
    Author.set('xsi:type','Application_t') # TODO: Check this is right
    Name = ET.SubElement(Author,'Name')
    Name.text = 'Huawei_TCX_Converter'
    Build = ET.SubElement(Author,'Build')
    Version = ET.SubElement(Build,'Version')
    VersionMajor = ET.SubElement(Version,'VersionMajor')
    VersionMajor.text = '1'
    VersionMinor = ET.SubElement(Version,'VersionMinor')
    VersionMinor.text = '0'
    BuildMajor = ET.SubElement(Version,'BuildMajor')
    BuildMajor.text = '1'
    BuildMinor = ET.SubElement(Version,'BuildMinor')
    BuildMinor.text = '0'
    LangID = ET.SubElement(Author,'LangID')
    LangID.text = 'en' # TODO: Translations? Probably not...
    PartNumber = ET.SubElement(Author,'PartNumber')
    PartNumber.text = '000-00000-00'

    print('OKAY')
    return TrainingCenterDatabase

def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def save_xml(TrainingCenterDatabase):
    print('saving: ', end='')
    tree = ET.ElementTree(TrainingCenterDatabase)
    indent(TrainingCenterDatabase)
    new_filename = sys.argv[1][8:]+'.tcx'
    with open(new_filename, 'wb') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>'.encode('utf8'))
        tree.write(f, 'utf-8')
    print('OKAY')

    return new_filename

def validate_xml(filename, xmlschema_found):
    if xmlschema_found:
        print('validating: ', end='')
        # Download and import schema to check against
        url = 'https://www8.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd'
        urllib.request.urlretrieve(url, 'TrainingCenterDatabasev2.xsd')
        schema = xmlschema.XMLSchema('TrainingCenterDatabasev2.xsd')
        # Validate
        try:
            schema.validate(filename)
            print('OKAY')
        except:
            print('FAILED')
    else:
        print('validation requires xmlschema, skipping')

        return

input_file, stats = parse_filename()
data = read_file(input_file)
data, stats = process_data(data, stats)
TrainingCenterDatabase = generate_xml(data, stats)
filename = save_xml(TrainingCenterDatabase)
validate_xml(filename, xmlschema_found)
