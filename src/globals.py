# defs is a package which claims to export all constants and some JavaScript objects, but in reality does
#  nothing. This is useful mainly when using an editor like PyCharm, so that it 'knows' that things like Object, Creep,
#  Game, etc. do exist.
from defs import *
# These are currently required for Transcrypt in order to use the following names in JavaScript.
# Without the 'noalias' pragma, each of the following would be translated into something like 'py_Infinity' or
#  'py_keys' in the output file.
__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')


CONTROLLED_ROOMS = ["E26S42"]
#TEST = { CONTROLLED_ROOMS[0]: True }
#roomName = spawn.pos.roomName
#print(globals.TEST[roomName])

#do builders use storage energy when refilling towers
BUILDER_TOWER_ENERGY = { CONTROLLED_ROOMS[0]: False }
#do harvesters tell builders where to put roads in a room
HARVESTER_ROADS = { CONTROLLED_ROOMS[0]: False }
#do towers fix roads
FIX_ROADS = { CONTROLLED_ROOMS[0]: True }
#do towers fix walls
FIX_WALLS = { CONTROLLED_ROOMS[0]: True }
#do harvesters/builders mine minerals
MINE_MINERALS = { CONTROLLED_ROOMS[0]: False }

MAX_HARVESTERS = { CONTROLLED_ROOMS[0]: 3 }
MAX_BUILDERS = { CONTROLLED_ROOMS[0]: 2 }

TOWER_ENERGY_RESERVE_PERCENTAGE = { CONTROLLED_ROOMS[0]: 0.3 }
HARVESTER_BUILDER_MAX_POWER = { CONTROLLED_ROOMS[0]: 1800 }
HARVESTER_BUILDER_MIN_POWER = { CONTROLLED_ROOMS[0]: 300 }
MAX_CREEP_WAIT = { CONTROLLED_ROOMS[0]: 50 }

#debugs
DEBUG_HARVESTERS = True
DEBUG_CREEP_CREATION = True
DEBUG_BUILDERS = False
DEBUG_SOURCE_SELECTION = False
DEBUG_TOWERS = False
DEBUG_LINKS = False



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
            source = getSource(creep)
        creep.memory.source = source.id

    if creep.pos.isNearTo(source):
        # If we're near the source, harvest it - otherwise, move to it.
        if source.structureType == STRUCTURE_STORAGE or source.structureType == STRUCTURE_LINK:
            creep.say("🔄 withdraw")
            result = creep.withdraw(source, RESOURCE_ENERGY)
        #this is a tombstone
        elif source.deathTime != undefined and _.find(source.store) != undefined:
            creep.say("🔄 tombstone")
            result = creep.withdraw(source, _.findKey(source.store))
        elif source.structureType == STRUCTURE_EXTRACTOR:
            creep.say("🔄 minerals")
            result = creep.harvest(source)
        #this is a dropped resource
        elif source.resourceType != undefined:
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
            #stick around if it is a mineral in cooldown
            if result == ERR_TIRED and source.mineralAmount != undefined:
                pass
            else:
                print("[{}] Unknown result from creep.harvest({}): {}".format(creep.name, source, result))
                del creep.memory.source
    else:
        #wait if the source is currently being used by someone else, so as not to crowd them in, but only do this if it is a real source or a mineral
        waiting = (creep.pos.getRangeTo(source) == 2 and source.pos.findInRange(FIND_MY_CREEPS, 1) != 0 and (source.ticksToRegeneration or source.mineralType))
        #store how long they have been waiting for later debug purposes
        if waiting:
            if creep.memory.waiting:
                creep.memory.waiting += 1
            else:
                creep.memory.waiting = 1
            waiting_creeps = source.pos.findInRange(FIND_MY_CREEPS, 2, {"filter": lambda s: (s.memory.waiting > 1)})
            if waiting_creeps.length > 1 or creep.memory.waiting >= MAX_CREEP_WAIT[creep.pos.roomName]:
                #too many creeps waiting, 50/50 find a new source
                if _.random(0,1) == 0:
                    creep.say("🔄 wait")
                    del creep.memory.source
                    del creep.memory.waiting

        #If I'm not waiting, or the source is a dropped resource and not a mineral, move closer
        if not waiting or (source.energyCapacity == undefined and source.mineralType == undefined):
            if source == creep.memory.spawnLink:
                source = Game.getObjectById(source)
            creep.moveTo(source, {"visualizePathStyle": { "stroke": "#ffffff" } })
            del creep.memory.waiting

def getMyCreepsInRoom(roomName):
    num_creeps = 0
    num_harvesters = 0
    num_builders = 0
    for name in Object.keys(Game.creeps):
        countCreep = Game.creeps[name]
        if countCreep.pos.roomName == roomName:
            if countCreep.memory.role == "harvester":
                num_harvesters += 1
            elif countCreep.memory.role == "builder":
                num_builders += 1
    num_creeps = num_harvesters + num_builders

    return { "num_creeps": num_creeps, 
            "num_harvesters": num_harvesters, 
            "num_builders": num_builders }

def getSource(creep):
    #If there is a dropped source, just go there
    dropped_sources = _(creep.room.find(FIND_DROPPED_RESOURCES)).first()
    if dropped_sources:
        if DEBUG_SOURCE_SELECTION:
            print("Picking up dropped resources")
        return dropped_sources
    
    #then go to tombstones
    tombstones = creep.room.find(FIND_TOMBSTONES)
    if tombstones:
        for tombstone in tombstones:
            if _.find(tombstone.store):
                if DEBUG_SOURCE_SELECTION:
                    print("Picking up from tombstone")
                return tombstone
    
    #if the creep knows the spawn link and it has available energy, gather from the spawnLink
    if creep.memory.spawnLink:
        spawnLink = Game.getObjectById(creep.memory.spawnLink.id)
        if DEBUG_LINKS:
            print("Selecting sources, creep spawn link is: " + spawnLink)
        if spawnLink and spawnLink.store.getUsedCapacity(RESOURCE_ENERGY) > 0:
            if DEBUG_SOURCE_SELECTION:
                print("Gathering energy from spawn link")
            return creep.memory.spawnLink

    sources = creep.room.find(FIND_SOURCES, {"filter": lambda s: ((s.energy > 0))})
    unusedSources = []
    for source in sources:
        if source.pos.findInRange(FIND_MY_CREEPS, 1).length == 0 and source.energy > 0:
            unusedSources.append(source)
            if DEBUG_SOURCE_SELECTION:
                print("Unused sources: " + unusedSources + " with count " + unusedSources.length)
    
    range = 99999999
    if unusedSources.length > 0:
        #If there are sources with no one around, go to those
        for s in unusedSources:
            source_range = creep.pos.getRangeTo(s)
            if DEBUG_SOURCE_SELECTION:
                print("Range to " + s + " is " + source_range)
            if source_range < range:
                target = s
                range = source_range
        if DEBUG_SOURCE_SELECTION:
            print("Selected closest target is " + target)
        return target
    else:
        #otherwise go to a source that doesn't have a link and a creep
        if DEBUG_SOURCE_SELECTION:
            print("Both sources taken, picking random non-link source")
        waitSources = []
        for source in sources:
            #If the source has a creep and a link nearby, don't go there
            if not (source.pos.findInRange(FIND_MY_CREEPS, 1).length > 0 and \
                source.pos.findInRange(FIND_MY_STRUCTURES, 2, { "filter": lambda s: (s.structureType == STRUCTURE_LINK)}).length > 0):
                waitSources.append(source)
        #if there is truly nothing else to gather, check for minerals to extract
        if waitSources.length == 0:
            if MINE_MINERALS[creep.pos.roomName]:
                if DEBUG_SOURCE_SELECTION:
                    print("checking for minerals")
                minerals = getExtractableMinerals(creep.room)
                if DEBUG_SOURCE_SELECTION:
                    print("minerals: " + minerals)
                if minerals:
                    return minerals
            #if there is no energy in sources and there are no minerals to extract, check if storage has energy
            if creep.room.storage and creep.room.storage.store.getUsedCapacity(RESOURCE_ENERGY) > 0:
                return creep.room.storage
            
            #If there's just no energy and no minerals, return None
            return None
                
        return waitSources[_.random(0, waitSources.length - 1)]

def getExtractableMinerals(room):
    #check to see if there is a mineral in the room
    #if yes, check if there is an extractor at the same position
    #if so, return it. If not, return None The game mandates there is only ever 1 type of mineral in a room

    mineral = _(room.find(FIND_MINERALS, { "filter": lambda s: ((s.mineralAmount > 0))})).first()
    if DEBUG_SOURCE_SELECTION:
        print(mineral.pos)
    if mineral.pos:
        extractor = _(room.find(FIND_MY_STRUCTURES, {"filter": lambda s: ((s.structureType == STRUCTURE_EXTRACTOR and s.pos.x == mineral.pos.x and s.pos.y == mineral.pos.y))})).first()
        print(extractor)
    if extractor:
        return mineral
    return None

def getSpawnLink(spawn):
    link = spawn.pos.findClosestByRange(FIND_MY_STRUCTURES, { "filter": lambda s: ((s.structureType == STRUCTURE_LINK))})
    #if DEBUG_LINKS:
    #    print("Spawn link is " + link)
    return link

def getBrokenStructure(creep, closest=True, hitsMinPercentage=1, myStructures = True, avoidStructureType = None, structureType = None):
    """
    Gets a structure in the same room as a creep with hits less than hitsMinPercentage of max hits
    :param creep: The creep to run
    :param closest: Whether to find the closest road
    :param hitsMinPercentage: The percentage to repair the road up to, between 0 and 1
    :param structureType: The the specific structureType to look for. If None, look for anything
    :param avoidStructureType: Look for any structures besides the one specified. If provided, ignores structureType
    """
    if myStructures:
        FIND_CONSTANT = FIND_MY_STRUCTURES
    else:
        FIND_CONSTANT = FIND_STRUCTURES
        
    if structureType == None and avoidStructureType == None:
        if DEBUG_TOWERS:
            print("Getting first broken structure")
        if not closest:
            return _(creep.room.find(FIND_CONSTANT)) \
                        .filter(lambda s: (s.hits < (s.hitsMax * hitsMinPercentage))) \
                        .first()
        else:
            return creep.pos.findClosestByRange(FIND_CONSTANT, { "filter": lambda s: ((s.hits < (s.hitsMax * hitsMinPercentage))) })
    if avoidStructureType != None:
        if DEBUG_TOWERS:
            print("Avoiding structure type: " + avoidStructureType)
        if not closest:
            return _(creep.room.find(FIND_CONSTANT)) \
                        .filter(lambda s: ((s.hits < (s.hitsMax * hitsMinPercentage) and s.structureType != avoidStructureType))) \
                        .first()
        else:
            return creep.pos.findClosestByRange(FIND_CONSTANT, { "filter": lambda s: ((s.hits < (s.hitsMax * hitsMinPercentage) and s.structureType != avoidStructureType)) })
    if structureType != None:
        if DEBUG_TOWERS:
            print("Finding first broken structure of type: " + structureType)
        if not closest:
            return _(creep.room.find(FIND_CONSTANT)) \
                        .filter(lambda s: ((s.hits < (s.hitsMax * hitsMinPercentage) and s.structureType == structureType))) \
                        .first()
    if DEBUG_TOWERS:
        print("Finding closest broken structure")
    return creep.pos.findClosestByRange(FIND_CONSTANT, { "filter": lambda s: ((s.hits < (s.hitsMax * hitsMinPercentage) and s.structureType == structureType)) })

def getTower(creep, maxEnergyPercentage = 0.6):
    """
    Gets the closest tower in the same room as a creep
    :param creep: The creep to run
    :param maxEnergyPercentage: The max energy percentage of total that the tower is allowed to have, between 0 and 1. 0 means only totally empty towers, 1 means only full towers
    """
    tower = creep.pos.findClosestByPath(FIND_MY_STRUCTURES, { "filter": \
        lambda s: ((s.structureType == STRUCTURE_TOWER and s.store.getUsedCapacity(RESOURCE_ENERGY) < s.store.getCapacity(RESOURCE_ENERGY) * maxEnergyPercentage)) })
    if not tower:
        tower = creep.pos.findClosestByRange(FIND_MY_STRUCTURES, { "filter": \
            lambda s: ((s.structureType == STRUCTURE_TOWER and s.store.getUsedCapacity(RESOURCE_ENERGY) < s.store.getCapacity(RESOURCE_ENERGY) * maxEnergyPercentage)) })
    return tower

def getEnergyStorageStructure(creep, closest = True, controller = False, storage = False):
    """
    Gets an energy storage structure in the same room as a creep
    :param creep: The creep to run
    :param closest: Whether to find the closest energy storage structure
    :param controller: Whether to include the room controller in the available energy storage structures
    :param storage: Whether to include the room's storage structure in the available energy storage structures, overrides controller
    """
    if storage:
        target = creep.pos.findClosestByRange(FIND_MY_STRUCTURES, {"filter": \
            lambda s: ((s.structureType == STRUCTURE_STORAGE and s.store.getFreeCapacity(RESOURCE_ENERGY) > 0))})
        if target:
            return target

    if controller:
        #go to the closest spawn/extension
        target = creep.pos.findClosestByPath(FIND_MY_STRUCTURES, { "filter": \
            lambda s: ((s.structureType == STRUCTURE_SPAWN or s.structureType == STRUCTURE_EXTENSION) 
                    and s.store.getFreeCapacity(RESOURCE_ENERGY) > 0) })
        if not target:
            target = creep.pos.findClosestByRange(FIND_MY_STRUCTURES, { "filter": \
                lambda s: ((s.structureType == STRUCTURE_SPAWN or s.structureType == STRUCTURE_EXTENSION) 
                        and s.store.getFreeCapacity(RESOURCE_ENERGY) > 0) })
        if target == undefined:
            #go to the controller
            target = creep.pos.findClosestByRange(FIND_MY_STRUCTURES, { "filter": \
                lambda s: ((s.structureType == STRUCTURE_CONTROLLER)) })
            return target        
    if not closest:
        return _(creep.room.find(FIND_MY_STRUCTURES)) \
            .filter(lambda s: ((s.structureType == STRUCTURE_SPAWN or s.structureType == STRUCTURE_EXTENSION)
                                    and s.store.getFreeCapacity(RESOURCE_ENERGY) > 0)) \
            .sample()
    else:
        target = creep.pos.findClosestByPath(FIND_STRUCTURES, { "filter": \
            lambda s: (((s.structureType == STRUCTURE_SPAWN or s.structureType == STRUCTURE_EXTENSION) 
                    and s.store.getFreeCapacity(RESOURCE_ENERGY) > 0)) })
        if not target:
            target = creep.pos.findClosestByRange(FIND_STRUCTURES, { "filter": \
                lambda s: (((s.structureType == STRUCTURE_SPAWN or s.structureType == STRUCTURE_EXTENSION) 
                        and s.store.getFreeCapacity(RESOURCE_ENERGY) > 0)) })
        return target

