import torch
import torch.nn as nn
from torch.nn.utils.rnn import pad_sequence


class Encoder(nn.Module):
    def __init__(self, vocab_size, embed_size, hidden_size):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_size)
        self.lstm = nn.LSTM(
            embed_size, hidden_size, batch_first=True, bidirectional=True
        )

    def forward(self, x):
        embedded = self.embedding(x)
        outputs, (hidden, cell) = self.lstm(embedded)
        return outputs, hidden, cell


class Attention(nn.Module):
    def __init__(self, hidden_size):
        super().__init__()
        self.attention = nn.Linear(hidden_size * 3, hidden_size)
        self.v = nn.Linear(hidden_size, 1, bias=False)

    def forward(self, hidden, encoder_outputs):
        seq_len = encoder_outputs.size(1)
        hidden = hidden.unsqueeze(1).repeat(1, seq_len, 1)
        energy = torch.tanh(self.attention(torch.cat([hidden, encoder_outputs], dim=2)))
        attention_weights = torch.softmax(self.v(energy).squeeze(2), dim=1)
        context = torch.bmm(attention_weights.unsqueeze(1), encoder_outputs)
        return context.squeeze(1), attention_weights


class Decoder(nn.Module):
    def __init__(self, vocab_size, embed_size, hidden_size):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_size)
        self.attention = Attention(hidden_size)
        self.lstm = nn.LSTM(embed_size + hidden_size * 2, hidden_size, batch_first=True)
        self.output = nn.Linear(hidden_size, vocab_size)

    def forward(self, input_token, hidden, cell, encoder_outputs):
        embedded = self.embedding(input_token.unsqueeze(1))
        context, _ = self.attention(hidden[0], encoder_outputs)
        lstm_input = torch.cat([embedded, context.unsqueeze(1)], dim=2)
        output, (hidden, cell) = self.lstm(lstm_input, (hidden, cell))
        prediction = self.output(output.squeeze(1))
        return prediction, hidden, cell


class Seq2Seq(nn.Module):
    def __init__(
        self, input_vocab_size, output_vocab_size, embed_size=128, hidden_size=256
    ):
        super().__init__()
        self.encoder = Encoder(input_vocab_size, embed_size, hidden_size)
        self.decoder = Decoder(output_vocab_size, embed_size, hidden_size * 2)
        self.hidden_size = hidden_size

    def forward(self, src, trg, teacher_forcing_ratio=0.5):
        batch_size = src.size(0)
        trg_len = trg.size(1)
        trg_vocab_size = self.decoder.output.out_features

        outputs = torch.zeros(batch_size, trg_len, trg_vocab_size).to(src.device)
        encoder_outputs, hidden, cell = self.encoder(src)

        hidden = hidden.view(1, batch_size, -1)
        cell = cell.view(1, batch_size, -1)

        input_token = trg[:, 0]

        for t in range(1, trg_len):
            output, hidden, cell = self.decoder(
                input_token, hidden, cell, encoder_outputs
            )
            outputs[:, t] = output

            use_teacher_forcing = torch.rand(1).item() < teacher_forcing_ratio
            input_token = trg[:, t] if use_teacher_forcing else output.argmax(1)

        return outputs
