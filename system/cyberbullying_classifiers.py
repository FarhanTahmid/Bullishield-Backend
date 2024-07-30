import torch
import torch.nn as nn
from transformers import BertTokenizer, BertModel


class CyberBullyingClassifierBangla(nn.Module):
    def __init__(self):
        super(CyberBullyingClassifierBangla, self).__init__()
        self.bert = BertModel.from_pretrained('sagorsarker/bangla-bert-base')
        self.dropout = nn.Dropout(0.1)
        self.fc = nn.Linear(self.bert.config.hidden_size, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, input_ids, attention_mask):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        pooled_output = outputs.pooler_output
        pooled_output = self.dropout(pooled_output)
        logits = self.fc(pooled_output)
        probability = self.sigmoid(logits)
        return probability
    
class CyberBullyingClassifierEnglish(nn.Module):
    def __init__(self):
        super(CyberBullyingClassifierEnglish, self).__init__()
        self.bert = BertModel.from_pretrained('bert-base-uncased')
        self.dropout = nn.Dropout(0.1)
        self.fc = nn.Linear(self.bert.config.hidden_size, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, input_ids, attention_mask):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        pooled_output = outputs.pooler_output
        pooled_output = self.dropout(pooled_output)
        logits = self.fc(pooled_output)
        probability = self.sigmoid(logits)
        return probability

class BullyingProcessor:
    def predict_bangla_cyberbullying(model, texts, device):
        tokenizer = BertTokenizer.from_pretrained('sagorsarker/bangla-bert-base')
        model.eval()
        tokenized_texts = tokenizer.batch_encode_plus(
            texts,
            max_length=128,
            padding='max_length',
            truncation=True,
            return_token_type_ids=False,
            return_attention_mask=True,
            return_tensors='pt'
        )
        inputs = {key: val.to(device) for key, val in tokenized_texts.items()}
        with torch.no_grad():
            outputs = model(**inputs)
        probabilities = outputs.cpu().numpy()
        return probabilities
    
    def predict_english_cyberbullying(model, texts, device):
        tokenizer = BertTokenizer.from_pretrained('bert-base-uncased',do_lower_case=True)
        model.eval()
        tokenized_texts = tokenizer.batch_encode_plus(
            texts,
            max_length=128,
            padding='max_length',
            truncation=True,
            return_token_type_ids=False,
            return_attention_mask=True,
            return_tensors='pt'
        )
        inputs = {key: val.to(device) for key, val in tokenized_texts.items()}
        with torch.no_grad():
            outputs = model(**inputs)
        probabilities = outputs.cpu().numpy()
        return probabilities