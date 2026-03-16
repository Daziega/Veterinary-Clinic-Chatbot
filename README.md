## Veterinary Clinic Chatbot

The **Veterinary Clinic Chatbot** is designed to help pet owners easily **book, manage, and cancel appointments** with a veterinary clinic through a natural, conversational interface. It guides users through providing all the details the clinic needs, while keeping the experience simple and friendly.

- **Repository URL**: `https://github.com/Daziega/Veterinary-Clinic-Chatbot`

### Key features

- **Appointment booking**: Guides pet owners through scheduling new appointments for services such as check-ups, vaccinations, and follow-up visits.
- **Appointment management**: Supports rescheduling or cancelling existing appointments (depending on the underlying integration).
- **Structured data collection**: Captures key information (pet details, reason for visit, urgency, preferred date/time, preferred veterinarian) in a consistent format for clinic staff.
- **Clinic-friendly summaries**: Produces clear summaries that can be forwarded to clinic systems or staff for confirmation.

### Appointment flow

At a high level, a typical appointment conversation follows these steps:

1. **Conversation start**
   - The pet owner greets the chatbot or selects an option like “Book an appointment.”
2. **Gathering appointment details**
   - The chatbot asks for:
     - Pet name and basic details (species, breed, age if needed).
     - Reason for the visit (e.g., routine check-up, vaccination, illness).
     - Preferred date and time window.
     - Preferred veterinarian (if applicable) and any urgency information.
3. **Checking availability**
   - Based on the requested time (and any integration you add to this project), the chatbot determines potential appointment slots.
   - It may suggest the closest available options if the preferred slot is not free.
4. **Confirming the appointment**
   - The chatbot confirms the chosen date, time, and veterinarian with the user.
   - It then summarizes all details and, once integrated, can send them to the clinic’s appointment system or staff.
5. **Rescheduling or cancelling**
   - For an existing appointment, the chatbot can:
     - Look up the appointment using identifiers you choose to support (e.g., phone number, booking reference).
     - Offer new time slots for rescheduling.
     - Confirm cancellations and summarize the updated status.

### Example appointment conversation

**User**: Hi, I’d like to book an appointment for my dog.  
**Chatbot**: Sure! What is your dog’s name?  
**User**: Her name is Bella.  
**Chatbot**: Great. What is the reason for Bella’s visit?  
**User**: She needs her annual vaccinations.  
**Chatbot**: Got it. When would you prefer to come in?  
**User**: Next Tuesday afternoon.  
**Chatbot**: I can offer Tuesday at 2:30 PM or 4:00 PM. Which works better?  
**User**: 4:00 PM.  
**Chatbot**: Perfect. Do you have a preferred veterinarian, or should I assign the first available?  
**User**: First available is fine.  
**Chatbot**: All set! I’ve booked Bella for vaccinations on Tuesday at 4:00 PM with the first available veterinarian. You’ll receive a confirmation shortly.

### Cursor rules for this repository

This project uses Cursor's repository-level configuration stored in `.cursor/rules/repository.mdc`.

The current contents of `repository.mdc` are:

```markdown
---
alwaysApply: true
---
My repository url is https://github.com/Daziega/Veterinary-Clinic-Chatbot
```

- **`alwaysApply: true`**: Tells Cursor that this rule file should always be applied for this repository.
- **Repository URL note**: Documents the canonical GitHub URL for this repo, which tools and agents can use when they need to reference the project remotely.

### How to update the repository rules

- Edit `.cursor/rules/repository.mdc` if you need to:
  - Add more repository-wide metadata or conventions.
  - Capture coding standards or project-specific guidelines.
  - Document additional links (e.g., issues, wiki, CI dashboards).
- Keep the frontmatter (`---` block) valid YAML so Cursor can parse it correctly.

### Getting started

1. Clone the repository:

```bash
git clone https://github.com/Daziega/Veterinary-Clinic-Chatbot.git
cd Veterinary-Clinic-Chatbot
```

2. Open the project in Cursor to take advantage of the repository rules in `.cursor/rules/repository.mdc`.

