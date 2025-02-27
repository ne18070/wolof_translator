
# import the required libraries:
# import os, sys
from keras.models import Model
from keras.layers import Input, LSTM, GRU, Dense, Embedding
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
# from keras.utils import to_categorical
import numpy as np
# import pickle
import matplotlib.pyplot as plt

from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    # return 'Hello from lamine API!'

    # -*- coding: utf-8 -*-


    #Execute this script to set values for different parameters:
    BATCH_SIZE = 64
    # EPOCHS = 20
    LSTM_NODES =256
    NUM_SENTENCES = 20000
    # MAX_SENTENCE_LENGTH = 50
    MAX_NUM_WORDS = 20000
    EMBEDDING_SIZE = 200

    """The language translation model that we are going to develop will translate English sentences into their French language counterparts. To develop such a model, we need a dataset that contains English sentences and their French translations.

    # Data Preprocessing

    We need to generate two copies of the translated sentence: one with the start-of-sentence token and the other with the end-of-sentence token.
    """

    input_sentences = []
    output_sentences = []
    output_sentences_inputs = []

    count = 0
    for line in open('./fra.txt', encoding="utf-8"):
        count += 1
        if count > NUM_SENTENCES:
            break
        if '\t' not in line:
            continue
        input_sentence = line.rstrip().split('\t')[0]
        output = line.rstrip().split('\t')[1]

        output_sentence = output + ' <eos>'
        output_sentence_input = '<sos> ' + output

        input_sentences.append(input_sentence)
        output_sentences.append(output_sentence)
        output_sentences_inputs.append(output_sentence_input)

    print("Number of sample input:", len(input_sentences))
    print("Number of sample output:", len(output_sentences))
    print("Number of sample output input:", len(output_sentences_inputs))

    """Now randomly print a sentence to analyse your dataset."""

    print("English sentence: ",input_sentences[180])
    print("French translation: ",output_sentences[180])

    """You can see the original sentence, i.e. **Join us**; its corresponding translation in the output, i.e **Joignez-vous à nous.** <eos>. Notice, here we have <eos> token at the end of the sentence. Similarly, for the input to the decoder, we have <sos> **Joignez-vous à nous.**

    # Tokenization and Padding

    The next step is tokenizing the original and translated sentences and applying padding to the sentences that are longer or shorter than a certain length, which in case of inputs will be the length of the longest input sentence. And for the output this will be the length of the longest sentence in the output.
    """

    # let’s visualise the length of the sentences.
    import pandas as pd

    eng_len = []
    fren_len = []

    # populate the lists with sentence lengths
    for i in input_sentences:
          eng_len.append(len(i.split()))

    for i in output_sentences:
          fren_len.append(len(i.split()))

    length_df = pd.DataFrame({'english':eng_len, 'french':fren_len})

    length_df.hist(bins = 20)
    plt.show()

    """The histogram above shows  maximum length of the French sentences is 12 and that of the English sentence is 6.

    For tokenization, the Tokenizer class from the keras.preprocessing.text library can be used. The tokenizer class performs two tasks:

    1. It divides a sentence into the corresponding list of word

    2. Then it converts the words to integers

    Also the **word_index** attribute of the Tokenizer class returns a word-to-index dictionary where words are the keys and the corresponding integers are the values.
    """

    #tokenize the input sentences(input language)
    input_tokenizer = Tokenizer(num_words=MAX_NUM_WORDS)
    input_tokenizer.fit_on_texts(input_sentences)
    input_integer_seq = input_tokenizer.texts_to_sequences(input_sentences)
    print(input_integer_seq)

    word2idx_inputs = input_tokenizer.word_index
    print('Total unique words in the input: %s' % len(word2idx_inputs))

    max_input_len = max(len(sen) for sen in input_integer_seq)
    print("Length of longest sentence in input: %g" % max_input_len)

    #with open('input_tokenizer_NMT.pickle', 'wb') as handle:
    #    pickle.dump(input_tokenizer, handle, protocol=4)

    #tokenize the output sentences(Output language)
    output_tokenizer = Tokenizer(num_words=MAX_NUM_WORDS, filters='')
    output_tokenizer.fit_on_texts(output_sentences + output_sentences_inputs)
    output_integer_seq = output_tokenizer.texts_to_sequences(output_sentences)
    output_input_integer_seq = output_tokenizer.texts_to_sequences(output_sentences_inputs)
    print(output_input_integer_seq)

    word2idx_outputs = output_tokenizer.word_index
    print('Total unique words in the output: %s' % len(word2idx_outputs))

    num_words_output = len(word2idx_outputs) + 1
    max_out_len = max(len(sen) for sen in output_integer_seq)
    print("Length of longest sentence in the output: %g" % max_out_len)

    #with open('output_tokenizer_NMT.pickle', 'wb') as handle:
    #    pickle.dump(output_tokenizer, handle, protocol=4)

    """Now the lengths of longest sentence can also be varified from the histogram above. And it can be concluded that English sentences are normally shorter and contain a smaller number of words on average, compared to the translated French sentences.

    Next, we need to pad the input. The reason behind padding the input and the output is that text sentences can be of varying length, however LSTM expects input instances with the same length. Therefore, we need to convert our sentences into fixed-length vectors. One way to do this is via padding.
    """

    encoder_input_sequences = pad_sequences(input_integer_seq, maxlen=max_input_len)
    print("encoder_input_sequences.shape:", encoder_input_sequences.shape)
    print("encoder_input_sequences[180]:", encoder_input_sequences[180])

    """Since there are 20,000 sentences in the input and each input sentence is of length 6, the shape of the input is now (20000, 6).

    You may recall that the original sentence at index 180 is **join us**. The tokenizer divided the sentence into two words ***join*** and ***us***, converted them to integers, and then applied pre-padding by adding four zeros at the start of the corresponding integer sequence for the sentence at index 180 of the input list.

    To verify that the integer values for ***join*** and ***us*** are 464 and 59 respectively, you can pass the words to the word2index_inputs dictionary, as shown below:
    """

    print(word2idx_inputs["join"])
    print(word2idx_inputs["us"])

    """In the same way, the decoder outputs and the decoder inputs are padded."""

    decoder_input_sequences = pad_sequences(output_input_integer_seq, maxlen=max_out_len, padding='post')
    print("decoder_input_sequences.shape:", decoder_input_sequences.shape)
    print("decoder_input_sequences[180]:", decoder_input_sequences[180])

    """The sentence at index 180 of the decoder input is <sos> Joignez-vous à nous. If you print the corresponding integers from the word2idx_outputs dictionary, you should see 2, 2028, 20, and 228 printed on the console."""

    print(word2idx_outputs["<sos>"])
    print(word2idx_outputs["joignez-vous"])
    print(word2idx_outputs["à"])
    print(word2idx_outputs["nous."])

    decoder_output_sequences = pad_sequences(output_integer_seq, maxlen=max_out_len, padding='post')
    print("decoder_output_sequences.shape:", decoder_output_sequences.shape)

    """# Word Embeddings

    We already converted our words into integers. So what's the difference between integer representation and word embeddings?

    There are two main differences between single integer representation and word embeddings. With integer reprensentation, a word is represented only with a single integer. With vector representation a word is represented by a vector of 50, 100, 200, or whatever dimensions you like. Hence, word embeddings capture a lot more information about words. Secondly, the single-integer representation doesn't capture the relationships between different words. On the contrary, word embeddings retain relationships between the words. You can either use custom word embeddings or you can use pretrained word embeddings.

    For English sentences, i.e. the inputs, we will use the GloVe word embeddings. For the translated French sentences in the output, we will use custom word embeddings.

    Let's create word embeddings for the inputs first. To do so, we need to load the GloVe word vectors into memory. We will then create a dictionary where words are the keys and the corresponding vectors are values,
    """

    # from numpy import array
    from numpy import asarray
    from numpy import zeros

    embeddings_dictionary = dict()

    glove_file = open(r'./drive/My Drive/kaggle_sarcasm/glove.twitter.27B.200d.txt', encoding="utf8")

    for line in glove_file:
        rec = line.split()
        word = rec[0]
        vector_dimensions = asarray(rec[1:], dtype='float32')
        embeddings_dictionary[word] = vector_dimensions
    glove_file.close()

    """Recall that we have 2150 unique words in the input. We will create a matrix where the row number will represent the integer value for the word and the columns will correspond to the dimensions of the word. This matrix will contain the word embeddings for the words in our input sentences."""

    num_words = min(MAX_NUM_WORDS, len(word2idx_inputs) + 1)
    embedding_matrix = zeros((num_words, EMBEDDING_SIZE))
    for word, index in word2idx_inputs.items():
        embedding_vector = embeddings_dictionary.get(word)
        if embedding_vector is not None:
            embedding_matrix[index] = embedding_vector

    print(embeddings_dictionary["join"])

    """In the previous section, we saw that the integer representation for the word **join** is 464. Let's now check the 464th index of the word embedding matrix."""

    print(embedding_matrix[464])

    """You can see that the values for the 464th row in the embedding matrix are similar to the vector representation of the word **join** in the GloVe dictionary, which confirms that rows in the embedding matrix represent corresponding word embeddings from the GloVe word embedding dictionary. This word embedding matrix will be used to create the embedding layer for our LSTM model.

    **Creates the embedding layer for the input:**
    """

    embedding_layer = Embedding(num_words, EMBEDDING_SIZE, weights=[embedding_matrix], input_length=max_input_len)

    """# Creating the Model

    The first thing we need to do is to define our outputs, as we know that the output will be a sequence of words. Recall that the total number of unique words in the output are 9511. Therefore, each word in the output can be any of the 9511 words. The length of an output sentence is 12. And for each input sentence, we need a corresponding output sentence. Therefore, the final shape of the output will be:
    """

    #(number of inputs, length of the output sentence, the number of words in the output)

    decoder_targets_one_hot = np.zeros((
            len(input_sentences),
            max_out_len,
            num_words_output
        ),
        dtype='float32'
    )
    decoder_targets_one_hot.shape

    """To make predictions, the final layer of the model will be a dense layer, therefore we need the outputs in the form of one-hot encoded vectors, since we will be using softmax activation function at the dense layer. To create such one-hot encoded output, the next step is to assign 1 to the column number that corresponds to the integer representation of the word."""

    for i, d in enumerate(decoder_output_sequences):
        for t, word in enumerate(d):
            decoder_targets_one_hot[i, t, word] = 1

    """Next, we need to create the encoder and decoders. The input to the encoder will be the sentence in English and the output will be the hidden state and cell state of the LSTM."""

    encoder_inputs = Input(shape=(max_input_len,))
    x = embedding_layer(encoder_inputs)
    encoder = LSTM(LSTM_NODES, return_state=True)

    encoder_outputs, h, c = encoder(x)
    encoder_states = [h, c]

    """The next step is to define the decoder. The decoder will have two inputs: the hidden state and cell state from the encoder and the input sentence, which actually will be the output sentence with an <sos> token appended at the beginning."""

    decoder_inputs = Input(shape=(max_out_len,))

    decoder_embedding = Embedding(num_words_output, LSTM_NODES)
    decoder_inputs_x = decoder_embedding(decoder_inputs)

    decoder_lstm = LSTM(LSTM_NODES, return_sequences=True, return_state=True)
    decoder_outputs, _, _ = decoder_lstm(decoder_inputs_x, initial_state=encoder_states)

    """Finally, the output from the decoder LSTM is passed through a dense layer to predict decoder outputs."""

    decoder_dense = Dense(num_words_output, activation='softmax')
    decoder_outputs = decoder_dense(decoder_outputs)

    #Compile
    model = Model([encoder_inputs,decoder_inputs], decoder_outputs)
    model.compile(
        optimizer='rmsprop',
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    model.summary()

    """Let's plot our model to see how it looks."""

    from keras.utils import plot_model
    plot_model(model, to_file='model_plot4a.png', show_shapes=True, show_layer_names=True)

    """From the output, you can see that we have two types of input. input_1 is the input placeholder for the encoder, which is embedded and passed through lstm_1 layer, which basically is the encoder LSTM. There are three outputs from the lstm_1 layer: the output, the hidden layer and the cell state. However, only the cell state and the hidden state are passed to the decoder.

    Here the lstm_2 layer is the decoder LSTM. The input_2 contains the output sentences with <sos> token appended at the start. The input_2 is also passed through an embedding layer and is used as input to the decoder LSTM, lstm_2. Finally, the output from the decoder LSTM is passed through the dense layer to make predictions.
    """

    from keras.callbacks import EarlyStopping
    es = EarlyStopping(monitor='val_loss', mode='min', verbose=1)

    history = model.fit([encoder_input_sequences, decoder_input_sequences], decoder_targets_one_hot,
        batch_size=BATCH_SIZE,
        epochs=20,
        callbacks=[es],
        validation_split=0.1,
    )

    model.save('seq2seq_eng-fra.h5')

    import matplotlib.pyplot as plt
    # %matplotlib inline
    plt.title('Model Loss')
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend(['train', 'test'], loc='upper left')
    plt.show()



    encoder_model = Model(encoder_inputs, encoder_states)
    model.compile(optimizer='rmsprop', loss='categorical_crossentropy')
    model.load_weights('seq2seq_eng-fra.h5')

    decoder_state_input_h = Input(shape=(LSTM_NODES,))
    decoder_state_input_c = Input(shape=(LSTM_NODES,))
    decoder_states_inputs = [decoder_state_input_h, decoder_state_input_c]

    decoder_inputs_single = Input(shape=(1,))
    decoder_inputs_single_x = decoder_embedding(decoder_inputs_single)

    decoder_outputs, h, c = decoder_lstm(decoder_inputs_single_x, initial_state=decoder_states_inputs)

    decoder_states = [h, c]
    decoder_outputs = decoder_dense(decoder_outputs)

    decoder_model = Model(
        [decoder_inputs_single] + decoder_states_inputs,
        [decoder_outputs] + decoder_states
    )

    from keras.utils import plot_model
    plot_model(decoder_model, to_file='model_plot_dec.png', show_shapes=True, show_layer_names=True)

    """# Making Predictions

    we want our output to be a sequence of words in the French language. To do so, we need to convert the integers back to words. We will create new dictionaries for both inputs and outputs where the keys will be the integers and the corresponding values will be the words.
    """

    # idx2word_input = {v:k for k, v in word2idx_inputs.items()}
    idx2word_target = {v:k for k, v in word2idx_outputs.items()}

    """The method will accept an input-padded sequence English sentence (in the integer form) and will return the translated French sentence."""

    def translate_sentence(input_seq):
        states_value = encoder_model.predict(input_seq)
        target_seq = np.zeros((1, 1))
        target_seq[0, 0] = word2idx_outputs['<sos>']
        eos = word2idx_outputs['<eos>']
        output_sentence = []

        for _ in range(max_out_len):
            output_tokens, h, c = decoder_model.predict([target_seq] + states_value)
            idx = np.argmax(output_tokens[0, 0, :])

            if eos == idx:
                break

            word = ''

            if idx > 0:
                word = idx2word_target[idx]
                output_sentence.append(word)

            target_seq[0, 0] = idx
            states_value = [h, c]

        return ' '.join(output_sentence)

    i = np.random.choice(len(input_sentences))
    input_seq = encoder_input_sequences[i:i+1]
    translation = translate_sentence(input_seq)
    print('Input Language : ', input_sentences[i])
    print('Actual translation : ', output_sentences[i])
    print('French translation : ', translation)

if __name__ == '__main__':
    app.run()
