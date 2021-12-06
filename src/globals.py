import random
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


MAX_HARVESTERS = 3
MAX_BUILDERS = 2
DEBUG_HARVESTERS = False
DEBUG_CREEP_CREATION = True
DEBUG_BUILDERS = False
HARVESTER_ROADS = True
DEBUG_SOURCE_SELECTION = False
DEBUG_TOWERS = False
DEBUG_LINKS = False
FIX_ROADS = True
TOWER_ENERGY_RESERVE_PERCENTAGE = 0.3
HARVESTER_BUILDER_MAX_POWER = 12500
HARVESTER_BUILDER_MIN_POWER = 300
MAX_CREEP_WAIT = 50


def getSource(creep):
    #If there is a dropped source, just go there
    dropped_sources = _(creep.room.find(FIND_DROPPED_RESOURCES)).first()
    if dropped_sources:
        if DEBUG_SOURCE_SELECTION:
            print("Picking up dropped resources")
        return dropped_sources
    
    #then go to tombstones
    tombstone = _(creep.room.find(FIND_TOMBSTONES)).first()
    if tombstone and _.find(tombstone.store):
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
        #if there is truly nothing else to gather, then gather from storage
        if waitSources.length == 0:
            return creep.room.storage
        return waitSources[_.random(0, waitSources.length - 1)]

def getSpawnLink(spawn):
    link = spawn.pos.findClosestByRange(FIND_MY_STRUCTURES, { "filter": lambda s: ((s.structureType == STRUCTURE_LINK))})
    #if DEBUG_LINKS:
    #    print("Spawn link is " + link)
    return link

def getBrokenStructure(creep, closest=True, hitsMinPercentage=1, structureType = None, avoidStructureType = None):
    """
    Gets a structure in the same room as a creep with hits less than hitsMinPercentage of max hits
    :param creep: The creep to run
    :param closest: Whether to find the closest road
    :param hitsMinPercentage: The percentage to repair the road up to, between 0 and 1
    :param structureType: The the specific structureType to look for. If None, look for anything
    :param avoidStructureType: Look for any structures besides the one specified. If provided, ignores structureType
    """
    if structureType == None and avoidStructureType == None:
        if DEBUG_TOWERS:
            print("Getting first broken structure")
        if not closest:
            return _(creep.room.find(FIND_MY_STRUCTURES)) \
                        .filter(lambda s: (s.hits < (s.hitsMax * hitsMinPercentage))) \
                        .first()
        else:
            return creep.pos.findClosestByRange(FIND_MY_STRUCTURES, { "filter": lambda s: ((s.hits < (s.hitsMax * hitsMinPercentage))) })
    if avoidStructureType != None:
        if DEBUG_TOWERS:
            print("Avoiding structure type: " + avoidStructureType)
        if not closest:
            return _(creep.room.find(FIND_MY_STRUCTURES)) \
                        .filter(lambda s: ((s.hits < (s.hitsMax * hitsMinPercentage) and s.structureType != avoidStructureType))) \
                        .first()
        else:
            return creep.pos.findClosestByRange(FIND_MY_STRUCTURES, { "filter": lambda s: ((s.hits < (s.hitsMax * hitsMinPercentage) and s.structureType != avoidStructureType)) })
    if structureType != None:
        if DEBUG_TOWERS:
            print("Finding first broken structure of type: " + structureType)
        if not closest:
            return _(creep.room.find(FIND_MY_STRUCTURES)) \
                        .filter(lambda s: ((s.hits < (s.hitsMax * hitsMinPercentage) and s.structureType == structureType))) \
                        .first()
    if DEBUG_TOWERS:
        print("Finding closest broken structure")
    return creep.pos.findClosestByRange(FIND_MY_STRUCTURES, { "filter": lambda s: ((s.hits < (s.hitsMax * hitsMinPercentage) and s.structureType == structureType)) })

def getTower(creep, maxEnergyPercentage = 0.8):
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
        #ignore closest
        #determine randomly whether the energy goes to a spawn/extension or controller
        #then pick the closest of the winners
        selector = _.random(0, 9)
        if selector != 0:
            #go to the closest spawn/extension
            target = creep.pos.findClosestByPath(FIND_MY_STRUCTURES, { "filter": \
                lambda s: ((s.structureType == STRUCTURE_SPAWN or s.structureType == STRUCTURE_EXTENSION) 
                        and s.store.getFreeCapacity(RESOURCE_ENERGY) > 0) })
            if not target:
                target = creep.pos.findClosestByRange(FIND_MY_STRUCTURES, { "filter": \
                    lambda s: ((s.structureType == STRUCTURE_SPAWN or s.structureType == STRUCTURE_EXTENSION) 
                            and s.store.getFreeCapacity(RESOURCE_ENERGY) > 0) })
        if selector == 0 or target == undefined:
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


