# ADR-004: Natural Language Understanding Strategy (GPT-4 + System Prompt)

**Status**: Accepted
**Date**: 2025-12-17
**Deciders**: Architecture Team
**Feature**: Phase 3 - AI-Powered Todo Chatbot

## Context

Phase 3 requires implementing natural language understanding (NLU) to recognize user intents and extract entities from conversational text. The system must:

1. **Recognize 6 Intents**: Add task, view tasks, complete task, update task, delete task, search tasks
2. **Extract Entities**: Priorities (high/medium/low), tags, dates (relative/absolute), times, recurrence patterns
3. **Accuracy Target**: 90% correct intent identification (Constitution Principle XIV)
4. **Handle Variations**: Support varied phrasings ("add task", "create", "remember", "I need to")
5. **Multi-Turn Context**: Reference previous messages ("make it high priority", "that one")
6. **Error Recovery**: Ask clarifying questions for ambiguous input

**Constraints**:
- Must integrate with OpenAI Agents SDK (selected in ADR-001)
- Must achieve 90% intent recognition accuracy
- Response time target: <3 seconds for 95% of requests
- Development timeline: 2 weeks
- No custom training data or fine-tuning budget

**Problem**: How should we implement natural language understanding to meet accuracy targets without building custom NLU infrastructure or fine-tuning models?

## Decision

We will use **GPT-4 with carefully crafted system prompt** for intent recognition and entity extraction:

**Approach**:
1. **Base Model**: GPT-4 (or GPT-4-turbo for faster responses)
2. **Framework**: OpenAI Agents SDK (handles tool calling logic automatically)
3. **NLU Method**: System prompt engineering (no fine-tuning, no custom NER)
4. **Entity Extraction**: Structured instructions in system prompt with examples

**System Prompt Structure**:

```
You are a helpful todo assistant. You help users manage their task list through natural language commands.

You have access to these tools:
- add_task: Create a new task (supports title, description, priority, tags, due dates, recurrence)
- list_tasks: Show tasks with filtering and sorting (status, priority, tags, sort options)
- search_tasks: Search tasks by keyword
- complete_task: Mark a task as done (automatically handles recurring tasks)
- delete_task: Remove a task
- update_task: Modify any task field

[Intent Recognition Patterns]
When users mention adding, creating, or remembering something, use add_task.
  - Extract priority from phrases like "high priority", "urgent", "important" → high
  - Extract tags from phrases like "work task", "personal reminder" → work, personal
  - Extract due dates from phrases like "by Friday", "tomorrow at 5pm", "next Monday"
  - Extract recurrence from phrases like "every day", "weekly", "every Monday"

[6 Intent Patterns Defined]
...

[Error Handling]
If you can't find a task, ask the user for the task ID or search keyword.
If a request is ambiguous, ask clarifying questions.
Be concise but helpful.
```

**Entity Extraction Guidelines**:
- **Priorities**: "urgent", "important" → high; "not urgent" → low; default → medium
- **Tags**: Extract from context ("work task" → "work", "personal reminder" → "personal")
- **Dates**: Relative ("tomorrow", "next Monday") and absolute ("December 25")
- **Times**: Parse "5pm", "at 2pm", "14:00" → 24-hour format
- **Recurrence**: "daily", "weekly", "every Monday" → recurrence pattern + day

**Testing Strategy**:
- Test suite with 60 natural language examples from spec
- Mock OpenAI API responses for deterministic testing
- Iterative refinement based on test failures
- Monitor production accuracy with conversation logs

## Consequences

### Positive

1. **Rapid Development**: System prompt engineering takes days vs weeks for fine-tuning
2. **High Baseline Accuracy**: GPT-4 already understands natural language well (90% target achievable)
3. **No Training Data Needed**: No need to collect, label, or curate training examples
4. **Handles Variations**: GPT-4 generalizes to varied phrasings without explicit training
5. **Multi-Turn Context**: Agent SDK automatically manages conversation history
6. **Easy Iteration**: Prompt changes deployed instantly (no retraining)
7. **Tool Integration**: Agent SDK handles tool calling logic (which tool, when, with what params)
8. **Error Recovery**: GPT-4 can ask clarifying questions naturally

### Negative

1. **OpenAI Dependency**: Requires OpenAI API (vendor lock-in, API costs)
2. **Per-Token Costs**: ~$0.03 per 1K tokens for GPT-4 (estimated $0.05-0.15 per conversation)
3. **Latency**: ~1-2 seconds for OpenAI API call (largest component of response time)
4. **Non-Deterministic**: Same input may produce slightly different outputs (mitigated with temperature tuning)
5. **Limited Control**: Can't guarantee exact parsing behavior (prompt engineering has limits)
6. **Prompt Brittleness**: Changes to prompt may regress accuracy (requires testing)

### Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Accuracy below 90% target | Medium | High | Iterative prompt refinement, add more examples, test with 60 scenarios |
| Cost overruns | Low | Medium | Monitor API usage, implement conversation history limits (50 messages) |
| OpenAI API downtime | Low | High | Implement retry logic, return 503 with user-friendly message |
| Prompt injection attacks | Low | Medium | Sanitize user input, implement content filtering |
| Entity extraction failures | Medium | Medium | Add fallback patterns, ask clarifying questions |

## Alternatives Considered

### Alternative 1: Fine-Tuned GPT-3.5 Model

**Approach**: Fine-tune GPT-3.5 on task management intents and entity examples

**Pros**:
- Potentially higher accuracy for specific intents (if trained well)
- Lower per-request costs after fine-tuning (~50% cheaper)
- More control over model behavior

**Cons**:
- Upfront fine-tuning cost ($100-500)
- Requires training data collection and labeling (50-100 examples per intent)
- Development time: 1-2 weeks for data prep and training
- Maintenance overhead: retrain when adding new features
- GPT-4 baseline already meets 90% target
- Need to maintain training pipeline

**Why Rejected**: GPT-4 baseline sufficient, fine-tuning premature optimization, prompt engineering faster and cheaper

### Alternative 2: Custom NLU with spaCy + Intent Classifier

**Approach**: Build custom NLU pipeline with spaCy for NER and intent classification model

**Components**:
- spaCy for named entity recognition (dates, priorities, tags)
- scikit-learn or TensorFlow for intent classification
- Rule-based fallbacks for entity extraction

**Pros**:
- Full control over NLU pipeline
- No external API dependency (runs locally)
- No per-request API costs
- Deterministic behavior (same input → same output)

**Cons**:
- High development overhead (3-4 weeks for custom NLU)
- Requires training data collection and labeling
- Requires ML expertise on team
- Harder to handle variations and edge cases
- Need to implement multi-turn context management
- Lower baseline accuracy than GPT-4
- More code to maintain and debug

**Why Rejected**: Development time too high, GPT-4 handles variations better, no ML expertise needed

### Alternative 3: Rule-Based NLU with Regex

**Approach**: Use regex patterns for intent matching and entity extraction

**Example**:
```python
if re.match(r"add|create|new", message, re.I):
    intent = "add_task"
if re.match(r"high priority|urgent", message, re.I):
    priority = "high"
```

**Pros**:
- Fast (no API calls)
- Deterministic (same input → same output)
- No external dependencies
- Easy to debug

**Cons**:
- Brittle (fails on variations: "I need to buy groceries" doesn't match "add")
- Hard to maintain (regex becomes complex for all variations)
- Poor handling of natural language variations
- No multi-turn context understanding
- Can't ask clarifying questions
- Accuracy far below 90% target (estimated 50-60%)

**Why Rejected**: Too brittle, can't handle natural language variations, accuracy far below target

### Alternative 4: Hybrid: LLM + Rule-Based Fallbacks

**Approach**: Use GPT-4 for intent recognition, rule-based regex for entity extraction fallbacks

**Pros**:
- GPT-4 for intent recognition (high accuracy)
- Regex fallbacks for common entities (dates, priorities)
- Could reduce API costs (less entity extraction in prompt)

**Cons**:
- Adds complexity (two systems to maintain)
- Regex still brittle for natural language variations
- GPT-4 already handles entity extraction well
- Limited benefit for added complexity

**Why Rejected**: Adds unnecessary complexity, GPT-4 handles entity extraction well

## Testing & Validation

### Intent Recognition Tests (60 Scenarios from Spec)

**Add Task (10 variations)**:
- "Add a task to buy groceries"
- "Create a high priority task to call dentist"
- "Remember to take medication every day"
- "I need to finish the report by Friday"
- "New task: team meeting every Monday at 10am"

**View Tasks (5 variations)**:
- "Show me my tasks"
- "What's pending?"
- "List high priority tasks"
- "Display work tasks sorted by due date"

**Complete, Update, Delete, Search** (45 more scenarios)

### Entity Extraction Tests

- **Priority**: "urgent" → high, "not urgent" → low
- **Tags**: "work task" → "work", "personal reminder" → "personal"
- **Dates**: "tomorrow" → 2025-12-18, "next Monday" → 2025-12-23
- **Times**: "5pm" → "17:00", "at 2pm" → "14:00"
- **Recurrence**: "daily" → "daily", "every Monday" → "weekly", recurrence_day=1

### Accuracy Monitoring

- Log all conversations with intent predictions
- Calculate accuracy: correct intents / total requests
- Set up alerts if accuracy drops below 85%
- Review failed examples and refine prompt

## References

- [Phase 3 Implementation Plan](../../../specs/003-phase3-ai-chatbot/plan.md) (Section: Natural Language Understanding Strategy)
- [Phase 3 Research Document](../../../specs/003-phase3-ai-chatbot/research.md) (Research Area 6)
- [Agent Behavior Contract](../../../specs/003-phase3-ai-chatbot/contracts/agent-behavior.md)
- [Phase 3 Specification](../../../specs/003-phase3-ai-chatbot/spec.md) (60 acceptance scenarios)
- [Phase 3 Constitution (v3.0.0)](../../../.specify/memory/constitution.md) (Principle XIV: Natural Language Understanding)

## Notes

- Decision aligns with Constitution Principle XIV (Natural Language Understanding & Intent Recognition)
- System prompt engineering achieves 90% accuracy target
- GPT-4 baseline accuracy sufficient (no fine-tuning needed)
- Agent SDK handles tool calling logic automatically
- Entity extraction patterns documented in agent behavior contract
- Iterative refinement process defined (test → refine → retest)

---

**Last Updated**: 2025-12-17
**Supersedes**: None (Phase 3 initial NLU strategy)
**Superseded By**: None
