import cmd
import glob
import random
import pickle as p

class Proficiency():
    NONE = 0
    ONCE = 1
    TWICE = 2
    PROFICIENT = 3

class Card():
    proficiency = Proficiency.NONE

    def __init__(self, english, fr_m, fr_f):
        self.english = english
        self.fr_m = fr_m
        self.fr_f = fr_f
    
    def __str__(self):
        return f"{self.english} | Masculine: {self.fr_m}, Feminine: {self.fr_f}"
    
    def ask(self, gender, written):
        out = 0

        g = ""
        if gender != "both":
            g = gender
        else:
            g = random.choice(["m", "f"])
        
        if self.fr_f != self.fr_m:
            print(f"What is {self.english} in french? ({g})")
        else:
            print(f"What is {self.english} in french?")

        if written == "true":
            txt = input("Write >>> ")
            if g == "m" and txt == self.fr_m:
                out += 1
                print("Correct")
            elif g == "f" and txt == self.fr_f:
                out += 1
                print("Correct")
            elif g == "m":
                print("Incorrect. The correct answer is: " + self.fr_m)
            elif g == "f":
                print("Incorrect. The correct answer is: " + self.fr_f)
        else:
            input("Hit enter to show answer ")

            ans = ""
            if g == "m":
                ans = self.fr_m
            else:
                ans = self.fr_f

            print("The correct answer is " + ans)
            txt = input("Are you correct? (y|n) >>> ").replace(" ", "_")
            if txt == "y":
                out += 1
                if gender == "both":
                    out += 1
        
        if gender == "both" and self.fr_f != self.fr_m:
            if g == "m":
                out += self.ask("f", written)
            elif g == "f":
                out += self.ask("m", written)
        
        return out

class Set(list):
    @staticmethod
    def load(name):
        try:
            with open(name + ".dat", "rb") as f:
                s = p.load(f)
                if type(s) == list:
                    print("Converting legacy set format to new set format")
                    new = Set()
                    new.extend(s)
                    return new
                else:
                    return s
        except FileNotFoundError:
            print("Cannot find card set " + name)
    
    def save(self, name):
        with open(name + ".dat", "wb") as f:
            p.dump(self, f)

class Interface(cmd.Cmd):
    prompt = ">>> "
    cards = {}

    def do_load(self, name):
        """Loads a card set from a file
        Usage: load <set>"""
        self.cards[name] = Set.load(name)
    
    def do_unload(self, name):
        """Unloads a card set
        Usage: unload <set>"""
        self.cards[name].save(name)
        
        self.cards.pop(name)
    
    def do_edit(self, arg):
        """Edits a card
        Usage: edit <set> <english> <french masculine> <french feminine>
        """
        args = arg.split(" ")
        if len(args) != 4:
            print("Invalid number of arguments")
        else:
            idex = -1
            for edex, i in enumerate(self.cards[args[0]]):
                if i.english == args[1]:
                    idex = edex
            
            if idex == -1:
                print("Cannot find card with name " + args[1])
            else:
                self.cards[args[0]][idex] = Card(args[1], args[2], args[3])
    
    def do_create(self, name):
        """Creates a card set
        Usage: create <set>"""
        self.cards[name] = []
    
    def do_add(self, arg):
        """Adds a card to a set
        Usage: add <set> <english> <french masculine> <french feminine>
        Or: add <set> <english> <french>"""
        args = arg.split(" ")
        if len(args) != 4 and len(args) != 3:
            print("Invalid number of arguments")
        else:
            if args[0] not in self.cards:
                print("Cannot find card set")
                return

            if len(args) == 3:
                self.cards[args[0]].append(Card(args[1], args[2], args[2]))
                return
            self.cards[args[0]].append(Card(args[1], args[2], args[3]))
    
    def do_all(self, arg):
        """Shows all loaded cards
        Usage: all"""
        txt = ""
        for k, v in self.cards.items():
            for i in v:
                txt += str(i).replace("_", " ") + "\n"
        print(txt)
    
    def do_show(self, arg):
        """Shows all available sets to load
        Usage: show"""
        l = glob.glob("*.dat")
        for i in l:
            print(i.split(".")[0])

    def do_study(self, arg):
        """Starts a study session with all loaded card sets
        Usage: study <gender: m|f|both> <written: true|false> <random: true|false>"""
        args = arg.split(" ")
        if len(args) != 3:
            print("Invalid number of arguments")
        else:
            gender = args[0]
            written = args[1]
            r = args[2]

            points = 0

            c = []
            for k, v in self.cards.items():
                for i in v:
                    #print(i)
                    c.append(i)
            
            if r:
                random.shuffle(c)
            
            for i in c:
                points += i.ask(gender, written)
                print("")
            
            total = 0

            if gender == "both":
                total = len(c) * 2
            else:
                total = len(c)

            print("You got " + str(points) + " out of " + str(total) + " correct")
    
    def do_learn(self, arg):
        """Starts a learning session with all loaded sets
        Learning session saves with each set. Use the reset argument
        to reset the current save
        Usage: learn <gender: m|f|both> <written: true|false>
        Or: learn reset"""

        if arg == "reset":
            for k, v in self.cards.items():
                for i in v:
                    i.proficiency = Proficiency.NONE
            return
        
        args = arg.split(" ")
        if len(args) != 2:
            print("Invalid number of arguments")
        else:
            gender = args[0]
            written = args[1]
            while True:
                txt = "n"
                c = []
                idex = 0
                for k, v in self.cards.items():
                    for i in v:
                        idex += 1
                        if i.proficiency != Proficiency.PROFICIENT:
                            c.append(i)
                
                print(f"\nCards remaining: {len(c)}/{idex}\n")

                random.shuffle(c)

                if len(c) == 0 or txt == "y":
                    break

                for i in c:
                    points = i.ask(gender, written)
                    if points == 2:
                        i.proficiency += 1
                    elif points == 0 and i.proficiency > 0:
                        i.proficiency -= 1
                
                txt = input("Exit? (y|n) >>> ")

    def do_exit(self, arg):
        """Exits the program and saves
        Usage: exit"""
        return True
    
    def do_save(self, arg):
        """Saves all card sets
        Usage: save"""
        for k, v in self.cards.items():
            v.save(k)

c = Interface()
c.cmdloop()

for k, v in c.cards.items():
    v.save(k)
