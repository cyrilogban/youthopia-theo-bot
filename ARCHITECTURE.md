# Architecture 

## Current Design

Theo uses a simple layered structure:

- **Container** → handles infrastructure (settings + database)
- **Services** → business logic (scheduler, verse logic)
- **Adapters** → Telegram bot (TeleBot)
- **Main** → wiring everything together

---

## Option A vs Option B (Important Decision)

There are two ways I could structure the bot.

### Option B (Not used)
- Store Telegram bot inside the Container
- Access it with: `container.bot`

Problem:
- Container becomes tightly coupled to TeleBot
- Harder to change Telegram library later

---

### Option A (Chosen)

I removed the bot from the Container.

- `container.py` → only settings + database
- `main.py` → creates the bot
- `schedule_service.py` → receives bot as argument

Example:

```python
start_scheduler(lambda: daily_job(container, bot))

## Database Layer (MongoDB)

Theo uses MongoDB to persist group data.

### Responsibilities:
- Store registered Telegram groups
- Track whether daily verse is enabled or disabled
- Store group metadata (e.g. title)

### Implementation:
- MongoDB is accessed through `MongoGroupRepo`
- The repository follows an abstraction (`GroupRepo`) to allow flexibility

### Why MongoDB:
- Simple document-based storage
- Easy to scale
- Flexible schema for future features (preferences, settings)

---

## Data Flow

1. A group enables daily verse
2. The group is stored in MongoDB
3. Scheduler fetches enabled groups from MongoDB
4. Messages are sent to those groups

## Future Data Design
- store verse history per group
- store delivery time per group
- store preferred Bible version