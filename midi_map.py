"""Tell me what I am."""

import mido
import time
import requests
from datadog import statsd

from tonal import Tonal, mapping

output = mido.open_output()
to = Tonal()
mid_range = to.create_sorted_midi("HarmonicMajor", "C")


API_KEY = "3029dd3b274c8f534b16d89a14db6118"
GEO = "40.712784,-74.005941"
call = "https://api.forecast.io/forecast/{0}/{1}"

weather = call.format(API_KEY, GEO)

start = time.time()
max_time = 100

values = dict()
old_values = dict()

chans = dict(
    temp=1,
    app_temp=2,
    dew=3,
    humidity=4,
    visibility=5,
    ozone=6,
    windBearing=7
)


def get_info():
    """Get data."""
    hourly = []
    r = requests.get(weather)
    for i in range(len(r.json()["hourly"]["data"])):
        hourly.append(r.json()["hourly"]["data"][i])
    return hourly


def parse(record):
    """Get data."""
    values.update(temp=record["temperature"])
    values.update(
        app_temp=record["apparentTemperature"])
    values.update(dew=record["dewPoint"])
    values.update(humidity=record["humidity"] * 100)
    values.update(visibility=record["visibility"] * 10)
    values.update(ozone=record["ozone"])
    values.update(ozone=record["windBearing"])

keys = ["temperature", "apparentTemperature", "dewPoint", "humidity",
        "visibility", "ozone", "windBearing"]

while True:
    data = get_info()
    for item in data:
        parse(item)
        for key, value in values.iteritems():
            chan = chans.get(key)
            try:
                output.send(mido.Message(
                    'note_on',
                    note=mapping(value, mid_range),
                    velocity=50,
                    channel=chan))
            except:
                print("error")
            time.sleep(1)
            print(key, value, "note on", chan)
            statsd.gauge(key, value)
    for item in data:
        parse(item)
        for key, value in values.iteritems():
            chan = chans.get(key)
            output.send(mido.Message(
                'note_off',
                note=mapping(value, mid_range),
                channel=chan))
            time.sleep(1)
            print(key, value, "note off", chan)

"""
for x in range(0, 1000):

    note = mapping(random.randint(0, 120), mid_range)
    notea = mapping(note+1, mid_range)
    noteb = mapping(notea+1, mid_range)
    note_2 = mapping(random.randint(0, 120), mid_range)
    vel = random.randint(10, 100)
    vel_2 = random.randint(10, 100)
    output.send(mido.Message('note_on', note=note, velocity=vel, channel=1))
    output.send(mido.Message('note_on', note=notea, velocity=vel, channel=1))
    output.send(mido.Message('note_on', note=noteb, velocity=vel, channel=1))
    print(note, vel)
    time.sleep(4)
    output.send(
        mido.Message(
            'note_on',
            note=note_2,
            velocity=vel_2,
            channel=2
        ))
    print(note_2, vel_2)
    time.sleep(4)
    output.send(mido.Message('note_off', note=note, velocity=vel, channel=1))
    time.sleep(1)
    output.send(
        mido.Message(
            'note_off',
            note=note_2,
            velocity=vel_2,
            channel=2
        ))
    time.sleep(1)
"""
