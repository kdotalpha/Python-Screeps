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
            # Get a random new source and save it
            source = globals.getSource(creep)
            #source = _.sample(creep.room.find(FIND_SOURCES))
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
            debug_msg = False
            target = _(creep.room.find(FIND_CONSTRUCTION_SITES)).first()
            if globals.DEBUG_BUILDERS and target and not debug_msg:                
                print(creep.name + " build target is: " + target.structureType)
                debug_msg = True
            
            #If there is nothing to build, prioritize filling towers energy
            if not target:
                target = _(creep.room.find(FIND_STRUCTURES)) \
                    .filter(lambda s: ((s.structureType == STRUCTURE_TOWER) and s.store.getFreeCapacity(RESOURCE_ENERGY) > 0)) \
                    .first()
            if globals.DEBUG_BUILDERS and target and not debug_msg:
                debug_msg = True
                print(creep.name + " has nothing to build, so energy target is: " + target.structureType)
            
            #If there is nothing to build, prioritize filling spawns and extensions with energy
            if not target:
                target = _(creep.room.find(FIND_STRUCTURES)) \
                    .filter(lambda s: ((s.structureType == STRUCTURE_SPAWN or s.structureType == STRUCTURE_EXTENSION)
                                        and s.store.getFreeCapacity(RESOURCE_ENERGY) > 0)) \
                    .first()
            if globals.DEBUG_BUILDERS and target and not debug_msg:
                debug_msg = True
                print(creep.name + " has nothing to build, so energy target is: " + target.structureType)
            
            if not target:
                #If there is nothing to fill, get out of the way
                target = _(creep.room.find(FIND_STRUCTURES)) \
                    .filter(lambda s: ((s.structureType == STRUCTURE_SPAWN or s.structureType == STRUCTURE_EXTENSION))) \
                    .sample()
            if globals.DEBUG_BUILDERS and target and not debug_msg:
                debug_msg = True
                print(creep.name + " has nothing to build and nothing needs energy, so get out of the way: " + target.structureType)

            creep.memory.target = target.id

        # If we are targeting a spawn or extension, we need to be directly next to it - otherwise, we can be 3 away.
        # Controllers do not have an energy store, so it returns undefined and thus fails out
        if target != None and target.store:
            is_close = creep.pos.isNearTo(target)
        else:
            is_close = creep.pos.inRangeTo(target, 3)

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