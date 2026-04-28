from transformers import pipeline
import torch
import gc
import re

# Emotion labels that j-hartmann model returns.
# It includes 'disgust' and 'neutral' in addition to the 6
# your DB stores. We map them gracefully below.
SUPPORTED_EMOTIONS = {'joy', 'sadness', 'anger', 'fear', 'love', 'surprise'}

# Passive and indirect crisis signals
CRISIS_KEYWORDS = [
    'suicide', 'kill myself', 'end my life', 'want to die',
    'self harm', 'hurt myself', 'no reason to live',
    'give up on life', 'cant go on', "can't go on",
    'end it all', 'not want to be here', 'wish i was dead',
    'without me', 'go on without', 'better off without me',
    'fading out', 'fading away', 'slowly disappearing',
    'no one notices', 'no one would notice', 'no one would care',
    'nothing i do matters', "don't matter", 'dont matter',
    'not here anymore', 'disappear forever', 'tired of living',
    'what is the point', "what's the point", 'no point anymore',
]


class EmotionDetector:
    _instance = None
    _pipeline = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._pipeline = None
        return cls._instance

    def _load_model(self):
        if self._pipeline is None:
            try:
                print("Loading emotion detection model...")
                gc.collect()
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()

                self._pipeline = pipeline(
                    task="text-classification",
                    model="j-hartmann/emotion-english-distilroberta-base",
                    top_k=None,
                    device=-1,
                    torch_dtype=torch.float32,
                    low_cpu_mem_usage=True
                )
                print("Model loaded successfully!")
                gc.collect()

            except Exception as e:
                print(f"Model loading failed: {e}")
                self._pipeline = None

    def detect_emotions(self, text):
        if not text or len(text.strip()) < 5:
            return self._default_emotions()

        try:
            self._load_model()
            if self._pipeline is None:
                return self._default_emotions()

            # Truncate by words not characters
            words = text.split()
            if len(words) > 400:
                text = ' '.join(words[:400])

            results = self._pipeline(text)

            emotion_scores = {}
            if isinstance(results[0], list):
                results = results[0]

            for item in results:
                label = item['label'].lower()
                score = round(item['score'], 4)
                emotion_scores[label] = score

            # Inject love score based on text analysis
            emotion_scores = self._inject_love_score(text, emotion_scores)

            # Determine dominant after love injection
            dominant = max(emotion_scores, key=emotion_scores.get)
            confidence = emotion_scores[dominant]
            is_crisis = self._check_crisis(text, emotion_scores)

            gc.collect()

            return {
                'dominant_emotion': dominant,
                'confidence_score': confidence,
                'emotion_scores': emotion_scores,
                'is_crisis': is_crisis
            }

        except Exception as e:
            print(f"Emotion detection error: {e}")
            gc.collect()
            return self._default_emotions()

    # ------------------------------------------------------------------
    # Love score injection
    # ------------------------------------------------------------------

    def _inject_love_score(self, text, emotion_scores):
        """
        Love injection logic:
        - Only triggers when ALL three conditions are true:
            1. Model detected joy as dominant
            2. Text contains "love" keyword
            3. "love" is NOT part of "love to" / "would love to" etc.
        - In all other cases: love = 0.0, joy stays as-is.
        """
        text_lower = text.lower()

        # Condition 1: joy must be dominant
        dominant = max(emotion_scores, key=emotion_scores.get)
        if dominant != 'joy':
            emotion_scores['love'] = 0.0
            return emotion_scores

        # Condition 2: "love" word must be present
        if 'love' not in text_lower:
            emotion_scores['love'] = 0.0
            return emotion_scores

        # Condition 3: exclude "love to" in all its forms
        LOVE_TO_EXCLUSIONS = [
            'love to ',
            "love to,",
            "love to.",
            'would love to',
            "i'd love to",
            "id love to",
            "i would love to",
            "loved to ",
        ]
        is_love_to = any(excl in text_lower for excl in LOVE_TO_EXCLUSIONS)
        if is_love_to:
            emotion_scores['love'] = 0.0
            return emotion_scores

        # All 3 conditions passed — convert joy to love
        joy_score = emotion_scores.get('joy', 0.0)
        emotion_scores['love'] = joy_score              # love gets the joy score
        emotion_scores['joy'] = round(joy_score * 0.20, 4)  # joy drops to near zero

        return emotion_scores

    # ------------------------------------------------------------------
    # Crisis detection
    # ------------------------------------------------------------------

    def _check_crisis(self, text, emotion_scores):
        text_lower = text.lower()
        keyword_crisis = any(kw in text_lower for kw in CRISIS_KEYWORDS)

        sadness = emotion_scores.get('sadness', 0)
        fear = emotion_scores.get('fear', 0)
        anger = emotion_scores.get('anger', 0)
        combined_distress = sadness + fear

        score_crisis = (
            (sadness > 0.75) or
            (fear > 0.75) or
            (anger > 0.85) or
            (combined_distress > 0.60)
        )

        return keyword_crisis or score_crisis

    # ------------------------------------------------------------------

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
