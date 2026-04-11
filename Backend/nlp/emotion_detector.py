from transformers import pipeline
import torch

class EmotionDetector:
    _instance = None
    _pipeline = None

    def __new__(cls):
        # Singleton pattern - load model only once
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_model()
        return cls._instance

    def _load_model(self):
        print("Loading emotion detection model...")
        device = 0 if torch.cuda.is_available() else -1
        self._pipeline = pipeline(
            task="text-classification",
            model="j-hartmann/emotion-english-distilroberta-base",
            top_k=None,
            device=device
        )
        print("Model loaded successfully!")

    def detect_emotions(self, text):
        if not text or len(text.strip()) < 5:
            return self._default_emotions()

        try:
            # Truncate text to avoid token limit
            text = text[:1000]
            results = self._pipeline(text)

            # Results come as list of dicts
            emotion_scores = {}
            if isinstance(results[0], list):
                results = results[0]

            for item in results:
                label = item['label'].lower()
                score = round(item['score'], 4)
                emotion_scores[label] = score

            # Get dominant emotion
            dominant = max(emotion_scores, key=emotion_scores.get)
            confidence = emotion_scores[dominant]

            # Check for crisis
            is_crisis = self._check_crisis(text, emotion_scores)

            return {
                'dominant_emotion': dominant,
                'confidence_score': confidence,
                'emotion_scores': emotion_scores,
                'is_crisis': is_crisis
            }

        except Exception as e:
            print(f"Emotion detection error: {e}")
            return self._default_emotions()

    def _check_crisis(self, text, emotion_scores):
        # Crisis keywords
        crisis_keywords = [
            'suicide', 'kill myself', 'end my life', 'want to die',
            'self harm', 'hurt myself', 'no reason to live',
            'give up on life', 'cant go on', "can't go on"
        ]

        text_lower = text.lower()
        keyword_crisis = any(kw in text_lower for kw in crisis_keywords)

        # High negative emotion threshold
        sadness = emotion_scores.get('sadness', 0)
        fear = emotion_scores.get('fear', 0)
        anger = emotion_scores.get('anger', 0)
        score_crisis = (sadness > 0.85) or (fear > 0.85) or (anger > 0.85)

        return keyword_crisis or score_crisis

    def _default_emotions(self):
        return {
            'dominant_emotion': 'neutral',
            'confidence_score': 0.0,
            'emotion_scores': {
                'joy': 0.0,
                'sadness': 0.0,
                'anger': 0.0,
                'fear': 0.0,
                'love': 0.0,
                'surprise': 0.0
            },
            'is_crisis': False
        }