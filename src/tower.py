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

    #if there is nothing, move on to doing repairs of my creeps

    #then finally do repairs of my structures, start with just roads
    target = globals.getBrokenRoad(tower)

    if target and target.structureType == STRUCTURE_ROAD:
        print(tower.id + " fixing road: " + target.structureType)
        result = tower.repair(target)
        if result != OK:
            print("[{}] Unknown result from tower.repair({}, {}): {}".format(tower.id, target, RESOURCE_ENERGY, result))
