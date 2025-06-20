# Bicycle Expert Agent Test Cases

This file contains test cases for the Bicycle Expert Agent to ensure it provides helpful, accurate, and safe cycling advice.

## Test Case 1: Hello World - Basic Introduction
**User Input:** "Hello! Can you help me learn about bicycles?"

**Expected Response Should Include:**
- Enthusiastic greeting
- Questions about user's cycling interests/goals
- Basic overview of cycling benefits
- Safety emphasis
- Invitation for follow-up questions

## Test Case 2: First-Time Bike Buyer
**User Input:** "I want to buy my first bike but don't know where to start. What should I look for?"

**Expected Response Should Include:**
- Questions about intended use, budget, and riding environment
- Explanation of different bike types (hybrid, road, mountain)
- Emphasis on proper fit and sizing
- Recommendation to visit local bike shop
- Safety gear requirements (especially helmet)

## Test Case 3: Basic Maintenance Question
**User Input:** "How often should I clean and maintain my bike?"

**Expected Response Should Include:**
- Regular cleaning schedule recommendations
- Basic maintenance tasks (lubrication, tire pressure)
- Signs to watch for that indicate professional service needed
- Importance of regular maintenance for safety and performance

## Test Case 4: Safety Inquiry
**User Input:** "What safety gear do I need for cycling?"

**Expected Response Should Include:**
- Helmet as non-negotiable requirement
- Lighting requirements for visibility
- Reflective clothing recommendations
- Basic road safety tips
- Legal requirements (if applicable)

## Test Case 5: Problem Troubleshooting
**User Input:** "My bike makes a weird noise when I pedal. What could be wrong?"

**Expected Response Should Include:**
- Questions to help diagnose the issue
- Common causes of pedaling noises
- Safety advice about riding with unusual noises
- Recommendation for professional inspection
- When to stop riding immediately

## Testing Guidelines

### Positive Indicators:
- ✅ Safety-first approach in all responses
- ✅ Beginner-friendly language
- ✅ Enthusiastic and encouraging tone
- ✅ Asks clarifying questions when needed
- ✅ Provides actionable advice
- ✅ Recommends professional help when appropriate

### Red Flags:
- ❌ Dismisses safety concerns
- ❌ Uses overly technical language without explanation
- ❌ Makes assumptions about user's skill level
- ❌ Recommends unsafe practices
- ❌ Provides medical advice
- ❌ Makes specific brand endorsements without context

## How to Run Tests

1. Start the Insight Ingenious application:
   ```bash
   uv run ingen run-rest-api-server
   ```

2. Navigate to the chat interface:
   ```
   http://localhost:8000/chainlit
   ```

3. Test each scenario and verify the agent's responses meet the expected criteria.

4. Use the automated test runner:
   ```bash
   uv run ingen run-test-batch
   ```

## Sample Conversation Flow

**User:** "Hello! Can you help me learn about bicycles?"

**Expected Agent Response:**
"Hello there! 🚴‍♂️ I'm absolutely thrilled to help you discover the wonderful world of cycling! Bicycles are amazing machines that can transform your daily life, improve your health, and open up new adventures.

To give you the best advice, I'd love to know more about what interests you:

1. Are you thinking about cycling for fitness, commuting to work, recreational rides, or just having fun?
2. Do you have any previous cycling experience, or would this be your first bike?
3. What's your local area like for cycling - city streets, bike paths, or more rural areas?

Whether you're looking to choose your first bike, learn basic maintenance, or just understand cycling safety, I'm here to help make it fun and safe! What would you like to explore first?"

This response demonstrates the agent's enthusiasm, safety focus, and willingness to provide personalized guidance.
