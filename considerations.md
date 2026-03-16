## Business Rules and Scheduling Logic

This document defines the exact parameters, execution times, and constraints that govern the
decision algorithm of the AI Agent (**"The Brain"**) and the Flow Manager. The system shall be
programmed to obey these rules strictly whenever it proposes, validates, or confirms a surgical
appointment.

---

### 1. Definition of Operational Capacity ("The Quota")

The system manages the schedule based on an **inventory-of-minutes model**, not on traditional
fixed time slots. Each day has a finite pool of surgical minutes; every appointment consumes
some of those minutes until the daily capacity is exhausted.

**Daily operational parameters**

| Parameter              | Value                                                                                           |
| ---------------------- | ----------------------------------------------------------------------------------------------- |
| Operating days         | Monday to Thursday (Friday, Saturday, and Sunday are blocked by default for surgery, unless otherwise instructed). |
| Surgical work window   | 09:00 to 13:00.                                                                                |
| Maximum daily capacity | **240 minutes** total available per day.                                                       |
| Fill logic             | Each appointment subtracts minutes from this total capacity according to the service table in Section 2. |

**Quota rule**

- Every confirmed surgical appointment has a **Time Cost (minutes)**.
- The sum of all Time Costs for a given day **must never exceed 240 minutes**.
- The remaining quota for a date is:
  - Remaining minutes = 240 − (sum of minutes for all already-booked appointments on that date).

---

### 2. Master Table of Services and Times

The AI Agent shall classify the client's request and assign a duration (**Time Cost**) according
to the tables below. These are the values that shall be **subtracted from the 240-minute quota**
described in Section 1.

#### 2.1 Species: CAT (No quantity limit; only time limit)

For cats, there is **no daily quantity limit** on the number of patients. The only constraint is
that the **total minutes for all appointments (all species combined) remain within the 240-minute
quota**.

**Cat services and Time Cost**

| Service                   | Time (minutes) |
| ------------------------- | -------------- |
| Male cat sterilisation    | 12             |
| Female cat sterilisation  | 15             |

**Note**

- An internal **"Stray cat" alert** may apply where relevant, but the Time Cost for the procedure
  remains standard (as per the table above).

#### 2.2 Species: DOG (Subject to quantity restriction)

For dogs, both **time** and **daily dog count** must be respected.

- Time is determined by **sex and weight** as reported by the client.
- In addition, there is a hard limit of **maximum 2 dogs per operating day**, regardless of
  remaining minutes (see Section 3).

**Dog categories and Time Cost**

| Category                  | Time (minutes) |
| ------------------------- | -------------- |
| Male dog (any weight)     | 30             |
| Female dog (0–10 kg)      | 45             |
| Female dog (10–20 kg)     | 50             |
| Female dog (20–30 kg)     | 60             |
| Female dog (30–40 kg)     | 60             |
| Female dog (>40 kg)       | 70             |

---

### 3. Restriction and Blocking Algorithm ("The Tetris")

To confirm a date for a new appointment, the system must validate **both** of the following
logical conditions positively. If **either** condition fails, the date shall be considered
**"NOT AVAILABLE"** for that appointment.

#### Rule 1: Time validation (sum ≤ 240)

Let:

- `minutes_already_occupied` = sum of Time Costs (in minutes) for all confirmed appointments on
  that date (all species).
- `minutes_for_new_appointment` = Time Cost for the requested service from Section 2.

The time condition is:

\[
minutes\_already\_occupied + minutes\_for\_new\_appointment \leq 240
\]

If this inequality does **not** hold, the system shall **not** allow the booking for that date.

#### Rule 2: Dog limit (max 2)

If the new appointment is classified as **Species: DOG**:

- Let `dog_count_for_the_day` = number of dog appointments already confirmed for that date.
- The dog-count condition is:

\[
dog\_count\_for\_the\_day + 1 \leq 2
\]

If there are already 2 dogs scheduled on a given day, the system shall **block that day for any
further dog request**, even if there are minutes remaining within the 240-minute quota.

**Exception (cats unaffected by dog limit)**

- The dog-count rule does **not** apply to cats.
- A day with 2 dogs may still accept additional cats **until the 240 minutes are filled**.

#### Example: When a date is NOT AVAILABLE

- Assume a given Monday already has:
  - 2 dog surgeries confirmed (any categories), and
  - 160 minutes already occupied.
- A new dog request with a Time Cost of 30 minutes arrives.
  - Time condition: 160 + 30 = 190 ≤ 240 → **passes**.
  - Dog-count condition: dog_count_for_the_day is already 2, so 2 + 1 = 3 > 2 → **fails**.
- Result: The date is **NOT AVAILABLE** for the new dog appointment, even though there are still
  minutes available in the quota.

If, instead, the new request is for a cat sterilisation:

- Only the time condition is checked (no dog-count limit for cats).
- As long as the resulting total minutes remain ≤ 240, the date can still be offered to the
  client for a cat.

---

### 4. Species-Specific Drop-Off Windows (Mandatory)

Drop-off times are **species-specific and non-negotiable**. The system shall only offer and
confirm appointments whose **drop-off** falls within the following windows.

**Drop-off windows by species and day**

| Species | Drop-off window      | Applicable days                                              |
| ------- | -------------------- | ------------------------------------------------------------ |
| Cats    | 08:00–09:00 (strict) | Monday to Friday                                             |
| Dogs    | 09:00–10:30 (strict) | Operating days (Monday to Thursday)                         |

#### Validation rules

- **Cats**
  - A cat **cannot** be dropped off outside **08:00–09:00**.
  - The system shall **not** confirm any cat appointment that would require drop-off outside this
    window.
  - On operating days (Monday–Thursday), cats use the **08:00–09:00** window.
  - On Friday (if opened for cats), the same **08:00–09:00** window applies.

- **Dogs**
  - A dog **cannot** be dropped off outside **09:00–10:30**.
  - The system shall **not** confirm any dog appointment that would require drop-off outside this
    window.

**Summary**

- Cats: drop-off **08:00–09:00**, Monday–Friday.
- Dogs: drop-off **09:00–10:30**, Monday–Thursday (operating days).

---

### 5. Communication and Logistics Protocol

The system shall manage client expectations by explicitly distinguishing between **"Booking"** and
**"Drop-off"**:

- **Booking**: The **day** of surgery that is being reserved.
- **Drop-off**: The **time window** during which the client must bring the animal to the clinic.

The client **never chooses an exact surgical time** (e.g. 10:30). They only choose the **day**,
and the system instructs them on the correct drop-off window.

**Client communication rules**

| Rule                          | Description                                                                                                                                                                       |
| ----------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Hide surgical times           | The client shall **never** select a specific surgical time. They shall select **only the day** of the surgery.                                                                  |
| Species-specific drop-off message | Upon confirming the appointment, the system shall automatically instruct the client with the correct drop-off window:<br>- Cats: “The cat must be dropped off strictly between 08:00 and 09:00 in the morning.”<br>- Dogs: “The dog must be dropped off strictly between 09:00 and 10:30 in the morning for preparation.” |
| Fasting protocol              | Fasting instructions (from **midnight the night before**) shall be attached to the final confirmation message.                                                                  |

---

### 6. Implementation Notes for Engineers

This section provides guidance on how these rules should be enforced in the AI Agent (**"The
Brain"**) and the Flow Manager.

- **Represent daily quota as remaining minutes**
  - For each operating day, keep track of `minutes_already_occupied` and compute
    `remaining_minutes = 240 − minutes_already_occupied`.
  - When evaluating a new request, look up the Time Cost from Section 2 and ensure
    `remaining_minutes − time_cost >= 0`.

- **Track daily dog count separately from minutes**
  - Maintain `dog_count_for_the_day` for each operating day.
  - When the requested species is DOG, enforce `dog_count_for_the_day + 1 ≤ 2` before confirming.
  - For cats, do **not** consult the dog-count limit; only the minute quota matters.

- **Validate appointments against both quota and dog limit before confirming**
  - The Flow Manager should:
    1. Classify the request (species, sex, weight) and derive `time_cost`.
    2. Check Rule 1 (time validation).
    3. If species is DOG, check Rule 2 (dog limit).
    4. Only if all relevant conditions pass, mark the date as available and proceed to booking.

- **Enforce species-specific drop-off windows**
  - When proposing dates, present only those operating days where:
    - The quota and dog limit rules pass; and
    - The required species-specific drop-off window is valid (cats: 08:00–09:00 Mon–Fri; dogs: 09:00–10:30 Mon–Thu).
  - UI and chatbot messages should always express the drop-off **window**, not an exact time.

- **Communicate using day + drop-off window, not exact surgery time**
  - The AI Agent should phrase confirmations like:
    - “We have booked your cat for surgery on **[DAY]**. Please drop off your cat **between 08:00 and 09:00 in the morning**.”
  - This ensures that internal scheduling (within the 09:00–13:00 surgical work window) remains flexible while remaining consistent with the rules above.

- **Centralise configuration**
  - Where possible, treat parameters such as operating days, capacity (240 minutes), and drop-off windows as configuration values, so that the same rules are shared between the AI Agent and any backend services.

By following the rules and implementation notes above, the AI Agent and Flow Manager will make
consistent, predictable decisions that respect the clinic's operational constraints while
communicating clearly with clients.

