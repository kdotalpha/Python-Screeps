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
    target = _(tower.room.find(FIND_HOSTILE_CREEPS)).first()
    if target:
        result = tower.attack(target)
        if result != OK and globals.DEBUG_TOWERS:
            print("[{}] Unknown result from tower.attack({}, {}): {}".format(tower.id, target, RESOURCE_ENERGY, result))
    
    #if there is nothing to attack, move on to healing my creeps
    if not target:
        creeps = tower.room.find(FIND_MY_CREEPS)
        for creep in creeps:
            if creep.hits < creep.hitsMax:
                target = creep
                if globals.DEBUG_TOWERS:
                    print("Tower heal target is " + target)
                result = tower.heal(target)
                if result != OK and globals.DEBUG_TOWERS:
                    print("[{}] Unknown result from tower.heal({}, {}): {}".format(tower.id, target, RESOURCE_ENERGY, result))
                break

    #if there is nothing to heal, move on to doing repairs of my structures until we get down to a certain reserve, which we save for killing enemies
    #fix roads before other structures
    #TODO: Create a full structure priority list
    if not target and tower.store.getUsedCapacity(RESOURCE_ENERGY) > globals.TOWER_ENERGY_RESERVE_PERCENTAGE * tower.store.getCapacity(RESOURCE_ENERGY):
        if globals.FIX_ROADS:
            target = globals.getBrokenStructure(tower, True, 1, False, None, STRUCTURE_ROAD)
        if not target:
            #heal ramparts
            target = globals.getBrokenStructure(tower, True, 0.05, True, None, STRUCTURE_RAMPART)
        if not target and globals.FIX_WALLS:
            #heal walls to 5%
            target = globals.getBrokenStructure(tower, True, 0.001, False, None, STRUCTURE_WALL)
        if not target:
            #heal everything else
            target = globals.getBrokenStructure(tower, True, 1, True, STRUCTURE_RAMPART)
        if target:
            if globals.DEBUG_TOWERS:
                print("Tower repair target is " + target.structureType)
            result = tower.repair(target)
            if result != OK and globals.DEBUG_TOWERS:
                print("[{}] Unknown result from tower.repair({}, {}): {}".format(tower.id, target, RESOURCE_ENERGY, result))
    

