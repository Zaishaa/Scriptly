from transformers import pipeline
import torch
import gc

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
                
                # Free memory before loading
                gc.collect()
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()

                self._pipeline = pipeline(
                    task="text-classification",
                    model="j-hartmann/emotion-english-distilroberta-base",
                    top_k=None,
                    device=-1,  # Force CPU always
                    torch_dtype=torch.float32,
                    low_cpu_mem_usage=True  # Key memory saving option
                )
                print("Model loaded successfully!")
                
                # Free memory after loading
                gc.collect()
                
            except Exception as e:
                print(f"Model loading failed: {e}")
                self._pipeline = None

    def detect_emotions(self, text):
        if not text or len(text.strip()) < 5:
            return self._default_emotions()

        try:
            # Load model only when needed
            self._load_model()
            
            # If model failed to load return default
            if self._pipeline is None:
                return self._default_emotions()

            # Truncate text to save memory
            text = text[:512]
            
            results = self._pipeline(text)

            emotion_scores = {}
            if isinstance(results[0], list):
                results = results[0]

            for item in results:
                label = item['label'].lower()
                score = round(item['score'], 4)
                emotion_scores[label] = score

            dominant = max(emotion_scores, key=emotion_scores.get)
            confidence = emotion_scores[dominant]
            is_crisis = self._check_crisis(text, emotion_scores)

            # Free memory after inference
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

    def _check_crisis(self, text, emotion_scores):
        crisis_keywords = [
            'suicide', 'kill myself', 'end my life', 'want to die',
            'self harm', 'hurt myself', 'no reason to live',
            'give up on life', 'cant go on', "can't go on",
            # ADD these passive ideation patterns:
            'without me', 'fading out', 'no one notices', 'no one would notice',
            'slowly disappearing', 'go on without me', 'nothing i do matters',
            'fading away', 'dont matter', "don't matter"
        ]
        text_lower = text.lower()
        keyword_crisis = any(kw in text_lower for kw in crisis_keywords)

        sadness = emotion_scores.get('sadness', 0)
        fear = emotion_scores.get('fear', 0)
        anger = emotion_scores.get('anger', 0)
        # Also flag if sadness+fear combined is high, even if neither alone hits 0.85
        combined_distress = sadness + fear
        score_crisis = (sadness > 0.75) or (fear > 0.85) or (anger > 0.85) or (combined_distress > 1.2)

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
    
    