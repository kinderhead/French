import cmd
import glob
import random
import pickle as p

class Card():
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
        
        print(f"What is {self.english} in french? ({g})")

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
            txt = input("Are you correct? (y|n) >>> ")
            if txt == "y":
                out += 1
        
        if gender == "both":
            if g == "m":
                out += self.ask("f", written)
            elif g == "f":
                out += self.ask("m", written)
        
        return out

cards = {}

class Interface(cmd.Cmd):
    prompt = ">>> "

    def do_load(self, name):
        """Loads a card set from a file
        Usage: load <set>"""
        try:
            with open(name + ".dat", "rb") as f:
                cards[name] = p.load(f)
        except FileNotFoundError:
            print("Cannot find set of name " + name)
    
    def do_unload(self, name):
        """Unloads a card set
        Usage: unload <set>"""
        with open(name + ".dat", "wb") as f:
            p.dump(cards[name], f)
        
        cards.pop(name)
    
    def do_edit(self, arg):
        """Edits a card
        Usage: edit <set> <english> <french masculine> <french feminine>
        """
        args = arg.split(" ")
        if len(args) != 4:
            print("Invalid number of arguments")
        else:
            idex = -1
            for edex, i in enumerate(cards[args[0]]):
                if i.english == args[1]:
                    idex = edex
            
            if idex == -1:
                print("Cannot find card with name " + args[1])
            else:
                cards[args[0]][idex] = Card(args[1], args[2], args[3])
    
    def do_create(self, name):
        """Creates a card set
        Usage: create <set>"""
        cards[name] = []
    
    def do_add(self, arg):
        """Adds a card to a set
        Usage: add <set> <english> <french masculine> <french feminine>"""
        args = arg.split(" ")
        if len(args) != 4:
            print("Invalid number of arguments")
        else:
            cards[args[0]].append(Card(args[1], args[2], args[3]))
    
    def do_all(self, arg):
        """Shows all loaded cards
        Usage: all"""
        txt = ""
        for k, v in cards.items():
            for i in v:
                txt += str(i) + "\n"
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
            for k, v in cards.items():
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

    def do_exit(self, arg):
        """Exits the program and saves
        Usage: exit"""
        return True
    
    def do_save(self, arg):
        """Saves all card sets
        Usage: save"""
        for k, v in cards.items():
            with open(k + ".dat", "wb") as f:
                p.dump(v, f)

Interface().cmdloop()

for k, v in cards.items():
    with open(k + ".dat", "wb") as f:
        p.dump(v, f)
