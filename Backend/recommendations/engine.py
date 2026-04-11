RECOMMENDATIONS = {
    'joy': [
        {
            'category': 'gratitude',
            'title': 'Capture This Joy!',
            'description': 'You are feeling joyful today! This is a perfect moment to practice gratitude and amplify positive emotions.',
            'action_steps': '1. Write down 3 things that made you happy today.\n2. Share your happiness with someone you care about.\n3. Do one thing that you have been postponing.\n4. Celebrate this feeling — you deserve it!'
        },
        {
            'category': 'social',
            'title': 'Spread the Positivity',
            'description': 'Joy is contagious! Use this positive energy to strengthen your relationships.',
            'action_steps': '1. Call or message a friend or family member.\n2. Do a random act of kindness today.\n3. Write a thank you note to someone who helped you.\n4. Plan something fun for the near future.'
        }
    ],
    'sadness': [
        {
            'category': 'motivation',
            'title': 'You Are Not Alone',
            'description': 'Feeling sad is completely human. Every storm runs out of rain. Here are some gentle steps to help you feel better.',
            'action_steps': '1. Allow yourself to feel — do not suppress emotions.\n2. Listen to your favorite music for 10 minutes.\n3. Step outside for a short 5-minute walk.\n4. Write down one good thing, however small, from today.\n5. Reach out to someone you trust.'
        },
        {
            'category': 'physical',
            'title': 'Move Your Body, Lift Your Mood',
            'description': 'Physical movement releases endorphins which are natural mood boosters.',
            'action_steps': '1. Do 10 jumping jacks right now.\n2. Stretch your arms and neck for 2 minutes.\n3. Take a 15-minute walk outside.\n4. Dance to one song you love.\n5. Drink a glass of water — dehydration worsens mood.'
        }
    ],
    'anger': [
        {
            'category': 'calming',
            'title': '4-7-8 Breathing Technique',
            'description': 'Anger is energy. Let us channel it constructively with this proven breathing technique used by therapists worldwide.',
            'action_steps': '1. Inhale through nose for 4 seconds.\n2. Hold breath for 7 seconds.\n3. Exhale through mouth for 8 seconds.\n4. Repeat 4 times.\n5. After breathing, write what triggered the anger without judgment.\n6. Wait 10 minutes before responding to any situation.'
        },
        {
            'category': 'physical',
            'title': 'Release the Tension',
            'description': 'Physical release helps process anger safely and effectively.',
            'action_steps': '1. Do 20 push-ups or squats.\n2. Squeeze a pillow or stress ball tightly then release.\n3. Go for a brisk 10-minute walk.\n4. Splash cold water on your face.\n5. Write an unsent letter expressing your feelings.'
        }
    ],
    'fear': [
        {
            'category': 'breathing',
            'title': 'Box Breathing for Anxiety',
            'description': 'Fear and anxiety activate our fight-or-flight response. Box breathing is used by Navy SEALs to calm the nervous system instantly.',
            'action_steps': '1. Sit comfortably and close your eyes.\n2. Inhale slowly for 4 seconds.\n3. Hold for 4 seconds.\n4. Exhale for 4 seconds.\n5. Hold for 4 seconds.\n6. Repeat 5 times.\n7. Remind yourself: This feeling is temporary. I am safe right now.'
        },
        {
            'category': 'motivation',
            'title': 'Face Fear With Facts',
            'description': 'Our mind often exaggerates fears. Let us challenge those thoughts with logic.',
            'action_steps': '1. Write down exactly what you are afraid of.\n2. Ask: What is the actual probability of this happening?\n3. Ask: What is the worst case? Can I survive it?\n4. Ask: What is the best case?\n5. Write 3 times you overcame something scary before.\n6. Take one small action toward what scares you today.'
        }
    ],
    'love': [
        {
            'category': 'gratitude',
            'title': 'Nurture This Beautiful Feeling',
            'description': 'You are experiencing love and warmth. This is one of the most powerful human emotions. Cherish and deepen it.',
            'action_steps': '1. Express your feelings to the person or thing you love.\n2. Write a heartfelt message to someone important to you.\n3. Do something kind for someone without expecting anything back.\n4. Practice self-love — write 5 things you love about yourself.\n5. Create a happy memory today.'
        }
    ],
    'surprise': [
        {
            'category': 'motivation',
            'title': 'Embrace the Unexpected',
            'description': 'Surprise means something unexpected happened. Whether good or challenging, surprises help us grow.',
            'action_steps': '1. Take 5 deep breaths to center yourself.\n2. Write down what surprised you and how it made you feel.\n3. Ask: What can I learn from this?\n4. Talk to someone about what happened.\n5. Remember: Life is full of surprises — flexibility is a superpower.'
        }
    ],
    'neutral': [
        {
            'category': 'gratitude',
            'title': 'Daily Mindfulness Check-in',
            'description': 'A calm mind is a powerful mind. Use this neutral moment to practice mindfulness.',
            'action_steps': '1. Take 3 deep breaths right now.\n2. Write down 3 things you are grateful for today.\n3. Set one small intention for tomorrow.\n4. Do something creative for 10 minutes.\n5. Reflect: What went well today?'
        }
    ]
}

CRISIS_RECOMMENDATIONS = [
    {
        'category': 'professional',
        'title': 'You Matter — Please Reach Out',
        'description': 'We noticed your journal entry contains signs of intense distress. You are not alone and help is available. Please reach out to someone you trust or a professional immediately.',
        'action_steps': '1. Call iCall India: 9152987821\n2. Call Vandrevala Foundation: 1860-2662-345 (24/7)\n3. Text a trusted friend or family member right now.\n4. If in immediate danger, call emergency services: 112\n5. Remember: Asking for help is the bravest thing you can do.',
        'is_crisis_recommendation': True
    },
    {
        'category': 'breathing',
        'title': 'Immediate Grounding Exercise',
        'description': 'Use the 5-4-3-2-1 grounding technique to bring yourself back to the present moment.',
        'action_steps': '1. Name 5 things you can SEE right now.\n2. Name 4 things you can TOUCH right now.\n3. Name 3 things you can HEAR right now.\n4. Name 2 things you can SMELL right now.\n5. Name 1 thing you can TASTE right now.\n6. Take 3 slow deep breaths.\n7. You are safe. You are here. You are not alone.',
        'is_crisis_recommendation': True
    }
]


class RecommendationEngine:
    def generate(self, emotion_analysis):
        emotion = emotion_analysis.dominant_emotion
        is_crisis = emotion_analysis.is_crisis

        recommendations = []

        # Always add crisis recommendations first if crisis detected
        if is_crisis:
            recommendations.extend(CRISIS_RECOMMENDATIONS)

        # Add emotion-specific recommendations
        emotion_recs = RECOMMENDATIONS.get(emotion, RECOMMENDATIONS['neutral'])
        recommendations.extend(emotion_recs)

        return recommendations