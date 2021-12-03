
# defs is a package which claims to export all constants and some JavaScript objects, but in reality does
#  nothing. This is useful mainly when using an editor like PyCharm, so that it 'knows' that things like Object, Creep,
#  Game, etc. do exist.
from defs import *
import harvester
import globals
import builder
import tower

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

        if not spawn.spawning:
            # Get the number of our creeps in this room.
            num_creeps = 0
            num_harvesters = 0
            num_builders = 0
            num_linkedPairs = 0
            for name in Object.keys(Game.creeps):
                creep = Game.creeps[name]
                if creep.pos.roomName == spawn.pos.roomName:
                    if creep.memory.role == "harvester":
                        num_harvesters += 1
                    elif creep.memory.role == "builder":
                        num_builders += 1
                    elif creep.memory.role == "link_miner" or creep.memory.role == "link_carry":
                        num_linkedPairs += 1
            
            num_creeps = num_harvesters + num_builders + (num_linkedPairs * 2)

            allRoadHarvesters = spawn.room.find(FIND_MY_CREEPS, {"filter": lambda s: ((s.memory.role == "harvester" and s.allRoads == True))}).length

            #If we have less than the total max of harvesters, create a harvester
            if ((num_harvesters < globals.MAX_HARVESTERS and spawn.room.energyAvailable >= spawn.room.energyCapacityAvailable) or num_harvesters == 0) \
                and spawn.room.energyAvailable >= 250:
                createHarvesterBuilder = True
                memory = { "memory": { "role": "harvester"} }                
            #otherwise, create a builder
            elif num_builders < globals.MAX_BUILDERS and spawn.room.energyAvailable >= spawn.room.energyCapacityAvailable and spawn.room.energyAvailable >= 250:
                createHarvesterBuilder = True
                memory = { "memory": { "role": "builder"} }
            
            if createHarvesterBuilder:
                if globals.DEBUG_CREEP_CREATION:
                    print("All road harvesters: " + allRoadHarvesters + " Total harvesters: " + num_harvesters)    
                creep_name = Game.time
                energy = spawn.room.energyAvailable
                creepParts = []
                if allRoadHarvesters:
                    creepParts.append(MOVE)
                    energy -= 50
                energyUnits = _(energy / 250).floor()
                energyUnits = _.min([energyUnits, 12500])

                for part in range(0, energyUnits):
                    if allRoadHarvesters:
                        creepParts.append(WORK)
                    else:
                        creepParts.append(MOVE)
                        creepParts.append(MOVE)
                        
                    creepParts.append(WORK)
                    creepParts.append(CARRY)
                while energy >= (energyUnits * 250) + 100:
                    creepParts.append(WORK)
                    energy -= 100
                while energy >= (energyUnits * 250) + 50:
                    creepParts.append(CARRY)
                    energy -= 50
                        
                    result = spawn.spawnCreep(creepParts, creep_name, memory)
                    if result != OK:
                        print("Ran into error creating creep: " + result + " with energy " + energyUnits*250 + " with role: " + memory.memory.role + " with parts: " + creepParts)
                    elif globals.DEBUG_CREEP_CREATION:
                        print("Creating a new creep named " + creep_name + " with energy " + energyUnits*250 + " with role: " + memory.memory.role + " with parts: " + creepParts)

        
    # Run creeps
    for name in Object.keys(Game.creeps):
        creep = Game.creeps[name]
        if creep.memory.role == "harvester":
            harvester.run_harvester(creep, num_creeps)
        elif creep.memory.role == "builder":
            builder.run_builder(creep)

    # Run Towers
    for struct in Object.keys(Game.structures):
        s = Game.structures[struct]
        if s.structureType == STRUCTURE_TOWER:
            tower.run_tower(s)

module.exports.loop = main
