from phBot import *
from threading import Timer
from time import sleep
from binascii import hexlify  # for debugging
from enum import IntEnum, Enum
import QtBind
import struct


pName = 'TryTrappingFellowPet'
logPrefix = pName + '-plugin:'
pVersion = '1.0.0'
# ______________________________ Initializing ______________________________ #
gui = QtBind.init(__name__,pName)
gui_window_padding_x = 30
gui_window_padding_y = 100

gui_def_Profile_x = gui_window_padding_x
gui_def_Profile_y = gui_window_padding_y

gui_guild_storage_x = gui_window_padding_x
gui_guild_storage_y = gui_def_Profile_y + gui_window_padding_y

QtBind.createButton(gui, 'TrapFellow', 'trap fellow', gui_guild_storage_x, gui_guild_storage_y + 20)
QtBind.createButton(gui, 'UnsummonFellow', 'unsummon fellow', gui_guild_storage_x + 100, gui_guild_storage_y + 20)

#________________________________logging_______________________________#
def LogMsg(logstr):
    log(logPrefix + logstr)
    

# ______________________________ Methods ______________________________ #

class PetSkills(int, Enum):
     IronWill = 33704 #10 sec cool down to cast again. 1 min long
     Concentration = 33790 #3o sec cool down to cast again. 1 min long
     #Concentration = 34477

class PetData:
    def __init__(self, servername: str, skill_to_cast: PetSkills):
        self.servername = servername
        self.SkillToCast = skill_to_cast

class Pets(Enum):
    SILVERBACK = PetData("COS_PET2_PRO_SILVERBACK_A", PetSkills.IronWill)
    BEAR = PetData("COS_PET2_PRO_BEAR_A", PetSkills.IronWill)
    OSTRICH = PetData("COS_PET2_ENC_OSTRICH_A", PetSkills.Concentration)
    DOG = PetData("COS_PET2_PRO_DOG_A", PetSkills.IronWill)
    JAGUAR = PetData("COS_PET2_ENC_CAT_A", PetSkills.Concentration)

def AutoTrapFellow(arguments):
	Timer(1.0, TrapFellow).start()
	return 0

def TrapFellow():
    pets = get_pets()
    characterData = get_character_data()
    if(characterData is None):
        LogMsg("no character data found!")
        return
    characterID = characterData['player_id']
    # Convert to 4 bytes, little endian
    char_id_bytes = characterID.to_bytes(4, byteorder="little")
    LogMsg(f'player id is {characterID}')
    if(pets):
        for id,pet in pets.items():
             if pet['type'] == "fellow":
                servername = pet['servername']
                foundPet = next((pet_enum for pet_enum in Pets if pet_enum.value.servername == servername),None)
                if(foundPet):
                    p = id.to_bytes(4, byteorder='little')
                    p += b'\x0D'
                    p += foundPet.value.SkillToCast.to_bytes(4, byteorder='little')
                    p += characterID.to_bytes(4, byteorder="little")
                LogMsg('[%s] └ data: %s' % (__name__, hexlify(p)))
                inject_joymax(0x70C5,p, False)
                return 0
    else:
        LogMsg("no fellow pet found")

def UnsummonFellow():
    pets = get_pets()
    if(pets):
        for id,pet in pets.items():
             if pet['type'] == "fellow":
                p = struct.pack('I',id)
                inject_joymax(0x7116,p, False)
                LogMsg(f'Plugin: Unsummoning [{pet['servername']}]')
                return 0
    else:
        LogMsg("no fellow pet found")
    