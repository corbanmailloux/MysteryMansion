"""
Mystery Mansion, corb.co Edition

Built in 2016 by Corban Mailloux (http://corb.co)

Licensed under the MIT License.
"""

import subprocess as sp # Used to clear the screen
import random
import winsound
from time import sleep

DEBUG = False

class Furniture(object):
    """
        A single piece of furniture.

        Contains a name, number, and note.
    """
    def __init__(self, name):
        super(Furniture, self).__init__()

        self.name = name
        self.code = -1
        self.note = None

        self.filename = "furniture\\{0}".format(name.lower())
        if ("#" in name):
            self.filename = self.filename[0 : self.filename.find("#") - 1]

    def __str__(self):
        return "{0:>3d}: {1}".format(self.code, self.name)

    def __repr__(self):
        return str(self)

class Note(object):
    """
        Note objects are the data holder for each piece of furniture.

        This should probably be done through types/subclasses.
    """
    def __init__(self):
        super(Note, self).__init__()

        self.money = False # Contains the money
        self.ask = False # Ask about the item and/or person
        self.item = None # Item to be asked about
        self.person = None # Person to be asked about
        self.clue = False # Contains a clue card
        self.trapdoor = False # Contains a trapdoor
        self.secret = False # Contains a secret message
        self.text = None # Text to be displayed

class ItemOrPerson(object):
    """
        ItemOrPerson objects represent the physical cards in the game.
    """
    def __init__(self, name):
        super(ItemOrPerson, self).__init__()

        self.name = name
        self.filename = "items\\{0}".format(name.lower())

class Room(object):
    """
        A single room.

        Contains a name, number, locked state, and furniture.
    """
    def __init__(self, name, initial_furniture):
        super(Room, self).__init__()

        self.name = name
        self.code = -1
        self.furniture = initial_furniture
        self.locked = False # Lost when a game is restarted.

        self.filename = "rooms\\{0}".format(name.lower())

    def __str__(self):
        contains = ", ".join(map(str, self.furniture))

        locked_string = ""
        if self.locked:
            locked_string = " [LOCKED]"

        return "{0:>2d}{3}: {1} - Contains: {2}".format(self.code, self.name, contains, locked_string)

    def __repr__(self):
        return "{0:>2d}: {1}".format(self.code, self.name)

    def contains_furniture(self, furniture_number):
        return (furniture_number in self.furniture)

class Game(object):
    """
        The game. Creates the scenarios and runs the core logic.
    """
    def __init__(self, seed):
        super(Game, self).__init__()

        self.clues_found = 0 # Lost when a game is restarted.

        self.seed = seed
        random.seed(seed) # Set the seed. This allows game continuation.

        self.build_items()
        self.build_furniture()
        self.build_rooms()
        self.lock_rooms()
        #self.furnish_rooms_random() # Ignores pre-populated items.
        self.furnish_rooms_smart() # Uses pre-planned items.
        self.build_notes()

    def build_items(self):
        self.items = [
            ItemOrPerson("Tape"),
            ItemOrPerson("Letter"),
            ItemOrPerson("Photos"),
            ItemOrPerson("Map")
        ]

        self.people = [
            ItemOrPerson("Cook"),
            ItemOrPerson("Chauffeur"),
            ItemOrPerson("Maid"),
            ItemOrPerson("Butler")
        ]

    def build_furniture(self):
        furniture = {
            111: Furniture("Dining Room Chair #1 [111]"),
            112: Furniture("Dining Room Chair #2 [112]"),
            113: Furniture("Dining Room Table"),
            114: Furniture("China Cabinet"),
            121: Furniture("Sofa"),
            122: Furniture("Coffee Table"),
            123: Furniture("Bed"),
            124: Furniture("Dresser"),
            131: Furniture("Small Bookcase"),
            132: Furniture("Refrigerator"),
            133: Furniture("Sink"),
            134: Furniture("Oven"),
            141: Furniture("Kitchen Table"),
            142: Furniture("Pool Table"),
            143: Furniture("Pinball Machines"),
            144: Furniture("Large Bookcase"),
            211: Furniture("Whirlpool"),
            212: Furniture("Treadmill"),
            213: Furniture("Piano"),
            214: Furniture("Telescope"),
            221: Furniture("Clock"),
            222: Furniture("Computer"),
            223: Furniture("Juke Box"),
            224: Furniture("Rug"),
            231: Furniture("Fireplace"),
            232: Furniture("Knight"),
            233: Furniture("Television"),
            234: Furniture("Fish Tank"),
            241: Furniture("Lamp"),
            242: Furniture("Planter"),
            243: Furniture("Easel"),
            244: Furniture("Black Armchair #1 [244]"),
            311: Furniture("Black Armchair #2 [311]"),
            312: Furniture("White Armchair #1 [312]"),
            313: Furniture("White Armchair #2 [313]")
        }

        for i in furniture.keys():
            furniture[i].code = i

        self.furniture = furniture

    def build_notes(self):
        furniture_to_use = list(self.furniture.values())
        random.shuffle(furniture_to_use)

        # Hide the money
        money_furniture = furniture_to_use.pop()
        money_room = self.find_furniture(money_furniture.code)
        money_note = Note()
        money_note.money = True
        money_note.ask = True
        money_note.item = random.choice(self.items)
        money_note.person = random.choice(self.people)
        money_furniture.note = money_note
        if DEBUG:
            print("DEBUG: The money is in the {0}, code: {1}.".format(money_furniture.name, money_furniture.code))

        nonmoney_furniture = list(self.furniture.values())
        nonmoney_furniture.remove(money_furniture)

        nonmoney_rooms = list(self.rooms.values())
        nonmoney_rooms.remove(money_room)

        # Generate 11 "You found a clue!" notes.
        clue_furniture = []
        for i in range(11):
            note = Note()
            note.clue = True
            furniture = furniture_to_use.pop()
            furniture.note = note
            clue_furniture.append(furniture)

        # Trapdoor
        note = Note()
        note.trapdoor = True
        furniture_to_use.pop().note = note

        # Secret, 1-item, non-room clues
        for i in range(2):
            note = Note()
            note.secret = True
            note.ask = True
            if (random.choice([True, False])):
                note.item = random.choice(self.items)
                note.person = None
            else:
                note.item = None
                note.person = random.choice(self.people)
            note.text = "The money is not in the {0}.".format(random.choice(nonmoney_rooms).name)
            furniture_to_use.pop().note = note

        # 2-item, normal clue
        note = Note()
        note.ask = True
        note.item = random.choice(self.items)
        note.person = random.choice(self.people)
        note.clue = True
        furniture_to_use.pop().note = note

        # Not in furniture
        for i in range(6):
            note = Note()
            note.text = "The money is not in the {0}.".format(random.choice(nonmoney_furniture).name)
            furniture_to_use.pop().note = note

        # Look in furniture for clue
        for i in range(4):
            note = Note()
            note.text = "Look in the {0} for a clue.".format(random.choice(clue_furniture).name)
            furniture_to_use.pop().note = note

        if DEBUG:
            print("Unused items: {0}".format(len(furniture_to_use)))

    def find_furniture(self, furniture_number):
        for room in list(self.rooms.values()):
            if room.contains_furniture(furniture_number):
                return room

    def build_rooms(self):

        # Pre-populate rooms with their important pieces of furniture.
        room_names = [
            Room("Living Room", [121, 122]), # Sofa, Coffee Table
            Room("Bed Room", [123, 124]), # Bed, Dresser
            Room("Kitchen", [132, 133, 134, 141]), # Refrigerator, Sink, Oven, Kitchen Table
            Room("Music Room", [213]), # Piano
            Room("Game Room", [142, 143]), # Pool Table, Pinball Machines
            Room("Study", [131]), # Small Bookcase
            Room("Library", [144]), # Large Bookcase
            Room("Dining Room", [111, 112, 113]), # (2) Dining Room Chairs, Dining Room Table
            Room("Gym", [211, 212]) # Whirlpool, Treadmill
        ]

        room_numbers = [11, 12, 13, 14, 21, 22, 23, 24, 31]
        random.shuffle(room_names)

        rooms = dict(zip(room_numbers, room_names))

        for i in rooms.keys():
            rooms[i].code = i

        self.rooms = rooms

    def lock_rooms(self):
        room_numbers = list(self.rooms.keys())
        room_numbers.remove(11)

        room_numbers_to_lock = random.sample(room_numbers, random.randrange(1, 3))

        for i in room_numbers_to_lock:
            self.rooms[i].locked = True

    def furnish_rooms_random(self):
        # Ignores pre-populated items.

        furniture_to_use = list(self.furniture.keys())
        random.shuffle(furniture_to_use)

        rooms_to_use = list(self.rooms.values())
        random.shuffle(rooms_to_use)

        # 8 rooms get 4 pieces, 1 rooms gets 3 pieces
        start = 0
        for room in rooms_to_use:
            room.furniture = furniture_to_use[start:start + 4]
            start += 4

    def furnish_rooms_smart(self):
        furniture_to_use = list(self.furniture.keys())
        rooms_to_use = list(self.rooms.values())

        # Remove the used furniture
        for room in rooms_to_use:
            for furniture in room.furniture:
                furniture_to_use.remove(furniture)

        random.shuffle(furniture_to_use)
        random.shuffle(rooms_to_use)

        # Assign the remaining furniture
        while (len(furniture_to_use) > 0):
            for room in rooms_to_use:
                if ((len(room.furniture) < 4) and (len(furniture_to_use) > 0)):
                    room.furniture.append(furniture_to_use.pop())

    def start(self):
        while (True): # Bad
            clear_screen()
            self.get_input()
            input("(Enter to continue.)")

    def get_input(self):
        in_value = input("Enter number, or search for furniture by name: ")
        in_lenth = len(in_value)

        if (in_value.isdigit()): # Non-empty and a number
            try:
                in_value = int(in_value)
            except ValueError:
                print("Invalid value entered.")
                return

            if (in_lenth == 2): # Room
                self.explore_room(in_value)
            elif (in_lenth == 3): # Furniture
                self.explore_furniture(in_value)
            else:
                print("Invalid value entered.")
                return
        elif (in_lenth > 0):
            matching_furniture = []
            for furniture in list(self.furniture.values()):
                if (in_value.lower() in furniture.name.lower()):
                    matching_furniture.append(furniture)

            if (len(matching_furniture) > 0):
                print("Matching Furniture:")
                for furniture in matching_furniture:
                    print("- {0}".format(furniture))
            else:
                print("No matching furniture found.")

    def explore_room(self, room_number):
        if room_number not in self.rooms.keys():
            print("Invalid value entered.")
            return

        room = self.rooms[room_number]

        if room.locked:
            print("This room is locked. Do you have a key?")
            self.play_sound("room_locked")
            in_value = input("y/n: ")

            if (in_value is "y") or (in_value is "Y"):
                room.locked = False
            else:
                print("Sorry.")
                self.play_sound("sorry")
                return

        print("This is the {0}. You see the following:".format(room.name))
        for furniture_number in room.furniture:
            print("- {0}".format(self.furniture[furniture_number].name))

        self.play_sound("room_explore_1", False)
        self.play_sound(room.filename, False)
        self.play_sound("room_explore_2", False)
        for furniture_number in room.furniture:
            self.play_sound(self.furniture[furniture_number].filename, False)

    def play_sound(self, filename, async = True):
        base_audio_path = "game_audio\\{0}.wav"
        if (async):
            winsound.PlaySound(base_audio_path.format(filename), winsound.SND_FILENAME | winsound.SND_ASYNC)
        else:
            winsound.PlaySound(base_audio_path.format(filename), winsound.SND_FILENAME)

    def explore_furniture(self, furniture_number):
        if furniture_number not in self.furniture.keys():
            print("Invalid value entered.")
            return

        furniture = self.furniture[furniture_number]
        print(str(furniture))
        self.play_sound(furniture.filename, False)

        if (furniture.note is None):
            print("Sorry; no clue here.")
            self.play_sound("clue_none")
            return

        note = furniture.note

        if (note.trapdoor):
            print("Oops! A trapdoor! Go to the entrance.")
            self.play_sound("trapdoor")
            return

        if (note.ask):
            if (note.item is not None):
                print("Do you have the {0}?".format(note.item.name))
                self.play_sound("ask_item", False)
                self.play_sound(note.item.filename)
                in_value = input("y/n: ")

                if (in_value is "y") or (in_value is "Y"):
                    pass
                else:
                    print("Sorry.")
                    return
            if (note.person is not None):
                print("Is the {0} with you?".format(note.person.name))
                self.play_sound("ask_person_1", False)
                self.play_sound(note.person.filename, False)
                self.play_sound("ask_person_2")
                in_value = input("y/n: ")

                if (in_value is "y") or (in_value is "Y"):
                    pass
                else:
                    print("Sorry.")
                    self.play_sound("sorry")
                    return

        if (note.clue):
            if (self.clues_found < 10):
                self.clues_found += 1
                print("You found a clue!")
                self.play_sound("clue_found")
            else:
                print("Take a clue from another player.")
                self.play_sound("clue_take")
            note.clue = False
            return

        if (note.secret):
            print("***[SECRET MESSAGE]***")
            for i in range(3):
                winsound.Beep(900, 175)
                sleep(0.025)
            input("Press Enter to view.")

        if (note.text is not None):
            print(note.text)

            # Finish these!
            # # Look in the ___ for a clue.
            # self.play_sound("hint_look_1", False)
            # self.play_sound(note.?, False)
            # self.play_sound("hint_look_2")
            #
            # # The money is not in the ___.
            # self.play_sound("hint_not_in")
            # self.play_sound(note.?)
            return

        if (note.money):
            print("You found the money! You WIN!")

            print("      $            $            $      ")
            print("   ,$$$$$,      ,$$$$$,      ,$$$$$,   ")
            print(" ,$$$'$`$$$   ,$$$'$`$$$   ,$$$'$`$$$  ")
            print(" $$$  $   `   $$$  $   `   $$$  $   `  ")
            print(" '$$$,$       '$$$,$       '$$$,$      ")
            print("   '$$$$,       '$$$$,       '$$$$,    ")
            print("     '$$$$,       '$$$$,       '$$$$,  ")
            print("      $ $$$,       $ $$$,       $ $$$, ")
            print("  ,   $  $$$   ,   $  $$$   ,   $  $$$ ")
            print("  $$$,$.$$$'   $$$,$.$$$'   $$$,$.$$$' ")
            print("   '$$$$$'      '$$$$$'      '$$$$$'   ")
            print("      $            $            $      ")

            self.play_sound("win")

            input()
            return

        # Other cases
        print("Sorry; no clue here.")
        self.play_sound("clue_none")
        return

def clear_screen():
    if not DEBUG:
        sp.call('cls', shell=True) # Clear screen

def main():
    clear_screen()

    print("Welcome to Mystery Mansion, corb.co edition!")
    game_number_input = input("Press Enter to start a new game, or enter a game number to continue: ")

    seed = random.randrange(1, 10000) # Generate a game number.

    if (len(game_number_input) != 0):
        try:
            seed = int(game_number_input)
        except ValueError:
            print("Invalid value entered. Starting a new game.")

    print("Write down this game number: {0}".format(seed))
    input("Press Enter to start game.")

    game = Game(seed)
    game.play_sound("welcome", True)

    if DEBUG:
        print("ROOMS:")
        for room in list(game.rooms.values()):
            print("{0}:".format(room.name))
            for furniture_number in room.furniture:
                print("- {0}".format(game.furniture[furniture_number].name))

    game.start()


# Start
main()
