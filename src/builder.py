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


def run_builder(creep):
    """
    Runs a creep as a builder.
    :param creep: The creep to run
    """
    
    # If we're full, stop filling up and remove the saved source as well as any saved targets
    if creep.memory.filling and creep.store.getFreeCapacity() == 0:
        if globals.DEBUG_BUILDERS:
            print(creep.name + " has no more capacity and is done filling.")
        creep.memory.filling = False
        del creep.memory.source
        del creep.memory.target

    # If we're empty, start filling again and remove the saved target
    elif not creep.memory.filling and creep.store.getUsedCapacity() == 0:
        if globals.DEBUG_BUILDERS:
            print(creep.name + " is empty and will start filling.")
        if globals.CREEP_SPEAK:
            creep.say("🔄 harvest")
        creep.memory.filling = True
        del creep.memory.target
        del creep.memory.source
    
    #get the builder target
    # If we have a saved target, use it
    if creep.memory.target:
        target = Game.getObjectById(creep.memory.target)
        if target == None:
            del creep.memory.target
    if not creep.memory.target:
        if globals.DEBUG_BUILDERS:
            print("Selecting targets")
        #if I'm holding exotic materials, go deliver those
        if _.find(creep.store) != undefined and _.find(creep.store) != creep.store.getUsedCapacity(RESOURCE_ENERGY):
            target = globals.getEnergyStorageStructure(creep, True, False, True)
            if globals.DEBUG_BUILDERS and target:
                print(creep.name + " is holding exotic materials, go dump those: " + target.structureType)

        #highest priority is giving some energy to towers that are completely empty, command action is TRANSFER
        if not target:
            target = globals.getTower(creep, 0)
            #target = globals.getTowers(creep, True, True)
            if globals.DEBUG_BUILDERS and target:                
                print(creep.name + " prioritizing filling tower with min energy: " + target.structureType)
        
        #get the closest construction site, command action here is BUILD
        if not target:
            target = _(creep.room.find(FIND_CONSTRUCTION_SITES)).first()
            if globals.DEBUG_BUILDERS and target:                
                print(creep.name + " build target: " + target.structureType)
        
        #Then prioritize filling spawns and extensions with energy, command action is TRANSFER
        if not target:
            target = globals.getEnergyStorageStructure(creep)
            if globals.DEBUG_BUILDERS and target:
                print(creep.name + " refilling energy: " + target.structureType)
        
         #Then fill towers
        if not target:
            target = globals.getTower(creep, 0.9)
            if globals.DEBUG_BUILDERS and target:
                print(creep.name + " filling tower to min viable: " + target.structureType)         

        """
        #Then fill all towers to 100%
        if not target:
            target = globals.getTower(creep, 1)
            if globals.DEBUG_BUILDERS and target:
                print(creep.name + " filling tower to max: " + target.structureType)
        """

        #If there's truly nothing else to do, fill storage. If storage is full, upgrade controller 
        # Command action is upgradeController or TRANSFER
        if not target:                
            target = globals.getEnergyStorageStructure(creep, False, True, True)
            if globals.DEBUG_BUILDERS and target:
                print(creep.name + " transfering energy: " + target.structureType)
        
        if globals.DEBUG_BUILDERS:
            print("Builder target is " + target)
        #set the memory target
        creep.memory.target = target.id

    if creep.memory.filling:
        #we are building or filling a tower, go get the energy from storage if it exists and the spawnLink is empty
        spawnLink = Game.getObjectById(creep.memory.spawnLink)
        if creep.room.storage and creep.room.storage.store.getUsedCapacity(RESOURCE_ENERGY) > 0 and target and not (spawnLink and spawnLink.store.getUsedCapacity(RESOURCE_ENERGY) > 0) and \
            ((target.progress != undefined and target.structureType != STRUCTURE_CONTROLLER) or (target.structureType == STRUCTURE_TOWER and globals.BUILDER_TOWER_ENERGY[creep.pos.roomName])):
            if globals.DEBUG_BUILDERS:
                print("Filling from storage")            
            globals.fillCreep(creep, creep.room.storage)
        else:
            globals.fillCreep(creep)
    else:
        #try to perform the appropriate action and get closer, if the error is that you're not in range, just get closer
        #Check if this a target we need to BUILD
        if target: 
            if target.progress != undefined and target.structureType != STRUCTURE_CONTROLLER:
                if globals.DEBUG_BUILDERS:
                    print("building " + target)
                result = creep.build(target)
                if result == ERR_INVALID_TARGET:
                    #done building
                    del creep.memory.target
                elif result != OK and result != ERR_NOT_IN_RANGE:
                    print("[{}] Unknown result from creep.build({}): {}".format(creep.name, target, result))
                    del creep.memory.target

            elif target.structureType == STRUCTURE_TOWER or target.structureType == STRUCTURE_SPAWN or target.structureType == STRUCTURE_EXTENSION:
                result = creep.transfer(target, RESOURCE_ENERGY)
                if result == OK or result == ERR_FULL:
                    #done transfering
                    del creep.memory.target
                elif result != ERR_NOT_IN_RANGE:
                    print("[{}] Unknown result from creep.transfer({}, {}): {}".format(creep.name, target, RESOURCE_ENERGY, result))
                    del creep.memory.target
            
            #put everything in storage, not just RESOURCE_ENERGY
            elif target.structureType == STRUCTURE_STORAGE:
                result = creep.transfer(target, _.findKey(creep.store))
                if result == OK or result == ERR_FULL:
                    #done transfering
                    del creep.memory.target
                elif result != ERR_NOT_IN_RANGE:
                    print("[{}] Unknown result from transfer to storage: ({}, {}): {}".format(creep.name, target, RESOURCE_ENERGY, result))
                    del creep.memory.target

            elif target.structureType == STRUCTURE_CONTROLLER:
                result = creep.upgradeController(target)
                if result == ERR_INVALID_TARGET:
                    #done upgrading
                    del creep.memory.target
                elif result != ERR_NOT_IN_RANGE and result != OK:
                    print("[{}] Unknown result from creep.upgradeController({}, {}): {}".format(creep.name, target, RESOURCE_ENERGY, result))
                    del creep.memory.target
            else:
                #in this case, the target was likely completed as this creep was on the way
                if globals.DEBUG_BUILDERS:
                    print("Deleting target since it was not here to build")
                del creep.memory.target

            #keep getting closer
            creep.moveTo(target, {"visualizePathStyle": { "stroke": "#ffffff" } }) 