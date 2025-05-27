# Route Usage

## Quizzes

### 1. `"/create_quiz"` inserts the specified quiz in the `quizzes` collection in the database (for the first time). 

### The user must specify the following fields: `title`, which is the name of the quiz;  `description`, which is a description of the quiz's content; `creator_username`, the username of the quiz's creator (anonymous users cannot create quizzes); and finally, `is_public`, which is a boolean value that keeps track of whether the quiz can be publicly viewed by other users (including anonymous ones) or not. This is what the user sends to the provided route in JSON.

### Example: {title: "Svelte Trivia", description: "This quiz tests users' knowledge of the best frontend framework, Svelte.", creator_username: "SamLovesSvelte", is_public: true}

### The frontend is sent back what was sent but with two additional fields: `_id`, a unique identifier for the quiz, and `date_created`, which is the date of the quiz's creation in an ISO 8601 format. Both of the new fields are strings.

### Example: {title: "Svelte Trivia", description: "This quiz tests users' knowledge of the best frontend framework, Svelte.", creator_username: "SamLovesSvelte", is_public: true, _id: "665340af98c3b42c4f95e6a3", date_created: "2025-05-26T14:30:00Z"}

### 2. `"update_quiz"`

### 3. `"delete_quiz"`

### 4. `"get_user_quizzes"`

### 5. `"get_public_quizzes"`