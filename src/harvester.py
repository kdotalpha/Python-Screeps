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


def run_harvester(creep):
    """
    Runs a creep as a generic harvester.
    :param creep: The creep to run
    """
    #increase max_creeps as we build new types of creeps
    #TODO: this currently has a bug where if I'm in multiple rooms, I'm only looking at the max values instead of the values per room when
    #deciding whether or not to build more creeps
    max_creeps = globals.MAX_HARVESTERS[creep.pos.roomName] + globals.MAX_BUILDERS[creep.pos.roomName]

    # Get the number of our creeps in this room.
    creepCount = globals.getMyCreepsInRoom(creep.pos.roomName)
    num_links = creep.room.find(FIND_MY_STRUCTURES, { "filter": lambda s: (s.structureType == STRUCTURE_LINK)}).length
    
    #If this is the first time we've seen this creep, track it as having always been on all roads
    if creep.memory.allRoads == undefined:
        creep.memory.allRoads = True
    #if it has always been on all roads, check to see for every step if it is still walking on roads
    #if it ever steps on something that is not a road, it will remain false for its lifetime
    if creep.memory.allRoads:
        terrain = creep.room.lookAt(creep)
        foundRoad = False
        for thing in terrain:
            if thing.type == LOOK_STRUCTURES and thing.structure.structureType == STRUCTURE_ROAD:
                foundRoad = True
        creep.memory.allRoads = foundRoad
        if foundRoad == False:
            creep.say("No road")

    # If we're full, stop filling up and remove the saved source and any saved targets
    if creep.memory.filling and creep.store.getFreeCapacity() == 0:
        creep.memory.filling = False
        
        #Harvesters should stick to sources that are next to a link structure, and not move any longer, if there are move harvesters than links        
        if creepCount.num_harvesters > num_links - 1:
            closeLink = creep.pos.findInRange(FIND_MY_STRUCTURES, 1, { "filter": lambda s: (s.structureType == STRUCTURE_LINK)})
            if closeLink.length > 0 and closeLink[0].id != creep.memory.spawnLink.id:
                if globals.DEBUG_LINKS:
                    print(creep + " has new sticky source: " + creep.memory.source + " for link " + closeLink[0])
                creep.memory.stickySource = creep.memory.source
                creep.memory.closeLink = closeLink[0]
                creep.say("🔄 sticking")
            else:
                if globals.DEBUG_LINKS:
                    print(creep + " has no link nearby, unsticking")
                del creep.memory.stickySource

        del creep.memory.source
        del creep.memory.target
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
        if creep.memory.stickySource:
            globals.fillCreep(creep, Game.getObjectById(creep.memory.stickySource))
        else:
            globals.fillCreep(creep)
        if globals.HARVESTER_ROADS[creep.pos.roomName]:
            try:
                creep.room.createConstructionSite(creep.pos, STRUCTURE_ROAD)
            except:
                pass
    else:
        # If we have a saved target, use it
        if creep.memory.target:
            target = creep.memory.target
            #if globals.DEBUG_HARVESTERS:
            #    print(creep.name + " is using saved target: " + target)
        else:
            #if we have a sticky source, we must be next to a link, use that
            if creep.memory.stickySource:
                target = Game.getObjectById(creep.memory.closeLink.id)
                if globals.DEBUG_LINKS:
                    print("Using closeLink: " + target)
                if globals.DEBUG_HARVESTERS:
                    print("Sending to link")
            #if the creep is holding a resource that is not RESOURCE_ENERGY, go put that in storage
            elif _.find(creep.store) != undefined and _.find(creep.store) != creep.store.getUsedCapacity(RESOURCE_ENERGY):
                target = globals.getEnergyStorageStructure(creep, True, False, True)
                if globals.DEBUG_HARVESTERS:
                    print("Depositing rare materials")
            #if there is less than the max number of creeps, put the energy in a spawn/extension that isn't at max energy. Otherwise, pick a random target
            elif creepCount.num_creeps < max_creeps:
                if globals.DEBUG_HARVESTERS:
                    print("Less than max # of creeps, prioritizng extensions")
                target = globals.getEnergyStorageStructure(creep)
            else: 
                # Get a random new target.
                if globals.DEBUG_HARVESTERS:
                    print("Picking random target")
                target = globals.getEnergyStorageStructure(creep, False, True)

            creep.memory.target = target.id
            creep.say("🚧 " + target.structureType)
            if globals.DEBUG_HARVESTERS:
                print(creep.name + " has a new target: " + target.structureType)
        
        # If we are targeting a spawn or extension, we need to be directly next to it - otherwise, we can be 3 away.
        # Controllers do not have an energy store, so it returns undefined and thus fails out

        target = Game.getObjectById(creep.memory.target)
        if not target:
            del creep.memory.target
        elif target.store:
            is_close = creep.pos.isNearTo(target)
        else:
            is_close = creep.pos.inRangeTo(target, 3)

        if is_close:
            # If we are targeting a spawn or extension, transfer energy. Otherwise, use upgradeController on it.
            if target.structureType == STRUCTURE_SPAWN or target.structureType == STRUCTURE_EXTENSION or target.structureType == STRUCTURE_LINK:
                result = creep.transfer(target, RESOURCE_ENERGY)
                if result == OK or result == ERR_FULL:
                    del creep.memory.target
                else:
                    print("[{}] Unknown result from creep.transfer({}, {}): {}".format(
                        creep.name, target, RESOURCE_ENERGY, result))
                    del creep.memory.target
            elif target.structureType == STRUCTURE_STORAGE:
                result = creep.transfer(target, _.findKey(creep.store))
                if result != OK:
                    print("[{}] Unknown result from transfer to storage: ({}, {}): {}".format(creep.name, target, RESOURCE_ENERGY, result))
                    del creep.memory.target
            elif target.structureType == STRUCTURE_CONTROLLER:
                result = creep.upgradeController(target)
                if result != OK:
                    print("[{}] Unknown result from creep.upgradeController({}): {}".format(
                        creep.name, target, result))
                    del creep.memory.target
                # Let the creeps get a little bit closer than required to the controller, to make room for other creeps.
                if not creep.pos.inRangeTo(target, 2):
                    creep.moveTo(target, {"visualizePathStyle": { "stroke": "#ffffff" } })
                    if globals.HARVESTER_ROADS[creep.pos.roomName]:
                        try:
                            creep.room.createConstructionSite(creep.pos, STRUCTURE_ROAD)
                        except:
                            pass
        elif target:
            creep.moveTo(target, {"visualizePathStyle": { "stroke": "#ffffff" } })
            if globals.HARVESTER_ROADS[creep.pos.roomName]:
                try:
                    creep.room.createConstructionSite(creep.pos, STRUCTURE_ROAD)
                except:
                    pass