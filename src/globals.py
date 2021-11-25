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
HARVESTER_ROADS = False

def GetCreepByName(name):
    for creep_name in Object.keys(Game.creeps):
        if creep_name == name:
            return Game.creeps[name]
    return None

def getEnergyStorageStructure(creep, closest = True, controller = False):
    """
    Gets an energy storage structure in the same room as a creep
    :param creep: The creep to run
    :param closest: Whether to find the closest energy storage structure
    :param controller: Whether to include the room controller in the available energy storage structures
    """
    if controller:
        if not closest:
            return _(creep.room.find(FIND_MY_STRUCTURES)) \
                    .filter(lambda s: ((s.structureType == STRUCTURE_SPAWN or s.structureType == STRUCTURE_EXTENSION)
                                    and s.store.getFreeCapacity(RESOURCE_ENERGY) > 0) or s.structureType == STRUCTURE_CONTROLLER) \
                    .sample()
        else:
            return _(creep.pos.findClosestByRange(FIND_MY_STRUCTURES)) \
                    .filter(lambda s: ((s.structureType == STRUCTURE_SPAWN or s.structureType == STRUCTURE_EXTENSION)
                                    and s.store.getFreeCapacity(RESOURCE_ENERGY) > 0) or s.structureType == STRUCTURE_CONTROLLER)
    else:
        if not closest:
            return _(creep.room.find(FIND_MY_STRUCTURES)) \
                .filter(lambda s: ((s.structureType == STRUCTURE_SPAWN or s.structureType == STRUCTURE_EXTENSION)
                                        and s.store.getFreeCapacity(RESOURCE_ENERGY) > 0)) \
                .sample()
        else:
            return _(creep.pos.findClosestByRange(FIND_MY_STRUCTURES)) \
                .filter(lambda s: ((s.structureType == STRUCTURE_SPAWN or s.structureType == STRUCTURE_EXTENSION)
                                        and s.store.getFreeCapacity(RESOURCE_ENERGY) > 0))
