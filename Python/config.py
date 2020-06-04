import datetime

parameters = dict(
    distance=10,
    timedelta=datetime.timedelta(minutes=15),

    sourceEPSG=4326,
    targetEPSG=25832,

    starttime='2019-07-01T00:00:00Z',
    endtime='2019-08-01T00:00:00Z'
)
'''starttime=(datetime.datetime.now()-datetime.timedelta(days=14)).strftime('%Y-%m-%dT%H:%M:%SZ'),
    endtime=(datetime.datetime.now()).strftime('%Y-%m-%dT%H:%M:%SZ')'''