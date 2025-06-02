# Route Usage

## Quizzes

### 1. `/create_quiz` inserts the specified quiz in the `quizzes` collection in the database. This is meant to be used when creating new quizzes. 

### The user must specify the following fields: `title`, which is the name of the quiz;  `description`, which is a description of the quiz's content; `creator_username`, the username of the quiz's creator (anonymous users cannot create quizzes); and finally, `is_public`, which is a boolean value that keeps track of whether the quiz can be publicly viewed by other users (including anonymous ones) or not. This is what the user sends to the provided route in JSON.

### Example message: {title: "Svelte Trivia", description: "This quiz tests users' knowledge of the best frontend framework, Svelte.", creator_username: "SamLovesSvelte", is_public: true}

### The frontend is sent back what it originally sent but with two additional fields: `_id`, a unique identifier for the quiz, and `date_created`, which is the date of the quiz's creation in an ISO 8601 format. Both of the new fields are strings. `_id` is meant to be used in future queries to refer to this specific quiz.

### Example response: {title: "Svelte Trivia", description: "This quiz tests users' knowledge of the best frontend framework, Svelte.", creator_username: "SamLovesSvelte", is_public: true, _id: "665340af98c3b42c4f95e6a3", date_created: "2025-05-26T14:30:00Z"}

### 2. `/update_quiz` updates the specified quiz. It requires all of the fields, including the additional `_id` and `date_created` fields (so you can reuse what was returned by `/create_quiz`). All fields have the potential to get updated except for `creator_username` and `date_created`, whose new values will be ignored (as they are static fields). If the update is successful, then the response's `success` field will be set to true with an additional message, in `message`; otherwise, it will be false, with the `message` giving the particular error.

### Example message: {title: "Svelte Trivia", description: "This quiz tests users' knowledge of the WORST frontend framework, Svelte.", creator_username: "SamLovesSvelte", is_public: false, _id: "665340af98c3b42c4f95e6a3", date_created: "2025-05-26T14:30:00Z"}

### Example response: {success: true, message: "Successful update"}

### 3. `/delete_quiz` only requires `_id` being specified (from the quiz to delete). It deletes the quiz, as well as all of its questions, so it can be used to easily get rid of a quiz and all of its questions from the database in one go.

### Example message: {_id: "665340af98c3b42c4f95e6a3"}

### Example response: {success: true, message: "Successful delete"}

### 4. `/get_user_quizzes` fetches all of the user's quizzes, both public and private. All that needs to be specified is `creator_username`.

### Example message: {creator_username: "SamLovesSvelte"}

### Example response: {success: true, public_quizzes: [], private_quizzes: [{title: "Svelte Trivia", description: "This quiz tests users' knowledge of the WORST frontend framework, Svelte.", creator_username: "SamLovesSvelte", is_public: false, _id: "665340af98c3b42c4f95e6a3", date_created: "2025-05-26T14:30:00Z"}]}

### 5. `/get_public_quizzes` gets all of the public quizzes in the database. Perhaps it can be tweaked in the future to return a certain amount of quizzes instead of all of them, with more being requested as the user scrolls down more.

### Example response: {success: true, public_quizzes: []}

## Questions

### 1. `/add_question` adds the specified question to a particular quiz (using `_id` from the quiz). 

### It requires the following fields: `quiz_id`, which is `_id` from the quiz to add the question onto; `question`, which is the question; `answers`, which is a list of the potential answers to the question (both right and wrong); `correct_answer`, the answer from the list that is the one to select; and `explanation`, which gives the reasoning behind selecting the correct answer. This returns what was sent with the `_id` field added on for future queries.

### Example message: {quiz_id: "665340af98c3b42c4f95e6a3", question: "What's better, React or Svelte?", answers: ["React", "Svelte"], correct_answer: "React", explanation: "React is better because it is."}

### Example response: {quiz_id: "665340af98c3b42c4f95e6a3", question: "What's better, React or Svelte?", answers: ["React", "Svelte"], correct_answer: "React", explanation: "React is better because it is.", _id: "665340af98c3b42c4f95e6a4"}

### 2. `/update_question` updates the question. All fields need to be specified, including `_id`. `quiz_id` and `_id` remain static, however, and any changes will not be reflected in the database (so don't change them). The response indicates success or failure.

### Example message: {quiz_id: "665340af98c3b42c4f95e6a3", question: "What's better, React or Svelte?", answers: ["React", "Svelte"], correct_answer: "Svelte", explanation: "React isn't better because it isn't.", _id: "665340af98c3b42c4f95e6a4"}

### Example response: {success: true, message: "Successful update"}

### 3. `/delete_question` deletes the question with `_id`.

### Example message: {_id: "665340af98c3b42c4f95e6a4"}

### Example response: {success: true, message: "Successful delete"}

### 4. `/get_questions` gets all of the questions belonging to a particular quiz. All that needs to be specified is `quiz_id` (i.e. `_id` from the quiz).

### Example message: {_id: "665340af98c3b42c4f95e6a3"}

### Example response: {success: true, questions: [{quiz_id: "665340af98c3b42c4f95e6a3", question: "What's better, React or Svelte?", answers: ["React", "Svelte"], correct_answer: "Svelte", explanation: "React isn't better because it isn't.", _id: "665340af98c3b42c4f95e6a4"}]}

## Users

### 1. `/add_user` adds a user to the database. This should only be used when a new user that hasn't logged in to the website ever before logs in for the first time. Otherwise, it shouldn't be used.

### It uses the following fields: `username`, which is the unique name of the user which isn't repeated amongst users, nor is updated ever; `email`, which is the email of the user; and finally `score_history`, a list which logs the scores of the user for all the quizzes taken in the past. The score history object can be structured like {quiz_name: "Svelte Trivia", score: 90 / 100, date_taken: "2025-05-29T14:40:00Z"}, but there is flexibility since it's not rigourously checked. `score_history` will initially be an empty list.

### Example message: {username: SamLovesSvelte, email: samlovessvelte100@gmail.com, score_history: []}

### Example response: {username: SamLovesSvelte, email: samlovessvelte100@gmail.com, score_history: [], _id: "665340af98c3b42c4f95e6a5"}

### 2. `/update_user` takes the user object with the additional `_id` field and updates. `score_history` is all that ends up changing. You can use this route to add scores or clear the entire history of the user (for example with a button).

### Example message: {username: SamLovesSvelte, email: samlovessvelte100@gmail.com, score_history: [{quiz_name: "Svelte Trivia", score: 90 / 100, date_taken: "2025-05-29T14:40:00Z"}], _id: "665340af98c3b42c4f95e6a5"}

### Example response: {success: true, message: "Successful update"}

### 3. `/delete_user` needs `_id` to delete the specified user. It shouldn't be used anyway realistically. I guess it could be changed to take `username` instead. Both would work.

### Example message: {_id: "665340af98c3b42c4f95e6a5"}

### Example response: {success: true, message: "Successful delete"}

### 4. `/get_user` gets the user with the specified username from the database. This should be used whenever someone logs in to make sure they're not already registered. The returned object should be checked to make sure the user doesn't exist before adding a new one with `/add_user`.

### Example message: {username: "SamLovesSvelte"}

### Example response: {success: true, user: {username: SamLovesSvelte, email: samlovessvelte100@gmail.com, score_history: [{quiz_name: "Svelte Trivia", score: 90 / 100, date_taken: "2025-05-29T14:40:00Z"}], _id: "665340af98c3b42c4f95e6a5"}}