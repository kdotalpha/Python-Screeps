import globals
from defs import *

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')

def run_miner(creep):
    """
    Runs a creep as a mineral miner.
    :param creep: The creep to run
    """
    mineral = Game.getObjectById(creep.memory.mineral.id)
    
    # If we're full, stop filling up and remove the saved source as well as any saved targets
    if creep.memory.filling and creep.store.getFreeCapacity() == 0:
        if globals.DEBUG_MINERS:
            print(creep.name + " has no more capacity and is done filling.")
        creep.memory.filling = False
        del creep.memory.source
        del creep.memory.target

    # If we're empty, start filling again and remove the saved target
    elif not creep.memory.filling and creep.store.getUsedCapacity() == 0:
        if globals.DEBUG_MINERS:
            print(creep.name + " is empty and will start filling.")
        if globals.CREEP_SPEAK:
            creep.say("🔄 harvest")
        creep.memory.filling = True
        del creep.memory.target
        del creep.memory.source

    #get the miner target
    # If we have a saved target, use it
    if creep.memory.target:
        target = Game.getObjectById(creep.memory.target)
        if target == None:
            del creep.memory.target
    
    if not creep.memory.target:
        if globals.DEBUG_MINERS:
            print("Selecting targets")
        #if I'm holding exotic materials, go deliver those
        if _.find(creep.store) != undefined and _.find(creep.store) != creep.store.getUsedCapacity(RESOURCE_ENERGY):
            target = globals.getEnergyStorageStructure(creep, True)
            if globals.DEBUG_BUILDERS and target:
                print(creep.name + " is holding exotic materials, go dump those: " + target.structureType)

        #highest priority is giving some energy to towers that are completely empty, command action is TRANSFER
        if not target and mineral:
            target = mineral
            #target = globals.getTowers(creep, True, True)
            if globals.DEBUG_MINERS and target:                
                print(creep.name + " gathering minerals: " + target.mineralType)
        
        creep.memory.target = target.id

    if creep.memory.filling:
        if globals.DEBUG_MINERS:
            print("Filling creep with " + mineral)
        globals.fillCreep(creep, mineral)
    else:
        if target:
            if target.structureType == STRUCTURE_STORAGE:
                result = creep.transfer(target, _.findKey(creep.store))
                if result == OK or result == ERR_FULL:
                    #done transfering
                    del creep.memory.target
                elif result != ERR_NOT_IN_RANGE:
                    print("[{}] Unknown result from transfer to storage: ({}, {}): {}".format(creep.name, target, RESOURCE_ENERGY, result))
                    del creep.memory.target

            creep.moveTo(target, {"visualizePathStyle": { "stroke": "#ffffff" } }) 