import numpy as np
import matplotlib.pyplot as plt
import json


with open('flight_data1.json', encoding='UTF-8') as f:
    user = json.load(f)

time = [user[i]["time"] for i in range(len(user))]
altitude = [user[i]["altitude"] for i in range(len(user))]

plt.plot(time, altitude, color='blue')

plt.xticks(np.arange(0, 103, 20))
plt.yticks(np.arange(0, 32500, 2500))
plt.grid(True)

plt.legend()
plt.show()
