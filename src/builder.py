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


def run_builder(creep):
    """
    Runs a creep as a builder.
    :param creep: The creep to run
    :param num_creeps: The total number of creeps in the room
    """
    
    # If we're full, stop filling up and remove the saved source
    if creep.memory.filling and creep.store.getFreeCapacity() == 0:
        if globals.DEBUG_BUILDERS:
            print(creep.name + " has no more capacity and is done filling.")
        creep.memory.filling = False
        del creep.memory.source

    # If we're empty, start filling again and remove the saved target
    elif not creep.memory.filling and creep.store.getUsedCapacity() == 0:
        if globals.DEBUG_BUILDERS:
            print(creep.name + " is empty and will start filling.")
        creep.say("🔄 harvest")
        creep.memory.filling = True
        del creep.memory.target
        
    # calling into creep.memory.X is a boolean, unless you use Game.getObjectById to get the value
    if creep.memory.filling:
        # If we have a saved source, use it
        if creep.memory.source:
            source = Game.getObjectById(creep.memory.source)
        else:
            # Get a new source and save it
            source = globals.getSource(creep)
            creep.memory.source = source.id

        # If we're near the source, harvest it - otherwise, move to it.
        if creep.pos.isNearTo(source):
            result = creep.harvest(source)
            if result != OK:
                print("[{}] Unknown result from creep.harvest({}): {}".format(creep.name, source, result))
        else:
            creep.moveTo(source, {"visualizePathStyle": { "stroke": "#ffffff" } })
    else:
        # If we have a saved target, use it
        if creep.memory.target:
            target = Game.getObjectById(creep.memory.target)
            if not target:
                del creep.memory.target
        else:
            #get the closest construction site, command action here is BUILD
            target = creep.pos.findClosestByPath(FIND_CONSTRUCTION_SITES)
            if globals.DEBUG_BUILDERS and target:                
                print(creep.name + " build target: " + target.structureType)
            
            #If there is nothing to build, prioritize filling towers energy, command action is TRANSFER
            if not target:
                target = globals.getTowers(creep)
                if globals.DEBUG_BUILDERS and target:
                    print(creep.name + " filling tower: " + target.structureType)  
            
            #If there is nothing to build, prioritize filling spawns and extensions with energy, command action is TRANSFER
            if not target:
                target = globals.getEnergyStorageStructure(creep)
                if globals.DEBUG_BUILDERS and target:
                    print(creep.name + " refilling energy: " + target.structureType)
            
            #If there is nothing to fill, fix broken roads, command action is REPAIR
            if not target:                
                target = globals.getBrokenRoad(creep)
                if globals.DEBUG_BUILDERS and target:
                    print(creep.name + " fixing road: " + target.structureType)

            #If there's truly nothing else to do, become a harvester, command action is upgradeController or TRANSFER
            if not target:                
                target = globals.getEnergyStorageStructure(creep, False, True)
                if globals.DEBUG_BUILDERS and target:
                    print(creep.name + " transfering energy: " + target.structureType)

            creep.memory.target = target.id
        
        #try to perform the appropriate action and get closer, if the error is that you're not in range, just get closer
        #Check if this a target we need to BUILD
        if target.progress != undefined:
            result = creep.build(target)
            if result == ERR_INVALID_TARGET:
                #done building
                del creep.memory.target
            elif result != OK and result != ERR_NOT_IN_RANGE:
                print("[{}] Unknown result from creep.build({}): {}".format(creep.name, target, result))

        elif target.structureType == STRUCTURE_TOWER or target.structureType == STRUCTURE_SPAWN or target.structureType == STRUCTURE_EXTENSION:
            result = creep.transfer(target, RESOURCE_ENERGY)
            if result == OK or result == ERR_FULL:
                #done transfering
                del creep.memory.target
            elif result != ERR_NOT_IN_RANGE:
                print("[{}] Unknown result from creep.transfer({}, {}): {}".format(creep.name, target, RESOURCE_ENERGY, result))
        
        #TODO: Update this to repair all of my structures
        elif target.structureType == STRUCTURE_ROAD:
            result = creep.repair(target)
            if result == ERR_INVALID_TARGET:
                #done repairing
                del creep.memory.target
            elif result != ERR_NOT_IN_RANGE:
                print("[{}] Unknown result from creep.repair({}, {}): {}".format(creep.name, target, RESOURCE_ENERGY, result))

        elif target.structureType == STRUCTURE_CONTROLLER:
            result = creep.upgradeController(target)
            if result == ERR_INVALID_TARGET:
                #done upgrading
                del creep.memory.target
            elif result != ERR_NOT_IN_RANGE:
                print("[{}] Unknown result from creep.upgradeController({}, {}): {}".format(creep.name, target, RESOURCE_ENERGY, result))

        #keep getting closer
        creep.moveTo(target, {"visualizePathStyle": { "stroke": "#ffffff" } })

"""
        is_close = True      

        if is_close:
            # If we are targeting a spawn or extension, transfer energy. Otherwise, use upgradeController on it.
            if target != None and target.store:
                result = creep.transfer(target, RESOURCE_ENERGY)
                if result == OK or result == ERR_FULL:
                    del creep.memory.target
                else:
                    print("[{}] Unknown result from creep.transfer({}, {}): {}".format(
                        creep.name, target, RESOURCE_ENERGY, result))
            #otherwise, build it
            else:
                result = creep.build(target)
                #may need to add an OK clause here
                if result == ERR_INVALID_TARGET:
                    del creep.memory.target
                elif result != OK:
                    print("[{}] Unknown result from creep.build({}): {}".format(
                        creep.name, target, result))
                # Let the creeps get a little bit closer than required to the controller, to make room for other creeps.
                if not creep.pos.inRangeTo(target, 1):
                    creep.moveTo(target, {"visualizePathStyle": { "stroke": "#ffffff" } })
        else:
            creep.moveTo(target, {"visualizePathStyle": { "stroke": "#ffffff" } })
"""