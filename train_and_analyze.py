from util.encoder import encode_dataset, preprocess_dataset
from util.io_utils import read_dataset_csv
from train.model import Model
import pickle
import random
import matplotlib.pyplot as plt

def evaluate_dataset(model, dataset_files, normal_flows):
    perplexity_values = []
    dataset = read_dataset_csv(dataset_files)
    encoded_flows = encode_dataset(dataset, min_len_cutoff=15, normal_flows=normal_flows)
    print(encoded_flows)
    for encoded_line in encoded_flows:
        perplexity_values.extend(model.evaluate_chain(encoded_line))
    print(perplexity_values)
    return perplexity_values

def evaluate(n, vocab_filename, counts_filename, test_dataset, quantile):
    #load model
    with open(vocab_filename, 'rb') as vocab_file:
        vocab = pickle.load(vocab_file)

    with open(counts_filename, 'rb') as counts_file:
        counts = pickle.load(counts_file)

    model = Model(n, 8, 4, vocab, counts)
    print(model.mle.counts.N())
    print(len(list(model.mle.vocab)))

    #calculate perplexity
    normal_perplexities = evaluate_dataset(model, test_dataset, True)
    bot_perplexities = evaluate_dataset(model, test_dataset, False)

    bot_perplexities_len = len(bot_perplexities)
    size_aligned_normal_perplexities = random.sample(normal_perplexities, bot_perplexities_len)

    #build graphs
    plt.hist(size_aligned_normal_perplexities, bins=50, color='b', label='Normal', alpha = 0.7)
    plt.hist(bot_perplexities, bins=50, color='r', label='Bot', alpha=0.5)

    plt.gca().set(title='Frequency Histogram', ylabel='Frequency')
    plt.legend()
    plt.show()

    #calculate quantile
    print('Quantile for value {} is {}'.format(quantile, find_quantile_value(quantile, normal_perplexities)))

def find_quantile_value(quantile, normal_perplexity):
    norm_len = len(normal_perplexity)
    index = int(quantile * norm_len)
    print(norm_len)
    print(index)
    normal_perplexity.sort()
    print(normal_perplexity[index])
    return normal_perplexity[index]


def train_model(N, train_dataset, vocab_filename, counts_filename):
    """Default preprocessing for a sequence of sentences.

    Creates two iterators:
    - sentences padded and turned into sequences of `nltk.util.everygrams`
    - sentences padded as above and chained together for a flat stream of words

    :param N: Ngram order.
    :param train_dataset: List of files from CTU-13 dataset in .csv format
    :param vocab_filename: Filename to store vocab
    :param counts_filename: Filename to store counts
    """
    dataset = read_dataset_csv(train_dataset)
    encoded_flows = encode_dataset(dataset, min_len_cutoff=15)
    grams, vocabulary = preprocess_dataset(encoded_flows, n=N)
    # print(list(vocabulary))


    model = Model(N, chain_length=8, step=4)
    model.train(grams, vocabulary)

    print(model.mle.counts.N())
    print(len(list(model.mle.vocab)))
    print(list(model.mle.vocab))

    print(model.mle.counts['udp_CON_Domain Name Server_1.0'])

    n, vocab, counts = model.export()


    with open(vocab_filename, 'wb') as vocab_file:
         pickle.dump(vocab, vocab_file)
    with open(counts_filename, 'wb') as counts_file:
         pickle.dump(counts, counts_file)

if __name__ == "__main__":
    evaluate(4, './pretrained/vocab.txt', './pretrained/counts.txt', [
        'CTU-13 files to evaluate'
    ], 0.955)
