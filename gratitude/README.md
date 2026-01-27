What does the system do step-by-step?
1️⃣ Message Ingestion

People send gratitude messages like:

“A staff member in a red shirt near the food court helped my mother calmly.”

The system:

Stores the raw message

Keeps metadata (source, language, timestamp)

2️⃣ Understanding the Message (AI Extraction)

Each message is read by an AI model that extracts:

Who the gratitude is for (person / place / team)

What action happened (helped, guided, assisted)

Descriptions (calm, polite, red shirt)

Location (food court, mall area)

Sentiment (how positive it is)

The result is a structured story, not just text.

3️⃣ Turning Stories into Meaning (Embeddings)

Every story is converted into a numerical representation (an embedding).

This allows the system to:

Compare stories

Measure similarity

Group related stories automatically

No manual tagging needed.

4️⃣ Automatic Clustering (Grouping Similar Stories)

Stories that talk about the same situation or person are:

Grouped into clusters

Even if the wording is different

Example:

“food court”

“mall food area”

“near the food court”

➡️ All get grouped together.

5️⃣ Entity Creation (Who is this gratitude about?)

From each cluster, the system creates a Gratitude Entity:

A person

A place

Or a team

Each entity has:

A canonical profile (best summary)

Common descriptors

A confidence score

Count of stories supporting it

6️⃣ Human Review & Safety Checks

The system detects situations like:

Two entities that might be the same → merge candidate

One entity that might actually be multiple → split candidate

A human can:

Confirm

Merge

Split

Reject suggestions

This ensures high trust and no wrong conclusions.

7️⃣ Powerful Search

You can search gratitude by:

Location (food)

Action (helped)

Role (staff)

Entity type (person)

Results include:

The entity

All related stories

Sentiment and context

8️⃣ Analytics & Insights

The system can answer questions like:

Who receives the most gratitude?

Where do positive experiences happen most?

What actions are most appreciated?

Overall sentiment trends

All powered directly from real gratitude data.

What has been built so far?

✅ Message ingestion API
✅ AI-based information extraction
✅ Embeddings & similarity engine
✅ Automatic clustering
✅ Entity resolution system
✅ Human review workflow
✅ Search APIs
✅ Analytics APIs
✅ End-to-end tested with real data