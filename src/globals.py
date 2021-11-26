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
DEBUG_BUILDERS = True
HARVESTER_ROADS = False
DEBUG_SOURCE_SELECTION = False

def GetCreepByName(name):
    for creep_name in Object.keys(Game.creeps):
        if creep_name == name:
            return Game.creeps[name]
    return None

def getSource(creep):
    #source = _.sample(creep.room.find(FIND_SOURCES))
    sources = creep.room.find(FIND_SOURCES)
    unusedSources = []
    for source in sources:
        if source.pos.findInRange(FIND_MY_CREEPS, 1).length == 0 and source.energy > 0:
            unusedSources.append(source)
            if DEBUG_SOURCE_SELECTION:
                print("Unused sources: " + unusedSources + " with count " + unusedSources.length)
    range = 99999999
    sourceList = []
    
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
        #otherwise go to a random source
        if DEBUG_SOURCE_SELECTION:
            print("Both sources taken, picking random source")
        return sources[_.random(0, sources.length - 1)]

def getBrokenRoad(creep, closest = True, hitsMin = 300):
    """
    Gets a road in the same room as a creep with hits less than hitsMin
    :param creep: The creep to run
    :param closest: Whether to find the closest road
    :param hitsMin: The minimum number of hits we can allow before needing to repair
    """
    if not closest:
        return _(creep.room.find(FIND_STRUCTURES)) \
                    .filter(lambda s: (s.structureType == STRUCTURE_ROAD and s.hits < hitsMin)) \
                    .first()
    else:
        return creep.pos.findClosestByPath(FIND_STRUCTURES, { "filter": lambda s: ((s.structureType == STRUCTURE_ROAD and s.hits < hitsMin)) })        
    

def getTowers(creep, closest = True):
    """
    Gets a tower in the same room as a creep
    :param creep: The creep to run
    :param closest: Whether to find the closest tower
    """
    if not closest:
        return _(creep.room.find(FIND_MY_STRUCTURES)) \
                    .filter(lambda s: ((s.structureType == STRUCTURE_TOWER) and s.store.getFreeCapacity(RESOURCE_ENERGY) > 0)) \
                    .first()
    else:
        return creep.pos.findClosestByPath(FIND_MY_STRUCTURES, { "filter": lambda s: ((s.structureType == STRUCTURE_TOWER and s.store.getFreeCapacity(RESOURCE_ENERGY) > 0)) })


def getEnergyStorageStructure(creep, closest = True, controller = False):
    """
    Gets an energy storage structure in the same room as a creep
    :param creep: The creep to run
    :param closest: Whether to find the closest energy storage structure
    :param controller: Whether to include the room controller in the available energy storage structures
    """
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
        if selector == 0 or target == undefined:
            #go to the controller
            target = creep.pos.findClosestByPath(FIND_MY_STRUCTURES, { "filter": \
                lambda s: ((s.structureType == STRUCTURE_CONTROLLER)) })
        return target        

            
        if not closest:
            return _(creep.room.find(FIND_MY_STRUCTURES)) \
                    .filter(lambda s: ((s.structureType == STRUCTURE_SPAWN or s.structureType == STRUCTURE_EXTENSION)
                                    and s.store.getFreeCapacity(RESOURCE_ENERGY) > 0) or s.structureType == STRUCTURE_CONTROLLER) \
                    .sample()
        else:
            return creep.pos.findClosestByPath(FIND_MY_STRUCTURES, { "filter": \
                lambda s: (((s.structureType == STRUCTURE_SPAWN or s.structureType == STRUCTURE_EXTENSION) 
                        and s.store.getFreeCapacity(RESOURCE_ENERGY) > 0) or s.structureType == STRUCTURE_CONTROLLER) })
    else:
        if not closest:
            return _(creep.room.find(FIND_MY_STRUCTURES)) \
                .filter(lambda s: ((s.structureType == STRUCTURE_SPAWN or s.structureType == STRUCTURE_EXTENSION)
                                        and s.store.getFreeCapacity(RESOURCE_ENERGY) > 0)) \
                .sample()
        else:
            return creep.pos.findClosestByPath(FIND_MY_STRUCTURES, { "filter": \
                lambda s: ((s.structureType == STRUCTURE_SPAWN or s.structureType == STRUCTURE_EXTENSION) 
                        and s.store.getFreeCapacity(RESOURCE_ENERGY) > 0) })

