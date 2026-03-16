---
name: langchain-expert
description: Provides deep, opinionated guidance on designing, implementing, and debugging LangChain-based chatbots and tools for this veterinary clinic project. Use when the user mentions LangChain, chains, tools, agents, memory, RAG, or wants to evolve the clinic chatbot architecture.
---

# LangChain Expert for Veterinary Clinic Chatbot

## When to apply this skill

Use this skill whenever the work involves:

- Building or refactoring **LangChain** chains, agents, or tools.
- Implementing **session-based memory** for the clinic chatbot.
- Wiring up **RAG** over the clinic’s pre-surgery documentation.
- Implementing the **booking-quota availability tool** as a LangChain tool.
- Debugging or improving **conversation flow, tool calls, or prompt structure** in the chatbot.

This skill is tailored specifically to the **ENAE25 Veterinary Clinic** chatbot in this repository.

---

## Core design principles for this project

- **Single responsibility per component**
  - Keep concerns separated:
    - One module for **domain rules & quota logic** (minutes, dog-count, drop-off rules).
    - One module for **RAG / retrieval** over the pre-surgery documentation.
    - One module for **chat orchestration** (chains/agents, memory, tools).
  - Avoid mixing low-level HTTP, domain logic, and prompt text in the same file.

- **Configuration over hard-coding**
  - Centralise in config:
    - Operating days.
    - Daily quota (240 minutes).
    - Service time costs table for cats/dogs.
    - Drop-off windows by species.
  - Make LangChain components **read from config**, so updates don’t require prompt edits.

- **Deterministic tools, flexible LLM**
  - All **business rules** (quota, dog limit, drop-off windows) must be enforced in **code**.
  - The LLM may **explain** decisions, but never override the tool’s result.
  - Tools should be:
    - Pure functions from inputs → outputs.
    - Easy to test in isolation.

---

## Recommended LangChain architecture

### 1. Tooling layer

Define tools that encapsulate non-LLM logic:

- **`check_surgery_date_availability` tool**
  - Inputs:
    - Species (dog/cat).
    - Sex.
    - For dogs: weight band.
    - Desired date.
  - Behaviour:
    - Maps to a **Time Cost** using the service tables.
    - Looks up existing bookings for that date.
    - Computes:
      - `minutes_already_occupied`.
      - `dog_count_for_the_day`.
      - `remaining_minutes = 240 − minutes_already_occupied`.
    - Returns:
      - `status`: `"AVAILABLE"` or `"NOT_AVAILABLE"`.
      - `reason`: short explanation (e.g. `"exceeds 240-minute quota"`, `"max 2 dogs reached"`).
      - `remaining_minutes`.
      - `dog_count_for_the_day`.

- **`get_clinic_pre_surgery_info` tool (optional)**
  - Wraps a retriever over the pre-surgery documentation.
  - Accepts a query and returns the **top-k relevant chunks**.
  - The LLM is responsible for synthesising user-facing answers from these chunks.

Expose tools to LangChain using the appropriate wrapper (`Tool` / `StructuredTool`) with clear, typed schemas and concise docstrings describing **what** they do and **when** to call them.

### 2. Memory and state

- Use **session-based memory** keyed by a `session_id` passed from the client.
- Preferred patterns:
  - For simple chat: `ConversationBufferMemory` or `ConversationSummaryMemory`.
  - For tools-heavy agents: `ConversationBufferMemory` combined with tool output tracking.
- Always store:
  - Pet details (name, species, sex, weight band, age).
  - Previously discussed constraints (preferred date ranges, known illnesses).
  - Decisions that must stay consistent (e.g. “blood test mandatory because >6 years”).

Ensure memory does **not** store unnecessary PHI/PII beyond what is required by the clinic.

### 3. Orchestration pattern

Prefer a **tool-using agent** or a **Router → Tool chain**:

- Use **system messages** to:
  - Enforce scope: sterilisation, vaccination, microchip only.
  - Remind the agent to:
    - Call the **availability tool** whenever a booking day is being evaluated.
    - Use the **RAG tool** for any clinical/pre-surgery/after-care questions.
    - Never invent medical guidance beyond retrieved content.
    - Communicate **day + drop-off window**, not surgery time.

- Use **human messages** for user utterances.
- Use **tool messages** to represent tool calls and results in the chat history.

The agent should:

1. Collect sufficient booking details.
2. Call the availability tool with a proposed day.
3. If unavailable, iterate with the user to find a valid alternative.
4. Once a valid day is found, generate a **confirmation message** including:
   - Booked day.
   - Correct drop-off window (based on species).
   - Fasting and paperwork instructions sourced from RAG.

---

## Prompting guidelines

- **System prompt must encode hard constraints**
  - Always include:
    - “The clinic only provides sterilisation, vaccination, and microchip services.”
    - “Do not handle general illness or emergency care; advise contacting another practice.”
    - “Use the surgery booking tool to validate availability; never override its result.”
    - “When explaining preparation or after-care, base answers only on the retrieved clinic documentation.”

- **User-friendly but precise language**
  - Avoid technical jargon in user-facing answers.
  - Be explicit about:
    - Fasting schedule.
    - Required documents.
    - Approximate pick-up expectations, if configured.
    - Warning signs that require contacting the clinic.

- **Separation of booking vs information**
  - For booking questions:
    - Focus on **dates, quota, and drop-off windows**.
  - For clinical information:
    - Focus on **RAG-based answers** and clearly separate them from booking logistics.

---

## Implementation checklist

When implementing or modifying LangChain code in this repo, follow this checklist:

- [ ] **Define or reuse** a clear config source for quota and service tables.
- [ ] Implement or update the **availability tool** as a pure function.
- [ ] Wrap the tool as a **LangChain Tool/StructuredTool** with proper schema.
- [ ] Set up a **retriever** over the clinic’s pre-surgery documentation.
- [ ] Build a **tool-using agent** (or equivalent) with:
  - [ ] System prompt that encodes scope and constraints.
  - [ ] Access to both availability and RAG tools.
  - [ ] Session-based memory keyed by `session_id`.
- [ ] Add unit tests for:
  - [ ] Quota boundary conditions (0, 240 minutes, >240).
  - [ ] Dog-count rule (0, 1, 2, >2 dogs).
  - [ ] Cat bookings on days with 2 dogs.
- [ ] Add integration tests or scripted conversations for:
  - [ ] Happy-path booking (cat).
  - [ ] Happy-path booking (dog).
  - [ ] Day rejected due to quota.
  - [ ] Day rejected due to dog limit but still available for cats.

---

## Example usage scenarios

### Scenario 1 – Add a new conversation entry point

1. Update the conversation entry handler to accept a `session_id`.
2. Initialise a LangChain agent with:
   - Memory bound to that `session_id`.
   - Access to availability and RAG tools.
3. Ensure the system prompt is loaded from a **single source of truth** so that:
   - Booking rules.
   - Clinic scope.
   - Safety constraints.
   stay in sync with configuration files and repository rules.

### Scenario 2 – Debug incorrect date proposal

When the chatbot suggests an invalid or disallowed date:

1. Reproduce the conversation with logging enabled for:
   - Tool input/output.
   - LLM reasoning (if available).
2. Verify:
   - The availability tool receives the correct inputs.
   - The tool’s return value is correct according to the config.
3. If the tool is correct but the LLM still confirms a booking:
   - Strengthen the system prompt:
     - Emphasise “never contradict tool outputs”.
   - Optionally wrap booking confirmation in **post-check code** that rejects confirmation if the tool result is not `"AVAILABLE"`.

---

## How the agent should use this skill

When this skill is active, the agent should:

- Prefer **code-level enforcement** of business rules over prompt-only enforcement.
- Propose **modular LangChain designs** instead of monolithic scripts.
- Default to **simple, testable chains** before introducing more complex agent behaviour.
- Always respect:
  - The clinic’s **service scope**.
  - The **booking-quota rules**.
  - The **pre-surgery documentation** as the source of truth for clinical messaging.

