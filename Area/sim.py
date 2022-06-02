#!/usr/bin/env python

import traci
from sumolib import checkBinary  # Checks for the binary in environ vars
import os
import sys
import optparse

import threading

import socketio

sio = socketio.Client()

junction_id = 5
check_loop = True
check_input = False
input_state = 0
isAutomode = True
current_control = 4
temp_control = 4


@sio.event
def connect():
    print('connection established : ', sio.sid)


@sio.on('set:phase:sim')
def on_message(data):
    print('I received a message!', data)

    global input_state
    global check_input
    global isAutomode
    global junction_id
    global current_control

    phase = data['phase']
    junction_id = data['junction_id']
    current_control = junction_id

    input_state = phase
    check_input = True


@sio.on('set:mode:sim')
def on_message(data):
    print('I received a message!', data)
    
    global input_state
    global check_input
    global isAutomode
    global junction_id
    global current_control

    mode = data["mode"]
    junction_id = data['junction_id']
    current_control = junction_id

    if mode == 'auto':
        input_state = 0
        print("Auto")
    elif mode == 'manual':
        print("Manual")
        input_state = 1
    elif mode == 'red':
        print("All red")
        input_state = 9
    elif mode == 'flashing':
        print("Flashing")
        input_state = 10
    
    check_input = True







# we need to import some python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")


def get_options():
    opt_parser = optparse.OptionParser()
    opt_parser.add_option("--nogui", action="store_true",
                          default=False, help="run the commandline version of sumo")
    options, args = opt_parser.parse_args()
    return options


def thread_function(name):
    sio.connect('http://161.246.6.1:8017/api')
    global input_state
    global check_input
    
    # while check_loop:
    #     if check_input == False:
    #         print("input state")
    #         input_state = input()
    #         check_input = True


def run():
    global check_loop
    global check_input
    global current_control
    global temp_control

    step = 0
    traci.trafficlight.setProgram("gneJ12", 0)
    traci.trafficlight.setProgram("gneJ15", 0)
    traci.trafficlight.setProgram("gneJ16", 0)

    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        # print("Step -> ",step)
        if check_input:
            # print("change state to : ", input_state, "\n")
            # traci.trafficlight.setProgram('gneJ12', input_state)
            if current_control != temp_control:
                if temp_control == 4:
                    gen = "gneJ12"
                    traci.trafficlight.setProgram(gen, 0)
                elif temp_control == 1:
                    gen = "gneJ15"
                    traci.trafficlight.setProgram(gen, 0)
                elif temp_control == 6:
                    gen = "gneJ16"
                    traci.trafficlight.setProgram(gen, 0)
                temp_control = current_control
                

            gen = "gneJ15"
            if junction_id == 4:
                gen = "gneJ12"
            elif junction_id == 1:
                gen = "gneJ15"
            elif junction_id == 6:
                gen = "gneJ16"

            traci.trafficlight.setProgram(gen, input_state)
            check_input = False

        step += 1

    check_loop = False
    traci.close()
    sys.stdout.flush()


# main 
if __name__ == "__main__":
    options = get_options()

    thread_input = threading.Thread(target=thread_function, args=(1,))
    thread_input.start()

    # check binary
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    # traci starts sumo as a subprocess and then this script connects and runs

    traci.start([sumoBinary, "-c", "sim.sumocfg",
                "--tripinfo-output", "tripinfo.xml"])

    run()
