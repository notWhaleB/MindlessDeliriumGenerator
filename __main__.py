import sys
from copy import copy
from random import randint


class Node:
    def __init__(self, index):
        self.count = 1
        self.seq = dict()
        self.index = index

    def inc(self):
        self.count += 1

    def is_exist(self, word):
        return True if word in self.seq else False

    def get_next(self, word):
        return self.seq[word]

    def add_next(self, word, link):
        self.seq[word] = link


class Trie:
    def __init__(self):
        self.tree = list()
        self.tree.append(Node(0))
        self.max_deep = 0

    def add_node(self):
        self.tree.append(Node(self.back().index + 1))

    def back(self):
        return self.tree[-1]

    def root(self):
        return self.tree[0]

    def dump_to(self, filename):
        temp = copy(self)

        for node in temp.tree:
            for key in node.seq:
                node.seq[key] = node.seq[key].index
        with open(filename, "w") as file:
            print(temp.max_deep, file=file)
            for node in temp.tree:
                print(node.count, node.seq, sep="#$#", file=file)

        del temp

    def load_from_dump(self, filename):
        self.tree = list()

        print("Reading...")
        with open(filename) as file:
            self.max_deep = int(file.readline())
            for index, line in enumerate(file):
                temp = Node(-1)
                temp.index = index
                data = line.split("#$#")
                temp.count = int(data[0])
                temp.seq = eval(data[1])
                self.tree.append(temp)

        print("Rebuilding...")
        for node in self.tree:
            for key in node.seq:
                node.seq[key] = self.tree[node.seq[key]]


def learn(input_file, ngram, dump_file):
    trie = Trie()
    trie.max_deep = ngram
    words = list()

    # Reading.
    print("Reading...")
    with open(input_file) as file:
        for line in file:
            for word in line.strip().split():
                if word.isalpha():
                    words.append(word.lower())
                elif word[0:-1].isalpha():
                    words.append(word[0:-1].lower())

    # Increments count of passing by node and creates one if not exists.
    print("Processing...")
    for l in range(len(words) - ngram + 1):
        cur_node = trie.root()
        for word in words[l:l + ngram]:
            if cur_node.is_exist(word):
                cur_node = cur_node.get_next(word)
                cur_node.inc()
            else:
                trie.add_node()
                cur_node.add_next(word, trie.back())
                cur_node = trie.back()

    print("Writing...")
    trie.dump_to(dump_file)


def generate(dump_file, length, output_file):
    trie = Trie()
    trie.load_from_dump(dump_file)
    result = []
    first_words = []

    # Performance improve:
    # Pre-processing of first word in view of huge calculation repeating.
    for key in trie.root().seq:
        for k in range(trie.root().seq[key].count):
            first_words.append(key)

    print("Generating...")
    while len(result) <= length:
        cur_node = trie.root()

        result.append(first_words[randint(0, len(first_words) - 1)])
        cur_node = cur_node.seq[result[-1]]

        # On each turn deeper pass the tree and randomly choose new word.
        for j in range(randint(0, trie.max_deep - 1)):
            temp = []

            for key in cur_node.seq:
                for k in range(cur_node.seq[key].count):
                    temp.append(key)

            result.append(temp[randint(0, len(temp) - 1)])
            cur_node = cur_node.seq[result[-1]]

    print("Writing...")
    with open(output_file, "w") as file:
        print(" ".join([word for word in result[:length]]), file=file)


argv = []

# Reading of command line parameters.
if __name__ == "__main__":
    for i in sys.argv:
        argv.append(i)

if argv[1] == "learn":
    learn(argv[2], int(argv[3]), argv[4])
elif argv[1] == "generate":
    generate(argv[2], int(argv[3]), argv[4])

print("Done.")


