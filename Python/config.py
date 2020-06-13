import datetime

parameters = dict(
    # meters
    distance=10,
    # minutes
    timedelta=15,

    # epsg codes
    sourceEPSG=4326,
    targetEPSG=25832,

    # if starttime or endtime are None, then it automatically use the last 14 days
    starttime='2019-07-01T00:00:00Z',
    endtime='2019-08-01T00:00:00Z'
)