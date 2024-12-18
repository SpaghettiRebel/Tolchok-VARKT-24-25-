import numpy as np
import matplotlib.pyplot as plt
import math
import json

# Тяга ускорителей
thrust = 1479300

# Диаметр ракеты
diameter = 2.95

# Площадь сечени яракеты
midel_area = math.pi * (diameter / 2) ** 2

# Начальная масса летательного аппарата
mass_0 = 114055
G = 6.6743 * 10 ** (- 11)

# Масса и радиус Кербин
M_E = 5.2915158 * (10 ** 22)
R_E = 600000


# Гравитационное ускорение
def g(height):
    result = ((G * M_E) / ((R_E + height) ** 2))
    return result

with open('flight_temperature.json', encoding='UTF-8') as f:
    T = json.load(f)

# Изменение плотности воздуха по мере взлета
def density(height, time):
    temp = 219
    if time <= 103:
        temp = T[time]["air_temperature"]
    h0 = 0.0
    M = 29 # молярная масса
    R = 8.314 # газовая постоянная
    g = 9.81 # ускорение свободного падения
    rho0 = 1.2  # давление воздуха на уровне моря в кг/м^3

    # Расчет плотности воздуха на текущей высоте
    rho = (rho0 * np.exp(-height * M * g / (R * temp))) * M / (R * temp)

    return rho


def calculate_drag_force(atmosphere_density: float, speed: float, midel_area: float):
    c_x_coef = 0.5
    return c_x_coef * (atmosphere_density * (speed ** 2)) / 2 * midel_area



speed = 0
height = 0
current_rocket_mass = mass_0
fuel_consumption = 479.86

# Время полета ракеты
dt = 1
theoretical_time = list(range(0, 103, 1))

# Список высот полет ракеты
theoretical_height = [height]

for time in theoretical_time:
    # Расчет плотности и давления атмосферы
    atmosphere_density = density(height, time)

    # Расчет текущей массы ракеты
    current_rocket_mass = mass_0 - fuel_consumption * time

    # Расчет текущей силы лобового сопротивления
    current_drag_force = calculate_drag_force(atmosphere_density, speed, midel_area)

    # Расчет изменения скорости
    dv = (thrust - current_drag_force - current_rocket_mass * g(height)) / current_rocket_mass * dt

    # Расчет новой скорости
    previous_speed = speed
    speed = previous_speed + dv
    
    # Расчет высоты полета
    height = height + previous_speed * dt
    theoretical_height.append(height)


plt.xlabel('Время t (сек)')
plt.ylabel('Высота h (м)')
plt.title('Математическая модель')



plt.plot(range(len(theoretical_height)), [height for height in theoretical_height], color="red", label="Math model")
plt.xticks(np.arange(0, 103, 20))
plt.yticks(np.arange(0, 32500, 2500))
plt.grid(True)

plt.show()
