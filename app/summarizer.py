from transformers import pipeline

class Summarizer:
    def __init__(self):
        self.summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

    def summarize(self, text):
        # Limit input to 1024 tokens (model constraint)
        summary = self.summarizer(text[:1024], max_length=130, min_length=30, do_sample=False)
        return summary[0]['summary_text']

summarizer = Summarizer()
