# defs is a package which claims to export all constants and some JavaScript objects, but in reality does
#  nothing. This is useful mainly when using an editor like PyCharm, so that it 'knows' that things like Object, Creep,
#  Game, etc. do exist.
from defs import *
import globals
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


def run_tank(creep):
    moveToAttackRoom = False
    moveToSpawnRoom = False
    spawn = Game.getObjectById(creep.memory.spawnId)
    atSpawnRoom = creep.room.name == spawn.pos.roomName
    atAttackRoom = False
    flags = globals.getFlags(globals.FLAG_ATTACK)
    flag = None    
    if flags:
        flag = flags[0]
        atAttackRoom = creep.room.name == flag.pos.roomName

    if globals.DEBUG_TANKS and flag:
        print("Flag found in room: " + flag.pos.roomName)
    
    #check to see if the room I'm in is the room where the creep was spawned and we have a flag to go after
    if atSpawnRoom and flag:
        #if the answer is yes, don't move to the attack room until there is the minimum number of other creeps of the necessary type
        creepCount = globals.getMyCreepsInRoom(creep.pos.roomName)
        if creepCount.num_tanks >= globals.MIN_TANKS[creep.pos.roomName] or creep.memory.doneWaiting:
            if globals.DEBUG_TANKS:
                print(creep + " enough tanks in spawn room, moving to attack target")
            moveToAttackRoom = True
            creep.memory.doneWaiting = True
        else:
            #TODO: Get get them to wait at a rendezvous in the same room
            if globals.DEBUG_TANKS:
                print(creep + " waiting for more tanks before moving to attack room")
            if globals.CREEP_SPEAK:
                creep.say("waiting")

    #check if no flag is defined and I'm at the spawn room, defend spawn room
    elif atSpawnRoom and not flag:
        if globals.DEBUG_TANKS:
            print(creep + " defending spawn room because no flags are defined")
        moveToAttackRoom = False
        moveToSpawnRoom = True

    #we're not at the spawn room and no flag is defined, come home
    elif not atSpawnRoom and not flag:
        if globals.DEBUG_TANKS:
            print(creep + " no flags are defined, returning to spawn room")
        moveToAttackRoom = False        
        moveToSpawnRoom = True
        #TODO: have them wait at the rendezvous once coming home

    #we have a target, but we're not there yet, keep moving
    elif not atAttackRoom and not atSpawnRoom and flag:
        #not in the spawn room and there are defined flags, keep moving to the attack room
        if globals.DEBUG_TANKS:
            print(creep + " on mission")
        moveToAttackRoom = True
    #We've arrived at the target destination. You can only have an attackRoom if there is a flag
    elif atAttackRoom:
        if globals.DEBUG_TANKS:
            print(creep + " time to destroy")
    
    if moveToAttackRoom:
        if creep.room != flag.room:
            if globals.DEBUG_TANKS:
                print(creep + " moving to attack room")
            creep.moveTo(flag)
    elif moveToSpawnRoom and creep.room != spawn.room:
        if globals.DEBUG_TANKS:
            print(creep + " moving to spawn room")  
        creep.moveTo(spawn)
    else:
        enemies = globals.getHostiles(creep)
        if enemies.length > 0:
            target = enemies[0]
            if creep.pos.isNearTo(target):
                #do some killing
                creep.attack(target)
            else:
                #this approach always has the creep moving to the closest enemy target, as prioritized by the getHostiles call, it doesn't chase down stragglers
                #TODO: handle attacking a target that you can't move to (check path, if no path look for walls, then attack those)
                creep.moveTo(target)
        else:
            #move to rendezvous
            meetFlags = globals.getFlags(globals.FLAG_MEET)
            if meetFlags:
                if globals.DEBUG_TANKS:
                    print(creep + " moving to meet spot")
                creep.moveTo(meetFlags[0])
            else:
                creep.moveTo(spawn)
            
    
