# Wedding App API Documentation

## Overview
The Wedding App backend provides APIs for managing a wedding participant registry, photo uploads, and a quiz system. Admins can manage participant details, toggle features, and monitor quiz submissions, while users can register, upload photos, and participate in quizzes.

---

## Authentication
- **Method**: OAuth2 with Password (Bearer Token)
- **Token URL**: `/admin/login`
- **Headers**:
  - `Authorization: Bearer <token>`

### Admin Credentials
Admin authentication is required for specific endpoints. The credentials are stored in environment variables:
- `ADMIN_USERNAME`
- `ADMIN_PASSWORD`

---

## Endpoints

### 1. **Admin Login**
**POST** `/admin/login`
- **Description**: Authenticate as an admin and receive a token.
- **Request**:
  - **Form Data**:
    - `username` (str): Admin username
    - `password` (str): Admin password
- **Response**:
```json
{
  "access_token": "<token>",
  "token_type": "bearer"
}
```

### 2. **Toggle Photos**
**POST** `/admin/toggle_photos`
- **Description**: Enable or disable photo uploads.
- **Request**:
  - **Body**:
    - `status` (bool): `true` to enable, `false` to disable.
- **Response**:
```json
{
  "allow_photos": true
}
```

### 3. **Toggle Quiz**
**POST** `/admin/toggle_quiz`
- **Description**: Enable or disable quizzes.
- **Request**:
  - **Body**:
    - `status` (bool): `true` to enable, `false` to disable.
- **Response**:
```json
{
  "allow_quiz": true
}
```

### 4. **Register Participant**
**POST** `/participation`
- **Description**: Register a new participant.
- **Request**:
  - **Body**:
    - `first_name` (str): First name
    - `last_name` (str): Last name
    - `attending` (bool): Attendance status
- **Response**:
```json
{
  "id": 1,
  "first_name": "John",
  "last_name": "Doe",
  "attending": true
}
```

### 5. **Update Participant**
**PUT** `/participant/{participant_id}`
- **Description**: Update participant details.
- **Request**:
  - **Path Parameter**: `participant_id` (int): ID of the participant.
  - **Body**:
    - `first_name` (str): Updated first name
    - `last_name` (str): Updated last name
    - `attending` (bool): Updated attendance status
- **Response**:
```json
{
  "id": 1,
  "first_name": "John",
  "last_name": "Smith",
  "attending": false
}
```

### 6. **Delete Participant**
**DELETE** `/participant/{participant_id}`
- **Description**: Delete a participant by ID.
- **Request**:
  - **Path Parameter**: `participant_id` (int): ID of the participant.
- **Response**:
```json
{
  "message": "Participant deleted successfully"
}
```

### 7. **Get Participants**
**GET** `/participants`
- **Description**: Fetch all registered participants.
- **Response**:
```json
[
  {
    "id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "attending": true
  }
]
```

### 8. **Upload Photo**
**POST** `/upload_photo`
- **Description**: Upload a photo for a participant.
- **Request**:
  - **Form Data**:
    - `first_name` (str): Participant's first name
    - `last_name` (str): Participant's last name
    - `phone_number` (str): Participant's phone number
    - `file` (UploadFile): Photo file
- **Response**:
```json
{
  "message": "Photo uploaded successfully for John Doe.",
  "filename": "photo.jpg"
}
```

### 9. **Delete Photo**
**DELETE** `/upload_photo/{photo_id}`
- **Description**: Delete an uploaded photo by ID.
- **Request**:
  - **Path Parameter**: `photo_id` (int): ID of the photo.
- **Response**:
```json
{
  "message": "Photo deleted successfully"
}
```

### 10. **Get Photos**
**GET** `/photos`
- **Description**: Fetch all uploaded photos. Requires admin to enable photos.
- **Response**:
```json
[
  {
    "id": 1,
    "filename": "photo.jpg",
    "uploaded_by": "John Doe"
  }
]
```

### 11. **Add Quiz**
**POST** `/admin/quiz`
- **Description**: Add a quiz question.
- **Request**:
  - **Body**:
    - `question` (str): Quiz question
    - `options` (List[str]): List of options
    - `correct_option` (int): Index of the correct option
- **Response**:
```json
{
  "id": 1,
  "question": "What is the capital of France?",
  "options": ["Paris", "London", "Berlin"],
  "correct_option": 0
}
```

### 12. **Update Quiz**
**PUT** `/quiz/{quiz_id}`
- **Description**: Update quiz details.
- **Request**:
  - **Path Parameter**: `quiz_id` (int): ID of the quiz.
  - **Body**:
    - `question` (str): Updated quiz question
    - `options` (List[str]): Updated list of options
    - `correct_option` (int): Updated index of the correct option
- **Response**:
```json
{
  "id": 1,
  "question": "What is the capital of Germany?",
  "options": ["Paris", "London", "Berlin"],
  "correct_option": 2
}
```

### 13. **Delete Quiz**
**DELETE** `/admin/quiz/{quiz_id}`
- **Description**: Delete a quiz question by ID.
- **Request**:
  - **Path Parameter**: `quiz_id` (int): ID of the quiz.
- **Response**:
```json
{
  "message": "Quiz deleted successfully"
}
```

### 14. **Get Quiz**
**GET** `/quiz`
- **Description**: Fetch all quiz questions. Requires admin to enable quizzes.
- **Response**:
```json
[
  {
    "id": 1,
    "question": "What is the capital of France?",
    "options": ["Paris", "London", "Berlin"],
    "correct_option": 0
  }
]
```

### 15. **Submit Quiz**
**POST** `/quiz/submit`
- **Description**: Submit quiz answers and calculate total marks.
- **Request**:
  - **Body**:
    - `participant_id` (int): ID of the participant
    - `answers` (List[int]): List of selected options by the participant
- **Response**:
```json
{
  "participant_id": 1,
  "score": 5
}
```

### 16. **Get Quiz Participants**
**GET** `/quiz_participants`
- **Description**: Fetch all quiz participants and their results. Requires admin authorization.
- **Response**:
```json
[
  {
    "id": 1,
    "name": "John Doe",
    "score": 5
  }
]
```

