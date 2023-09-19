# from openap import Drag, FuelFlow
#
# ALTITUDE = [35000, 37000, 18000, 18000]
# SPEED = [527, 466, 285, 285]
# WIND_SPEED = [55, 55, 55, 55]
# LANDING_GEAR = [False, False, False, True]
# DURATION = [105 * 60, 70 * 60, 1.14 * 3600, 60 * 60]
# MASS = 77000
#
# drag = Drag(ac='A320')
# fuel = FuelFlow(ac='A320', eng='CFM56-5B4')
#
# print(fuel.takeoff(tas=100, alt=0, throttle=1))
#
# print('Mass = {:d} kg'.format(MASS))
# for i, val in enumerate(ALTITUDE):
#     D = drag.nonclean(mass=MASS, tas=SPEED[i] + WIND_SPEED[i], alt=ALTITUDE[i], flap_angle=0, path_angle=0,
#                       landing_gear=LANDING_GEAR[i])
#     FF = fuel.at_thrust(acthr=D, alt=ALTITUDE[i])
#     print('Flying on {0:d} feet, speed = {1:d} kts, landing gear = {2:d}, duration: {3:.0f} min'.
#           format((ALTITUDE[i]), SPEED[i] + WIND_SPEED[i], LANDING_GEAR[i], DURATION[i] / 60))
#     print("Drag : {0:.0f} N".format(D))
#     print("Fuel flow : {0:.4f} kg/s".format(FF))
#     print("Fuel burnt : {0:.0f} kg during {1:.0f} minutes".format(FF * DURATION[i], DURATION[i] / 60))
#     print()

#
# from openap import Thrust, Drag
# thrust = Thrust(ac='A320', eng='CFM56-5B4')
# print('Thrust')
# print(thrust.takeoff(tas=100, alt=0))
# print(thrust.climb(tas=352, alt=20150, roc=1600))
# print(thrust.cruise(tas=230, alt=32000))
#
# drag = Drag(ac='A320')
# print('Drag')
#
#
# for i in range(584, 600, 10):
#     print(i, drag.clean(mass=60000, tas=i, alt=35000), thrust.cruise(tas=i, alt=35000),
#           drag.nonclean(mass=60000, tas=i, alt=35000, flap_angle=0, path_angle=0, landing_gear=False))
#
# print(drag.clean(mass=60000, tas=200, alt=20000))
# print(drag.clean(mass=60000, tas=250, alt=20000))
# print(drag.clean(mass=60000, tas=400, alt=20000))
# print(drag.nonclean(mass=60000, tas=250, alt=20000, flap_angle=20, path_angle=10, landing_gear=False))
# print(drag.nonclean(mass=60000, tas=250, alt=20000, flap_angle=20, path_angle=10, landing_gear=True))

# line = arr[0]
# row = []
# for key, item in line.items():
#     if (type(item) is dict):
#         for key1 in item:
#             row.append(key1)
#     else:
#         row.append(key)
# text_row = ",".join(row)
# rows.append(text_row)
#
# for line in arr:
#     row = []
#     for item in line.items():
#         if (type(item[1]) is dict):
#             for item1 in item[1].items():
#                 row.append(str(item1[1]))
#         else:
#             row.append(str(item[1]))
#     text_row = ",".join(row)
#     rows.append(text_row)
# text = "\n".join(rows)
# with open('sample.csv', 'w') as f:
#     f.write(text)

## track data
import json
import numpy as np
from openap import Drag, FuelFlow, Thrust


def get_corrected_tas(spd: float, alt: float, mass: float, path_angle: float, lgear: bool, thrust: Thrust, drag: Drag) -> float:
    # thr = thrust.cruise(tas=spd, alt=alt)
    # drg = drag.nonclean(mass=mass, tas=spd, alt=alt, flap_angle=0, path_angle=path_angle, landing_gear=lgear)
    for i in range(100, 650, 30):
        print(i, thrust.cruise(tas=i, alt=alt),
              drag.nonclean(mass=mass, tas=i, alt=alt, flap_angle=0, path_angle=path_angle, landing_gear=lgear))
    print()
    return 0


# Opening JSON file
f = open('C:/Users/kuzmi/Downloads/u61383.json')

# returns JSON object as
# a dictionary
data = json.load(f)
arr = data['result']['response']['data']['flight']['track']

rows = []

for line in arr:
    row = []
    for item in line.items():
        if (type(item[1]) is dict):
            for item1 in item[1].items():
                row.append((item1[1]))
        else:
            row.append((item[1]))
    rows.append(row)

nparr = np.array(rows)
# delete the last column
nparr = np.delete(nparr, -1, 1)

ALT = nparr[:, 2]  # knots
SPD = nparr[:, 5]  # ground speed
VSP = nparr[:, 7]  # vertical speed
TST = nparr[:, 11]  # timestamp, epoch time, seconds
MASS = 70000  # initial mass, kg
TST0 = TST[0] - 11*60  # 22:15 - 22:25:58

thrust = Thrust(ac='A320', eng='CFM56-5B4')
drag = Drag(ac='A320')
fuel = FuelFlow(ac='A320', eng='CFM56-5B4')

THRUST_CLIMB = np.zeros((nparr.shape[0], 1))
THRUST_DESCENT = np.zeros((nparr.shape[0], 1))
THRUST_CRUISE = np.zeros((nparr.shape[0], 1))
THRUST = np.zeros((nparr.shape[0], 1))
DRAG = np.zeros((nparr.shape[0], 1))
FF_THRUST_CLIMB = np.zeros((nparr.shape[0], 1))
FF_THRUST_DESCENT = np.zeros((nparr.shape[0], 1))
FF_THRUST_CRUISE = np.zeros((nparr.shape[0], 1))
FF_ENROUTE = np.zeros((nparr.shape[0], 1))
FF_DRAG = np.zeros((nparr.shape[0], 1))
FF_BURNT = np.zeros((nparr.shape[0], 1))

LGEAR = np.zeros((nparr.shape[0], 1), dtype=bool)
LGEAR[434:, 0] = True
tan_values = (nparr[:, 8] / nparr[:, 4] * 3.6)

PATH_ANGLE = np.arctan((nparr[:, 8] / nparr[:, 4] * 3.6).astype(float))

for i in range(nparr.shape[0]):
    # get_corrected_tas(SPD[i], ALT[i], MASS, PATH_ANGLE[i], LGEAR[i, 0], thrust, drag)
    THRUST_CLIMB[i] = thrust.climb(tas=SPD[i], alt=ALT[i], roc=VSP[i])
    THRUST_DESCENT[i] = thrust.descent_idle(tas=SPD[i], alt=ALT[i])
    THRUST_CRUISE[i] = thrust.cruise(tas=SPD[i], alt=ALT[i])
    DRAG[i] = drag.nonclean(mass=MASS, tas=SPD[i], alt=ALT[i], flap_angle=0, path_angle=PATH_ANGLE[i], landing_gear=LGEAR[i])
    FF_THRUST_CLIMB[i] = fuel.at_thrust(acthr=THRUST_CLIMB[i], alt=ALT[i])
    FF_THRUST_DESCENT[i] = fuel.at_thrust(acthr=THRUST_DESCENT[i], alt=ALT[i])
    FF_THRUST_CRUISE[i] = fuel.at_thrust(acthr=THRUST_CRUISE[i], alt=ALT[i])
    FF_ENROUTE[i] = fuel.enroute(MASS, tas=SPD[i], alt=ALT[i], path_angle=PATH_ANGLE[i])
    FF_DRAG[i] = fuel.at_thrust(acthr=DRAG[i], alt=ALT[i])
    dTST = TST[i] - TST0
    TST0 = TST[i]
    if VSP[i] > 200:
        FF_BURNT[i] = FF_THRUST_CLIMB[i]
    elif VSP[i] < -200:
        FF_BURNT[i] = FF_THRUST_DESCENT[i]
    else:
        # FF_BURNT[i] = FF_ENROUTE[i]
        FF_BURNT[i] = FF_THRUST_CRUISE[i]
        #FF_BURNT[i] = FF_DRAG[i]
        #FF_BURNT[i] = (FF_THRUST_CRUISE[i] + FF_DRAG[i]) / 2
    # FF_BURNT[i] = FF_ENROUTE[i]

    # MASS = MASS - FF_BURNT[i, 0]
    print(i, FF_BURNT[i, 0], THRUST_CLIMB[i, 0], THRUST_DESCENT[i, 0], THRUST_CRUISE[i, 0], DRAG[i, 0])

print(np.trapz(FF_BURNT[:, 0], TST))
print(np.trapz(FF_BURNT[:434, 0], TST[:434]))
# print(FF_BURNT[:434].sum())
# print(FF_BURNT.sum())

# thrust.takeoff(tas=100, alt=0)

# Closing file
f.close()
