
# defs is a package which claims to export all constants and some JavaScript objects, but in reality does
#  nothing. This is useful mainly when using an editor like PyCharm, so that it 'knows' that things like Object, Creep,
#  Game, etc. do exist.
from defs import *
import harvester
import globals
import builder
import tower
import links

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


def main():
    """
    Main game logic loop.
    """
   
   #Clean the memory of dead creeps
    for mem_name in Object.keys(Memory.creeps):
       if not Game.creeps[mem_name]:
           del Memory.creeps[mem_name]

    # Run each spawn
    for name in Object.keys(Game.spawns):
        spawn = Game.spawns[name]

        links.runLinks(spawn)
        
        # Get the number of our creeps in this room.
        creepCount = globals.getMyCreepsInRoom(spawn.pos.roomName)
    
        if not spawn.spawning:

            #allRoadHarvesters = spawn.room.find(FIND_MY_CREEPS, {"filter": lambda s: ((s.memory.role == "harvester" and s.allRoads == True))}).length == num_harvesters and num_harvesters != 0
            allRoadHarvesters = True
            spawnLink = globals.getSpawnLink(spawn)

            #If we have less than the total max of harvesters, create a harvester
            if ((creepCount.num_harvesters < globals.MAX_HARVESTERS and spawn.room.energyAvailable >= spawn.room.energyCapacityAvailable) or creepCount.num_harvesters == 0) \
                and spawn.room.energyAvailable >= globals.HARVESTER_BUILDER_MIN_POWER:
                createHarvesterBuilder = True
                memory = { "memory": { "role": "harvester", "spawnLink": spawnLink } }                
            #otherwise, create a builder
            elif creepCount.num_builders < globals.MAX_BUILDERS and spawn.room.energyAvailable >= spawn.room.energyCapacityAvailable and \
                spawn.room.energyAvailable >= globals.HARVESTER_BUILDER_MIN_POWER:
                createHarvesterBuilder = True
                memory = { "memory": { "role": "builder", "spawnLink": spawnLink } }
            
            if createHarvesterBuilder:
                if globals.DEBUG_CREEP_CREATION:
                    print("All road harvesters: " + allRoadHarvesters + " Total harvesters: " + creepCount.num_harvesters)    
                creep_name = Game.time
                energy = _.min([spawn.room.energyAvailable, globals.HARVESTER_BUILDER_MAX_POWER])
                creepParts = []
                energyUnits = _(energy / globals.HARVESTER_BUILDER_MIN_POWER).floor()
                energyRemainder = energy - (energyUnits * globals.HARVESTER_BUILDER_MIN_POWER)
                print("energy remainder: " + energyRemainder)
                for part in range(0, energyUnits):
                    #for each energy unit of 300
                    if allRoadHarvesters:
                        creepParts.append(MOVE)
                        creepParts.append(MOVE)
                        creepParts.append(WORK)
                        creepParts.append(CARRY)
                        creepParts.append(CARRY)
                    else:
                        creepParts.append(MOVE)
                        creepParts.append(MOVE)
                        creepParts.append(MOVE)
                        creepParts.append(WORK)
                        creepParts.append(CARRY)

                #python really needs a switch block
                if energyRemainder == 250:
                    if allRoadHarvesters:
                        creepParts.append(MOVE)
                        creepParts.append(WORK)
                        creepParts.append(CARRY)
                        creepParts.append(CARRY)                        
                    else:
                        creepParts.append(MOVE)
                        creepParts.append(MOVE)
                        creepParts.append(CARRY)
                        creepParts.append(WORK)                        
                elif energyRemainder == 200:
                    if allRoadHarvesters:
                        creepParts.append(MOVE)
                        creepParts.append(CARRY)
                        creepParts.append(WORK)
                    else:
                        creepParts.append(MOVE)
                        creepParts.append(MOVE)
                        creepParts.append(CARRY)
                        creepParts.append(CARRY)
                elif energyRemainder == 150:
                    if allRoadHarvesters:
                        creepParts.append(MOVE)
                        creepParts.append(WORK)
                    else:
                        creepParts.append(MOVE)
                        creepParts.append(MOVE)
                        creepParts.append(CARRY)
                elif energyRemainder == 100:
                    if allRoadHarvesters:
                        creepParts.append(WORK)
                    else:
                        creepParts.append(MOVE)
                        creepParts.append(CARRY)
                elif energyRemainder == 50:
                    if allRoadHarvesters:
                        creepParts.append(CARRY)
                    else:
                        creepParts.append(MOVE)
                        
                result = spawn.spawnCreep(creepParts, creep_name, memory)
                if result != OK:
                    print("Ran into error creating creep: " + result + " with energy " + energy + " with role: " + memory.memory.role + " with parts: " + creepParts)
                elif globals.DEBUG_CREEP_CREATION:
                    print("Creating a new creep named " + creep_name + " with energy " + energy + " with role: " + memory.memory.role + " with parts: " + creepParts)

        
    # Run creeps in all rooms
    for name in Object.keys(Game.creeps):
        creep = Game.creeps[name]
        if creep.memory.role == "harvester":
            harvester.run_harvester(creep)
        elif creep.memory.role == "builder":
            builder.run_builder(creep)

    # Run Towers in all rooms
    for struct in Object.keys(Game.structures):
        s = Game.structures[struct]
        if s.structureType == STRUCTURE_TOWER:
            tower.run_tower(s)

module.exports.loop = main
