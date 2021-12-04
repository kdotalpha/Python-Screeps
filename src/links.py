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

def runLinks(spawn):
    spawnLink = globals.getSpawnLink(spawn)
    for link in spawn.room.find(FIND_MY_STRUCTURES, { "filter": lambda s: ((s.structureType == STRUCTURE_LINK))}):
        if link is not spawnLink and link.store.getUsedCapacity(RESOURCE_ENERGY) > 0:
            result = link.transferEnergy(spawnLink)
            if globals.DEBUG_LINKS:
                print("Energy transfer from " + link + " to " + spawnLink + " with result: " + result)
            if result != OK and result != ERR_FULL and result != ERR_TIRED:
                print("Error transfering energy from " + link + " to " + spawnLink + ": " + result)
            if result == ERR_FULL and globals.DEBUG_LINKS:
                print("Can't transfer energy from " + link + " as " + spawnLink + " is full.")
    