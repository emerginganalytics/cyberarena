import random


class NameGenerator:
    def __init__(self, count):
        self.count = int(count)

    def generate(self):
        name_list = []
        for i in range(self.count):
            while True:
                name = self._get_name()
                if name not in name_list:
                    name_list.append(name)
                    break
        return name_list

    def _get_name(self):
        adj = random.choice(self.Words.ADJ)
        animal = random.choice(self.Words.ANIMALS)
        return f'{adj}{animal}'

    class Words:
        ANIMALS = ["Cat", "Cattle", "Dog", "Horse", "Pig", "Rabbit", "Aardvark", "Aardwolf", "Elephant", "Leopard",
                   "Albatross", "Alligator", "Alpaca", "Bison", "Robin", "Anaconda", "Angelfish", "Anglerfish", "Ant",
                   "Anteater", "Antelope", "Antlion", "Ape", "Aphid", "Wolf", "Armadillo", "Crab", "Baboon", "Badger",
                   "Eagle", "Bandicoot", "Barnacle", "Barracuda", "Basilisk", "Bass", "Bat", "Whale", "Bear", "Beaver",
                   "Bedbug", "Bee", "Beetle", "Bird", "Blackbird", "Panther", "Boa", "Boar", "Bobcat", "Bobolink", "Bonobo",
                   "Booby", "Jellyfish", "Bovid", "Butterfly", "Buzzard", "Canid", "Capybara", "Cardinal", "Caribou",
                   "Carp", "Catshark", "Catfish", "Cattle", "Centipede", "Cephalopod", "Chameleon",
                   "Cheetah", "Chickadee", "Chicken", "Chimpanzee", "Chinchilla", "Chipmunk", "Clam", "Clownfish", "Cobra",
                   "Cockroach", "Cod", "Condor", "Coral", "Cougar", "Cow", "Coyote", "Crawdad", "Crayfish",
                   "Cricket", "Crocodile", "Crow", "Cuckoo", "Cicada", "Deer", "Dinosaur", "Dog", "Dolphin", "Dragonfly",
                   "Dragon", "Echidna", "Eel", "Egret", "Elk", "Emu", "Ermine", "Falcon", "Ferret", "Finch", "Firefly",
                   "Fish", "Flamingo", "Flyingfish", "Gazelle", "Gecko", "Gerbil", "Gibbon", "Goldfish", "Goose", "Shark",
                   "Bear", "Grouse", "Gull", "Guppy", "Hamster", "Hare", "Harrier", "Hawk", "Hedgehog",
                   "Heron", "Herring", "Hookworm", "Hornet", "Horse", "Hoverfly", "Hummingbird", "Hyena",
                   "Iguana", "Impala", "Jackal", "Jaguar", "Jay", "Kangaroo", "Kingfisher", "Kite", "Kiwi",
                   "Koala", "Koi", "Krill", "Ladybug", "Lamprey", "Lark", "Leech", "Lemming", "Lemur", "Leopard", "Leopon",
                   "Limpet", "Lion", "Lizard", "Llama", "Lobster", "Locust", "Loon", "Louse", "Lynx", "Macaw", "Mackerel",
                   "Magpie", "Mammal", "Manatee", "Mandrill", "Marlin", "Marmoset", "Marmot", "Marsupial", "Marten",
                   "Mastodon", "Meadowlark", "Meerkat", "Mink", "Minnow", "Mite", "Mockingbird", "Mole", "Mollusk",
                   "Mongoose", "Monitor lizard", "Monkey", "Moose", "Mosquito", "Moth", "Mouse", "Muskox",
                   "Narwhal", "Newt", "Nightingale", "Ocelot", "Octopus", "Opossum", "Orangutan", "Orca", "Ostrich",
                   "Otter", "Owl", "Ox", "Panda", "Panther", "Parakeet", "Parrot", "Partridge", "Peacock",
                   "Peafowl", "Pelican", "Penguin", "Perch", "Pheasant", "Pinniped", "Piranha", "Planarian", "Platypus",
                   "Pony", "Porcupine", "Porpoise", "Possum", "Primate", "Ptarmigan", "Puffin", "Puma", "Python", "Quail",
                   "Quelea", "Quokka", "Rabbit", "Raccoon", "Raven", "Reindeer", "Reptile", "Rhinoceros",
                   "Roadrunner", "Rodent", "Rook", "Rooster", "Sailfish", "Salamander", "Salmon", "Sawfish",
                   "Scallop", "Scorpion", "Seahorse", "Shrew", "Shrimp", "Silverfish", "Skunk", "Snail",
                   "Snake", "Snipe", "Sparrow", "Spider", "Spoonbill", "Squid", "Squirrel", "Starfish", "Stingray", "Stoat",
                   "Stork", "Sturgeon", "Swallow", "Swan", "Swift", "Swordfish", "Swordtail", "Tahr", "Takin", "Tapir",
                   "Tarantula", "Tarsier", "Tern", "Thrush", "Tiger", "Tiglon", "Toad", "Tortoise", "Toucan", "Trout",
                   "Tuna", "Turkey", "Turtle", "Vicuna", "Viper", "Vole", "Wallaby", "Walrus",
                   "Wasp", "Warbler", "Wildcat", "Wildebeest", "Wildfowl", "Wolverine", "Wombat", "Woodpecker", "Worm",
                   "Wren", "Xerinae", "Yak", "Zebra", "Alpaca", "Cattle", "Cat", "Cattle", "Chicken", "Dog", "Camel",
                   "Canary", "Duck", "Goat", "Goose", "Hedgehog", "Pig", "Pigeon", "Rabbit", "Silkmoth",
                   "Fox", "Turkey", "Mouse", "Ferret", "Goldfish", "GuineaPig", "Guppy", "Horse", "Koi", "Llama", "Dove",
                   "Sheep", "Fish", "Buffalo", "Cabal", "Eliksni", 'Taken', "Hive", "Guardian"]
        ADJ = ['Fun', 'Wacky', 'Finicky', 'Sad', 'Cryptic', 'Cynical', 'Satirical', 'Ironic', 'Tawdry', 'Stoic', 'Critical',
               'Paper', 'Cheesy', 'Wordy', 'Cute', 'Cuddly', 'Red', 'Yellow', 'Teal', 'Green', 'Purple', 'Shiny',
               'Silky', 'Soft', 'Metal', 'Rocky', 'Cybernetic', 'Groovy']
