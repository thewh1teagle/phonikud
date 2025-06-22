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
        self.hidden_size = hidden_size

    def forward(self, x):
        embedded = self.embedding(x)
        outputs, (hidden, cell) = self.lstm(embedded)
        return outputs, hidden, cell


class Attention(nn.Module):
    def __init__(self, hidden_size):
        super().__init__()
        # Encoder outputs are bidirectional (hidden_size * 2)
        # Decoder hidden state is hidden_size
        self.attention = nn.Linear(hidden_size + hidden_size * 2, hidden_size)
        self.v = nn.Linear(hidden_size, 1, bias=False)

    def forward(self, hidden, encoder_outputs):
        batch_size = encoder_outputs.size(0)
        seq_len = encoder_outputs.size(1)
        
        # hidden is [1, batch_size, hidden_size] from decoder
        # encoder_outputs is [batch_size, seq_len, hidden_size * 2]
        hidden = hidden.squeeze(0)  # [batch_size, hidden_size]
        hidden = hidden.unsqueeze(1).repeat(1, seq_len, 1)  # [batch_size, seq_len, hidden_size]
        
        # Concatenate and compute attention
        combined = torch.cat([hidden, encoder_outputs], dim=2)  # [batch_size, seq_len, hidden_size + hidden_size * 2]
        energy = torch.tanh(self.attention(combined))  # [batch_size, seq_len, hidden_size]
        attention_weights = torch.softmax(self.v(energy).squeeze(2), dim=1)  # [batch_size, seq_len]
        
        # Apply attention weights to encoder outputs
        context = torch.bmm(attention_weights.unsqueeze(1), encoder_outputs)  # [batch_size, 1, hidden_size * 2]
        return context.squeeze(1), attention_weights  # [batch_size, hidden_size * 2]


class Decoder(nn.Module):
    def __init__(self, vocab_size, embed_size, hidden_size):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_size)
        self.attention = Attention(hidden_size)
        # LSTM input: embedding + context (from attention)
        self.lstm = nn.LSTM(embed_size + hidden_size * 2, hidden_size, batch_first=True)
        self.output = nn.Linear(hidden_size, vocab_size)
        self.hidden_size = hidden_size

    def forward(self, input_token, hidden, cell, encoder_outputs):
        # input_token: [batch_size]
        embedded = self.embedding(input_token.unsqueeze(1))  # [batch_size, 1, embed_size]
        
        # Get context from attention
        context, attention_weights = self.attention(hidden, encoder_outputs)  # [batch_size, hidden_size * 2]
        
        # Combine embedding and context
        lstm_input = torch.cat([embedded, context.unsqueeze(1)], dim=2)  # [batch_size, 1, embed_size + hidden_size * 2]
        
        # Pass through LSTM
        output, (hidden, cell) = self.lstm(lstm_input, (hidden, cell))
        
        # Generate prediction
        prediction = self.output(output.squeeze(1))  # [batch_size, vocab_size]
        
        return prediction, hidden, cell


class Seq2Seq(nn.Module):
    def __init__(
        self, input_vocab_size, output_vocab_size, embed_size=128, hidden_size=256
    ):
        super().__init__()
        self.encoder = Encoder(input_vocab_size, embed_size, hidden_size)
        self.decoder = Decoder(output_vocab_size, embed_size, hidden_size)
        self.hidden_size = hidden_size
        
        # Projection layers to convert bidirectional encoder states to decoder states
        self.hidden_projection = nn.Linear(hidden_size * 2, hidden_size)
        self.cell_projection = nn.Linear(hidden_size * 2, hidden_size)

    def forward(self, src, trg, teacher_forcing_ratio=0.5):
        batch_size = src.size(0)
        trg_len = trg.size(1)
        trg_vocab_size = self.decoder.output.out_features

        outputs = torch.zeros(batch_size, trg_len, trg_vocab_size).to(src.device)
        encoder_outputs, hidden, cell = self.encoder(src)

        # Handle bidirectional LSTM states
        # hidden/cell: [2, batch_size, hidden_size] (2 for bidirectional)
        # We need to combine forward and backward states
        
        # Combine forward and backward hidden states
        hidden = torch.cat([hidden[0], hidden[1]], dim=1)  # [batch_size, hidden_size * 2]
        cell = torch.cat([cell[0], cell[1]], dim=1)  # [batch_size, hidden_size * 2]
        
        # Project to decoder hidden size
        hidden = self.hidden_projection(hidden).unsqueeze(0)  # [1, batch_size, hidden_size]
        cell = self.cell_projection(cell).unsqueeze(0)  # [1, batch_size, hidden_size]

        input_token = trg[:, 0]

        for t in range(1, trg_len):
            output, hidden, cell = self.decoder(
                input_token, hidden, cell, encoder_outputs
            )
            outputs[:, t] = output

            use_teacher_forcing = torch.rand(1).item() < teacher_forcing_ratio
            input_token = trg[:, t] if use_teacher_forcing else output.argmax(1)

        return outputs