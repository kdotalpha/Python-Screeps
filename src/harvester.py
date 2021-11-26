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


def run_harvester(creep, num_creeps):
    """
    Runs a creep as a generic harvester.
    :param creep: The creep to run
    """
    #increase max_creeps as we build new types of creeps
    #TODO: this currently has a bug where if I'm in multiple rooms, I'm only looking at the max values instead of the values per room when
    #deciding whether or not to build more creeps
    max_creeps = globals.MAX_HARVESTERS + globals.MAX_BUILDERS
    
    # If we're full, stop filling up and remove the saved source
    if creep.memory.filling and creep.store.getFreeCapacity() == 0:
        creep.memory.filling = False
        del creep.memory.source
        if globals.DEBUG_HARVESTERS:
            print(creep.name + " has no more capacity and is done filling.")

    # If we're empty, start filling again and remove the saved target
    elif not creep.memory.filling and creep.store.getUsedCapacity() == 0:
        creep.say("🔄 harvest")
        creep.memory.filling = True
        del creep.memory.target
        if globals.DEBUG_HARVESTERS:
            print(creep.name + " is empty and will start filling.")
        
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
            if globals.HARVESTER_ROADS:
                try:
                    creep.room.createConstructionSite(creep.pos, STRUCTURE_ROAD)
                except:
                    pass
    else:
        # If we have a saved target, use it
        if creep.memory.target:
            target = Game.getObjectById(creep.memory.target)
        else:
            #if there is less than the max number of creeps, put the energy in a spawn/extension that isn't at max energy. Otherwise, pick a random target
            if num_creeps < max_creeps:
                target = globals.getEnergyStorageStructure(creep)
            else: 
                # Get a random new target.
                target = globals.getEnergyStorageStructure(creep, False, True)

            creep.memory.target = target.id
            creep.say("🚧 " + target.structureType)
            if globals.DEBUG_HARVESTERS:
                print(creep.name + " has a new target: " + target.structureType)

        # If we are targeting a spawn or extension, we need to be directly next to it - otherwise, we can be 3 away.
        # Controllers do not have an energy store, so it returns undefined and thus fails out
        if target.store:
            is_close = creep.pos.isNearTo(target)
        else:
            is_close = creep.pos.inRangeTo(target, 3)

        if is_close:
            # If we are targeting a spawn or extension, transfer energy. Otherwise, use upgradeController on it.
            if target.store:
                result = creep.transfer(target, RESOURCE_ENERGY)
                if result == OK or result == ERR_FULL:
                    del creep.memory.target
                else:
                    print("[{}] Unknown result from creep.transfer({}, {}): {}".format(
                        creep.name, target, RESOURCE_ENERGY, result))
            else:
                result = creep.upgradeController(target)
                if result != OK:
                    print("[{}] Unknown result from creep.upgradeController({}): {}".format(
                        creep.name, target, result))
                # Let the creeps get a little bit closer than required to the controller, to make room for other creeps.
                if not creep.pos.inRangeTo(target, 2):
                    creep.moveTo(target, {"visualizePathStyle": { "stroke": "#ffffff" } })
                    if globals.HARVESTER_ROADS:
                        try:
                            creep.room.createConstructionSite(creep.pos, STRUCTURE_ROAD)
                        except:
                            pass
        else:
            creep.moveTo(target, {"visualizePathStyle": { "stroke": "#ffffff" } })
            if globals.HARVESTER_ROADS:
                try:
                    creep.room.createConstructionSite(creep.pos, STRUCTURE_ROAD)
                except:
                    pass