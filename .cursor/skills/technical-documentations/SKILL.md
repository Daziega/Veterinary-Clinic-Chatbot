---
name: technical-documentations
description: Summarises and applies the clinic's pre-surgery technical documentation (cats and dogs) when generating chatbot flows, patient-facing instructions, FAQs, and case-study materials. Use when the user mentions pre-surgery, sterilisation instructions, ENAE Session 1, Event Storming, SDD, or this veterinary clinic case study.
---

# Technical Documentations – Pre-Surgery (Veterinary Clinic Case Study)

## Purpose

This skill encodes the clinic's **pre-surgery information for canine and feline sterilisation** as a concise reference for agents.
Use it whenever you need to:

- Draft or refine **chatbot conversations**, **FAQs**, **checklists**, or **handouts** about neutering/spaying at this clinic.
- Support **Event Storming** and **Service Design / SDD** work for ENAE Session 1 using this clinic as a case study.
- Ensure outputs remain **clinically consistent** with the given documentation (but separate from booking-quota rules).

The clinic is **almost exclusively preventive-medicine focused**:
- **Sterilisation (neutering/spaying) of dogs and cats.**
- **Vaccination and microchip identification.**
- It **does not** provide routine consultations or emergency care.

## High‑Level Behaviour

When using this skill:

1. **Respect scope of services**
   - The clinic **only** offers:
     - Canine and feline sterilisation.
     - Vaccination and microchipping.
   - It **does not** see general illness or emergency cases; instruct clients to contact another practice for those.
   - If a complication is **related to the sterilisation**, direct them to **phone/WhatsApp during opening hours**.

2. **Stay aligned with booking rules**
   - For **capacity, quotas, days, and drop-off windows**, defer to the repository booking-quota rules.
   - This skill focuses on **clinical preparation, aftercare, and communication**, not slot allocation.

3. **Use patient-friendly language**
   - Explain risks and care clearly and calmly.
   - Avoid alarmist language while being honest about anaesthetic risk.

## Clinical Content Summary

### What the procedure involves

- **Castration / sterilisation under general anaesthesia**:
  - **Males**: removal of testicles (**orchiectomy**).
  - **Females**: removal of ovaries and uterus (**ovariohysterectomy**).
- **Incisions**
  - Female cats (uncomplicated): ~**1.5 cm** abdominal incision.
  - Female dogs: incision length varies with dog size.
- **Sutures**
  - Stitches are **intradermal/internal**, absorbable, and do **not** need removal.
  - After surgery, **females no longer come into heat**.
- **Heat / oestrus rules**
  - **Cats**: can be operated **while in heat**.
  - **Dogs**: **must not** be operated while in heat. Surgery should be scheduled **2 months after** the end of heat to reduce risk of false (“psychological”) pregnancy.

### Before the operation

- **General health**
  - Animals should be **vaccinated and dewormed** (internal and external), **including indoor-only cats**.
  - Any surgery and general anaesthesia carry risk (including death), so:
    - The animal should be **healthy and strong** at the time of surgery.
    - If there is **any illness or condition**, the owner must inform the clinic **before booking**; surgery may be contraindicated or need special planning.
  - In healthy animals, this is considered a **routine, low-risk procedure**.

- **Pre-operative blood test**
  - A **pre-op blood test is recommended for greater safety**.
  - The clinic may refer clients to a **partner lab** for blood tests and check-ups when a condition is suspected.
  - Owners must state they are **referred by the clinic** so results are sent to the clinic.
  - The blood test is **mandatory for animals over 6 years old** due to increased anaesthetic risk.
  - The **cost of the blood test** is paid directly at the lab.

- **Cancellations**
  - If the owner will not attend the appointment, they should **notify at least 24 hours in advance**.
  - Otherwise, the clinic may apply a **surcharge**.

- **Fasting**
  - **Food**: last meal **8–12 hours before** surgery.
  - **Water**: allowed until **1–2 hours before** surgery (especially important in summer).

### Day of surgery

- **Documentation and arrival**
  - Owners must:
    - Arrive on time.
    - Bring the **signed informed consent form**.
    - Bring the animal’s **documentation** (European passport or health card).
  - Current regulations: **microchip and rabies vaccination are mandatory** for dogs and cats.

- **Microchip on the day**
  - Microchipping can be done **under anaesthesia** during surgery.
  - Its **cost is separate** from the sterilisation and may include microchip, rabies vaccine, and passport.

- **Transport requirements**
  - **Cats**:
    - Must arrive in a **rigid carrier** with a blanket or towel inside.
    - Blanket/towel is used to **cover them after surgery** and **absorb fluids** (urine, vomit) during transport.
    - **Cardboard boxes or fabric carriers are not acceptable**.
    - If bringing multiple cats, **each cat must be in its own carrier**.
  - **Dogs**:
    - Must always be on **collar/harness and lead**, never loose.
    - A **muzzle is required** if they may bite strangers.

- **Consent and payment**
  - The **registered microchip owner** must complete and sign the informed consent.
  - If they cannot attend:
    - They should sign the consent at home.
    - Send it with the animal and accompanying person.
  - Payment can be made **in cash or by card**.

- **Indicative pick-up times**
  - **Cats**: approximately **15:00**.
  - **Dogs**: approximately **12:00**; dog surgeries are usually scheduled **first thing in the morning**.
  - If these times do not suit the owner, they should mention it **when booking** so alternatives can be arranged if possible.

### After the operation

- **Environment and activity**
  - Keep the animal in a **quiet, warm environment** (bed, blanket, heat source if needed).
  - They should **rest**, but may go out briefly **to toilet**.

- **Water and food**
  - **Water**: offer when the animal is **fully awake**, usually **4–5 hours** after surgery.
  - **Food**: introduce **soft food** (pâtés, jellies, a little ham, or a small amount of kibble) **6–8 hours** after surgery.

- **Wound care**
  - Stitches are **internal and absorbable**; they do **not** need removal.
  - Some **licking** is normal; owners should **discourage excessive licking**.
  - If licking is **compulsive**, use:
    - A **recovery suit** for cats, or
    - An **Elizabethan collar** (cone) for dogs.
  - **Do not apply products on the wound**.
  - If disinfection is needed, use **chlorhexidine-impregnated gauze only**; other products may damage the wound.
  - In some females, the scar may **bulge slightly** a few days after surgery; this can be **normal**.
  - In males, some **scrotal swelling and bruising** in the days after surgery can be **normal**.

- **Residual fertility (males)**
  - In both dogs and cats, **males can remain fertile for about a month after surgery**.
  - If they live with an unsterilised female, they **may still impregnate her** during this period.

### Medication

- **Dogs**
  - Give any **capsule or liquid** as indicated, e.g. around **6 hours after surgery**.
  - Give **anti-inflammatory tablets** **24 hours after surgery**, at the **prescribed dose and duration**.

- **Cats**
  - Give **syrup or tablet** **24 hours after surgery**, **only if the animal allows it**.

- **Special circumstances**
  - If the animal has **special conditions** requiring additional medication, the clinic will inform the owner.
  - Extra medication costs are **charged separately**.

### Normal vs concerning signs

- **Do not worry (generally normal)**
  - The animal **vomits** on the day of the operation.
  - The animal is **drowsy and uninterested in play** on the day of surgery (some cats wake more slowly).
  - The animal **does not want to eat or drink in the first 24 hours**; owners should offer appetising food but not force it.

- **Contact the clinic (warning signs)**
  - **Active bleeding** (more than just a few drops).
  - **Pale gums** and **no response to stimuli 8 hours after surgery**.
  - The animal **does not eat or drink within 48 hours**.
  - The **wound opens or oozes**.

- **How to contact**
  - Owners should contact the clinic **by phone and WhatsApp**, using the **same number used to book**, during **opening hours**.

## How to Use This Skill in Practice

When the user asks for anything related to sterilisation preparations, day-of instructions, or aftercare for this clinic:

1. **Check the question scope**
   - If it is about **scheduling, quotas, or capacity**, combine this skill with the clinic’s **booking-quota rules**.
   - If it is about **clinical preparation, owner guidance, or expectations**, rely primarily on this skill.

2. **Synthesize, don’t copy-paste**
   - Provide **clear summaries, bullet lists, and checklists** tailored to the user’s context (e.g. chatbot script vs. printable handout).
   - You may paraphrase, but **must not contradict** the clinical content above.

3. **Clarify the clinic’s limitations**
   - Remind users that:
     - The clinic is **preventive** (sterilisation, vaccination, microchip).
     - It does **not** handle routine or emergency illness.
   - For non-sterilisation illnesses or emergencies, instruct users to **contact another veterinary practice**.

4. **Support Event Storming / SDD**
   - When modelling flows:
     - Capture key events: booking, pre-op checks, lab referral, fasting, arrival, surgery, recovery, complications, follow-up.
     - Use the content above as **business rules** and **domain language** for the process steps.

5. **Tone and reassurance**
   - Maintain a **reassuring, informative tone**.
   - Acknowledge that anaesthesia has risks but emphasise **routine nature in healthy animals** and the **purpose of recommended precautions**.

