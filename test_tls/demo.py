#!/usr/bin/env python

import os
import sys
import optparse

import threading

# we need to import some python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")


from sumolib import checkBinary  # Checks for the binary in environ vars
import traci


def get_options():
    opt_parser = optparse.OptionParser()
    opt_parser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = opt_parser.parse_args()
    return options


# contains TraCI control loop

check_loop = True
check_input = False
input_state = 0


def thread_function(name):
    global input_state
    global check_input
    while check_loop:
        if check_input == False:
            print("input state")
            input_state = input()
            check_input = True
        

def run():
    global check_loop
    global check_input
    step = 0
    traci.trafficlight.setProgram("gneJ1",0)
    
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        # print("Step -> ",step)
        if check_input:
            print("change state to : " , input_state,"\n")
            check_input = False
            # traci.trafficlight.setPhase("gneJ1",input_state)
            traci.trafficlight.setProgram("gneJ1",input_state)

        step += 1

    check_loop = False
    traci.close()
    sys.stdout.flush()


# main entry point
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
