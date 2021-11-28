from defs import *
import globals

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')

def run_tower(tower):
    #start by destroying hostile creeps

    #if there is nothing, move on to doing repairs of structures 
    target = globals.getBrokenStructures(tower)
    if globals.DEBUG_TOWERS:
        print("Tower target is " + target.structureType)
    result = tower.repair(target)
    if result != OK and globals.DEBUG_TOWERS:
        print("[{}] Unknown result from tower.repair({}, {}): {}".format(tower.id, target, RESOURCE_ENERGY, result))
