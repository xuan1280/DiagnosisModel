import keras
from keras import Model
from keras.layers import *
import numpy as np


def build_diagnosis_model(user_feature_size):
    sequence_input = Input(shape=(None, 8))
    # lstm1, state_h都是hidden state, 等值
    # state_c是最後的結果
    lstm1, state_h, sequence_state = LSTM(1, return_state=True)(sequence_input)
    print(sequence_state)

    user_info_input = Input(shape=(3,), name='user_info_input')
    # 多輸入: sequence狀態與user資訊(痛感, 性別, 年齡)
    x = keras.layers.concatenate([sequence_state, user_info_input])
    x = Dense(120, activation='relu')(x)
    main_output = Dense(12, activation='sigmoid', name='main_output')(x)

    model = Model(inputs=[sequence_input, user_info_input], outputs=main_output)
    model.compile(optimizer='rmsprop', loss='binary_crossentropy', metrics=['accuracy'])
    return model


def pad_sequences(sequences, max_len=10):
    new_sequences = list()
    for sequence in sequences:
        sequence = np.array(sequence)
        gap = max_len - sequence.shape[0]
        new_sequence = np.zeros((max_len, 8))
        new_sequence[gap:, :] = sequence
        new_sequences.append(new_sequence.tolist())
    return new_sequences


if __name__ == '__main__':
    batch_size = 10
    epochs = 4
    sequence_max_len = 10

    # 按壓序列，一個序列多筆，每筆8個數值
    sequence_input = [[[22, 33, 44, 5, 33, 33, 22, 35], [24, 33, 43, 5, 36, 77, 22, 35],
                       [22, 33, 44, 5, 33, 33, 22, 35], [22, 33, 44, 5, 33, 33, 22, 35],
                       [22, 33, 44, 5, 33, 33, 22, 35], [22, 33, 44, 5, 33, 33, 22, 35]],
                      [[22, 33, 44, 5, 33, 33, 22, 35], [24, 33, 43, 5, 36, 77, 22, 35],
                       [22, 33, 44, 5, 33, 33, 22, 35], [22, 33, 44, 5, 33, 33, 22, 35]]]
    # 痛(0, 1, 2), 性別(0, 1), 年齡(0-100)
    user_info_input = [0, 1, 22]
    # 12個輸出
    target_data = [0.22, 0.44, 0.4, 0.1, 0.3, 0.12, 0.11, 0.23, 0.3, 0.13, 0.2, 0.1]

    # 將序列變成相同寬度(sequence_max_len)
    sequence_input = pad_sequences(sequence_input, sequence_max_len)

    sequence_input = np.array(sequence_input)
    user_info_input = np.tile(np.array(user_info_input), (len(sequence_input), 1))
    target_data = np.tile(np.array(target_data), (len(sequence_input), 1))

    print("Train Sequence Data's shape: ", sequence_input.shape)
    print("Train User Data' shape: ", user_info_input.shape)
    print("Train Label Data's shape: ", target_data.shape)

    model = build_diagnosis_model(len(user_info_input))
    model.fit([sequence_input, user_info_input], target_data, batch_size=batch_size, epochs=epochs,
              validation_split=0.2)
