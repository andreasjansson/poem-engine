import nltk
from collections import defaultdict
import random
import copy
import gdbm

def get_tags(filename):
    with open(filename) as f:
        text = f.read()

    tokens = nltk.word_tokenize(text)
    tags = nltk.pos_tag(tokens)
    tags = [(x.lower(), y) for x, y in tags]

    return tags

def get_sentences(tags, max_length=6):
    sentences = []
    for i, (word, tag) in enumerate(tags):
        if word == 'a':
            sentence = []
            good_sentence = None
            for j in range(i, min(i + max_length, len(tags))):
                word, tag = tags[j]
                if word in (',', ')', '(', '``', ';', ':', "'s", '?'):
                    break
                if word.endswith('.'):
                    sentence.append((word[:-1], tag))
                else:
                    sentence.append((word, tag))
                if tag == 'NNP' or word.endswith('.'):
                    good_sentence = sentence
                    break
            else:
                for j in range(max_length - 1, 0, -1):
                    word, tag = sentence[j]
                    if tag == 'NN':
                        good_sentence = sentence[:j + 1]
                        break
            if good_sentence:
                sentences.append([w for w, _ in good_sentence])

    return sentences

def get_rhymes(sentences):
    smap = defaultdict(set)
    db = gdbm.open('words.db')
    for s in sentences:
        last = s[-1]
        try:
            pron = db[last.upper()]
        except KeyError:
            continue
        smap[pron].add(tuple(s))
    db.close()
    return smap

def order_sentences(smap):
    smap = {x: copy.copy(y) for x, y in smap.items() if len(y) > 1}
    sentences = []

    while len(smap):
        k = random.choice(smap.keys())
        v = smap[k]
        s = random.choice(list(v))
        last = s[-1]
        if all([x[-1] == last for x in v]):
            del smap[k]
        else:
            v.remove(s)
            s2 = s
            while s2[-1] == s[-1]:
                s2 = random.choice(list(v))
            sentences += [s, s2]
            v.remove(s2)
            if not v:
                del smap[k]

    ordered = []
    for i in xrange(0, len(sentences) - 4, 4):
        ordered.append(sentences[i])
        ordered.append(sentences[i + 2])
        ordered.append(sentences[i + 1])
        ordered.append(sentences[i + 3])

    return ordered

def print_poem(ordered_sentences):
    for i, sentence in enumerate(ordered_sentences):
        if i % 4 == 0:
            print ''
        print ' '.join(sentence)

def main():
    nltk.download('maxent_treebank_pos_tagger')

    tags = get_tags('machinery.txt')
    sentences = get_sentences(tags)
    smap = get_rhymes(sentences)
    ordered = order_sentences(smap)

    print_poem(ordered)

    return smap, ordered

if __name__ == '__main__':
    main()
