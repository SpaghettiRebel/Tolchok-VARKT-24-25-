from astropy import units as u  # для работы с физическими единицами
from astropy.time import Time
from poliastro.bodies import Sun, Earth, Venus  # Импортируем планеты 
from poliastro.ephem import Ephem  # для работы с орбитами
from poliastro.twobody import Orbit  # для работы с двухтелесными орбитами
from poliastro.util import time_range  # для генерации промежутков времени
from itertools import product
from poliastro.maneuver import Maneuver  # для работы с маневрами
from matplotlib import pyplot as plt
from poliastro.plotting import StaticOrbitPlotter  # для визуализации орбит

# Задаем временные параметры отправления и прибытия для миссии
departure_date = Time("1961-04-01", scale="tdb")
arrival_date = departure_date + 2 * u.year

# Генерируем промежутки времени от даты отправления до даты прибытия
epochs = time_range(departure_date, end=arrival_date)  

# Определяем орбиты Земли и Венеры на заданные моменты времени
earth = Ephem.from_body(Earth, epochs=epochs)  # Создаем эфемериды для орбиты Земли
venus = Ephem.from_body(Venus, epochs=epochs)  # Создаем эфемериды для орбиты Венеры

# Создаем орбиты для момента отправления с Земли и прибытия к Венере
earth_departure = Orbit.from_ephem(Sun, earth, departure_date)  
venus_arrival = Orbit.from_ephem(Sun, venus, arrival_date) 

# Генерируем все возможные комбинации типа движения и пути
type_of_motion_and_path = list(product([True, False], repeat=2))

colors_and_styles = [
    color + style for color in ["r", "b"] for style in ["-", "--"]
]

# Вычисляет все возможные орбиты решения задачи Ламберта
def lambert_solution_orbits(ss_departure, ss_arrival, M):
    for (is_prograde, is_lowpath) in type_of_motion_and_path:
        if (is_prograde != is_lowpath):
            continue
        ss_sol = Maneuver.lambert(
            ss_departure,
            ss_arrival,
            M=M,
            prograde=is_prograde,
            lowpath=is_lowpath,
        )
        yield ss_sol

# Создаем сетку 1x1 для графиков
fig, axs = plt.subplots(1, 1, figsize=(8, 8))
a = [1]
for i in a:
    ith_case = 2
    M = 2
    # Отображаем орбиты Земли и Венеры
    op = StaticOrbitPlotter(ax=axs)
    axs.set_title("Mission Trajectory")

    op.plot_body_orbit(Earth, departure_date - 0.193 * u.year)
    op.plot_body_orbit(Venus, arrival_date)

    # Отображаем решения задачи Ламберта для данного сценария
    for ss, colorstyle in zip(
            lambert_solution_orbits(earth_departure, venus_arrival, M=M),
            colors_and_styles,
    ):
        ss_plot_traj = op.plot_maneuver(
            earth_departure, ss, color=colorstyle[0]
        )
plt.show()