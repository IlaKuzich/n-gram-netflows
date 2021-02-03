import nltk

from nltk.util import ngrams
from nltk.lm import Laplace

nltk.download('punkt')

class Model:
    def __init__(self, n, chain_length, step=1, vocabulary=None, counter=None):
        self.step = step
        self.n = n
        self.mle = Laplace(n, vocabulary, counter)
        self.chain_length = chain_length

    def train(self, training_ngrams, padded_sentences=None):
        self.mle.fit(training_ngrams, padded_sentences)

    def evaluate_chain(self, netflows):
        chains = []
        if len(netflows) <= self.chain_length:
            chains = [netflows]
        else:
            chains = [netflows[index:index + self.chain_length] for index in range(0, len(netflows) - self.chain_length, self.step)]
        values = []
        for chain in chains:
            if len(chain) < self.chain_length:
                continue
            grams = ngrams(chain, self.n)
            values.append(self.mle.perplexity(grams))
        return values

    def export(self):
        return self.n, self.mle.vocab, self.mle.counts
