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

def fillCreep(creep, customSource = False):
    # If we have a saved source, use it
    if creep.memory.source:
        source = Game.getObjectById(creep.memory.source)
        if source == None:
            del creep.memory.source
            return
    else:
        # Get a random new source and save it
        if customSource:
            source = customSource
        else:
            source = globals.getSource(creep)
        creep.memory.source = source.id

    if creep.pos.isNearTo(source):
        # If we're near the source, harvest it - otherwise, move to it.
        if source.structureType == STRUCTURE_STORAGE or source.structureType == STRUCTURE_LINK:
            creep.say("🔄 withdraw")
            result = creep.withdraw(source, RESOURCE_ENERGY)
        elif source.energyCapacity == undefined:
            creep.say("🔄 pickup")
            result = creep.pickup(source)
        else: 
            result = creep.harvest(source)
        if result == ERR_NOT_ENOUGH_RESOURCES:
            #we've mined this out, stop filling and delete this source
            creep.say("🔄 OOE")
            del creep.memory.source
            creep.memory.filling = False
        elif result != OK:
            print("[{}] Unknown result from creep.harvest({}): {}".format(creep.name, source, result))
            del creep.memory.source
    else:
        #wait if the source is currently being used by someone else, so as not to crowd them in
        waiting = (creep.pos.getRangeTo(source) == 2 and source.pos.findInRange(FIND_MY_CREEPS, 1) != 0)
        #store how long they have been waiting for later debug purposes
        if waiting:
            if creep.memory.waiting:
                creep.memory.waiting += 1
            else:
                creep.memory.waiting = 1
            waiting_creeps = source.pos.findInRange(FIND_MY_CREEPS, 2, {"filter": lambda s: (s.memory.waiting > 1)})
            if waiting_creeps.length > 1:
                #too many creeps waiting, 50/50 find a new source
                if _.random(0,1) == 0:
                    creep.say("🔄 wait")
                    del creep.memory.source
                    del creep.memory.waiting

        #If I'm not waiting, or the source is a dropped resource, move closer
        if not waiting or source.energyCapacity == undefined:
            if source == creep.memory.spawnLink:
                source = Game.getObjectById(source)
            creep.moveTo(source, {"visualizePathStyle": { "stroke": "#ffffff" } })
            del creep.memory.waiting
        


def run_harvester(creep, num_creeps):
    """
    Runs a creep as a generic harvester.
    :param creep: The creep to run
    """
    #increase max_creeps as we build new types of creeps
    #TODO: this currently has a bug where if I'm in multiple rooms, I'm only looking at the max values instead of the values per room when
    #deciding whether or not to build more creeps
    max_creeps = globals.MAX_HARVESTERS + globals.MAX_BUILDERS + globals.MAX_LINKED_PAIRS
    
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

    # If we're full, stop filling up and remove the saved source
    if creep.memory.filling and creep.store.getFreeCapacity() == 0:
        creep.memory.filling = False
        #Harvesters should stick to sources that are next to a link structure, and not move any longer
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
            fillCreep(creep, Game.getObjectById(creep.memory.stickySource))
        else:
            fillCreep(creep)
        if globals.HARVESTER_ROADS:
            try:
                creep.room.createConstructionSite(creep.pos, STRUCTURE_ROAD)
            except:
                pass
    else:
        # If we have a saved target, use it
        if creep.memory.target:
            target = creep.memory.target
        else:
            #if we have a sticky source, we must be next to a link, use that
            if creep.memory.stickySource:
                target = Game.getObjectById(creep.memory.closeLink.id)
                if globals.DEBUG_LINKS:
                    print("Using closeLink: " + target)
            #if there is less than the max number of creeps, put the energy in a spawn/extension that isn't at max energy. Otherwise, pick a random target
            elif num_creeps < max_creeps:
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

        target = Game.getObjectById(creep.memory.target)
        if not target:
            del creep.memory.target
        elif target.store:
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
        elif target:
            creep.moveTo(target, {"visualizePathStyle": { "stroke": "#ffffff" } })
            if globals.HARVESTER_ROADS:
                try:
                    creep.room.createConstructionSite(creep.pos, STRUCTURE_ROAD)
                except:
                    pass