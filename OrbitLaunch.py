import math
import time
import krpc
import json

turn_start_altitude = 250
turn_end_altitude = 60000
target_altitude = 250000

conn = krpc.connect()
vessel = conn.space_center.active_vessel

# Потоки данных
ut = conn.add_stream(getattr, conn.space_center, "ut")
altitude = conn.add_stream(getattr, vessel.flight(), "mean_altitude")
apoapsis = conn.add_stream(getattr, vessel.orbit, "apoapsis_altitude")
stage_resources = [
    conn.add_stream(
        vessel.resources_in_decouple_stage(stage=i, cumulative=False).amount,
        "LiquidFuel",
    )
    for i in range(3, -1, -1)
]

vessel.control.sas = False
vessel.control.rcs = False
vessel.control.throttle = 1.0

for t in range(3, 0, -1):
    print(f"{t}...")
    time.sleep(1)
print("Поехали!")

# Старт
vessel.control.activate_next_stage()
vessel.auto_pilot.engage()
vessel.auto_pilot.target_pitch_and_heading(90, 90)


flight_data = []
start_time = ut()


def save_flight_data(data, filename="flight_data.json"):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)


# Основной цикл подъема
turn_angle = 0
current_stage = 0
while True:
    if current_stage == 0:
        current_fuel = vessel.resources.amount("LiquidFuel") + vessel.resources.amount(
            "LiquidFuel"
        )
        flight_data.append(
            {
                "time": math.floor(ut() - start_time),
                "altitude": altitude(),
            }
        )
        save_flight_data(flight_data)

    time.sleep(1)

    # Гравитационный поворот
    if turn_start_altitude < altitude() < turn_end_altitude:
        frac = (altitude() - turn_start_altitude) / (
            turn_end_altitude - turn_start_altitude
        )
        new_turn_angle = frac * 90
        if abs(new_turn_angle - turn_angle) > 0.5:
            turn_angle = new_turn_angle
            vessel.auto_pilot.target_pitch_and_heading(90 - turn_angle, 90)

    if apoapsis() > target_altitude * 0.8:
        vessel.control.throttle = 0.7
    if apoapsis() > target_altitude * 0.95:
        vessel.control.throttle = 0.2

    # Проверка топлива и разделение ступеней
    if current_stage < 4 and stage_resources[current_stage]() < 0.05:
        print(f"Отсоединение ступени {current_stage + 1}...")
        vessel.control.activate_next_stage()
        current_stage += 1

    # Завершение подъема
    if apoapsis() > target_altitude:
        print("Достигнут целевой апогей")
        vessel.control.throttle = 0.0
        break

print("Ожидание выхода из атмосферы")
while altitude() < 70500:
    time.sleep(0.1)
print("Ракета покинула атмосферу")

# Планирование циркуляризации
print("Подготовка к выходу на круговую орбиту")
mu = vessel.orbit.body.gravitational_parameter
r = vessel.orbit.apoapsis
a1 = vessel.orbit.semi_major_axis
a2 = r
v1 = math.sqrt(mu * ((2.0 / r) - (1.0 / a1)))
v2 = math.sqrt(mu * ((2.0 / r) - (1.0 / r)))  # r для круговой орбиты
delta_v = v2 - v1
node = vessel.control.add_node(ut() + vessel.orbit.time_to_apoapsis, prograde=delta_v)

# Расчет времени работы двигателей
F = vessel.available_thrust
Isp = vessel.specific_impulse * 9.82

m0 = vessel.mass
m1 = m0 / math.exp(delta_v / Isp)
flow_rate = F / Isp

burn_time = (m0 - m1) / flow_rate

# Ориентация корабля
vessel.auto_pilot.reference_frame = node.reference_frame
vessel.auto_pilot.target_direction = (0, 1, 0)
vessel.auto_pilot.wait()

# Ожидание момента выполнения манёвра
burn_ut = ut() + vessel.orbit.time_to_apoapsis - (burn_time / 2.0)
lead_time = 5  # Время для выхода из TimeWarp перед маневром
conn.space_center.warp_to(burn_ut - lead_time)

while ut() < burn_ut - 0.1:
    time.sleep(0.1)

vessel.control.throttle = 1.0
start_time = ut()

while ut() - start_time < burn_time - 0.1:
    time.sleep(0.1)

vessel.control.throttle = 0.0
node.remove()
print("Целевая орбита достигнута")

for panel in vessel.parts.solar_panels:
    if panel.deployable:
        panel.deployed = True
