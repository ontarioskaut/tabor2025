# API documentation

## RFID nodes related API (`/api/nodes`):

- **Get basic user info from tag UID (`get_identification` [GET]):**
  - **Input:** `user_tag_id=string`
  - **Output:** 
    ```json
    {
      "name": string,
      "user_time": int
    }
    ```
  - **Errors:**
    ```json
    { "error": "user_tag_id is required" }
    { "error": "User not found" }
    ```

---

- **Subtract time from user (`subtract_time` [GET]):**
  - **Input:** 
    - `time_to_subtract=int`
    - `user_tag_id=string`
  - **Output:** 
    ```json
    { "status": "success", "user_time": int }
    ```
  - **Errors:**
    ```json
    { "error": "time_to_substract and user_tag_id are required" }
    { "error": "time must be an integer" }
    { "error": "User not found" }
    ```

---

- **Add time to user (`add_time` [GET]):**
  - **Input:** 
    - `time_to_add=int`
    - `user_tag_id=string`
  - **Output:** 
    ```json
    { "status": "success", "user_time": int }
    ```
  - **Errors:**
    ```json
    { "error": "time_to_add and user_tag_id are required" }
    { "error": "time must be an integer" }
    { "error": "User not found" }
    ```

---

- **Change time (add, subtract, multiply, percent) (`change_time` [GET]):**
  - **Input:** 
    - `input_time=string` (e.g. `30+`, `20-`, `50%`)
    - `user_tag_id=string`
  - **Output:**
    ```json
    { "status": "success", "user_time": int }
    ```
  - **Errors:**
    ```json
    { "error": "input_time and user_tag_id are required" }
    { "error": "time must be integer" }
    { "error": "User not found" }
    ```

---

- **Add coin value to user time (`add_coinval` [GET]):**
  - **Input:**
    - `coin_tag_id=string`
    - `user_tag_id=string`
  - **Output:**
    ```json
    { "status": "success", "user_time": int }
    ```
  - **Errors:**
    ```json
    { "error": "coin_tag_id and user_tag_id are required" }
    { "error": "coin is inactive" }
    { "error": "User or tag found" }
    ```

---

- **Set coin value and category (`set_coinval` [GET]):**
  - **Input:**
    - `coin_tag_id=string`
    - `coin_value=int`
    - `category=int`
  - **Output:**
    ```json
    { "status": "success" }
    ```
  - **Errors:**
    ```json
    { "error": "coin_tag_id and coin_value and category are required" }
    { "error": "coin_value and category must be integers" }
    ```

---

- **Activate coin (`activate_coin` [GET]):**
  - **Input:**
    - `coin_tag_id=string`
  - **Output:**
    ```json
    { "status": "success" }
    ```
  - **Errors:**
    ```json
    { "error": "coin tag is required" }
    ```

---

- **Initialize user by tag UID (`init_user_tag` [GET]):**
  - **Input:**
    - `user_tag_id=string`
  - **Output:**
    ```json
    { "status": "success" }
    ```
    or
    ```json
    { "status": "error", "text": "user already exist" }
    ```
  - **Errors:**
    ```json
    { "error": "no user_tag_id" }
    ```

## Admin API (`/api/admin`):

### **User management**

- **Set user field (`set_user_field` [GET]):**
  - **Input (query params):**
    - `user_id` (int)
    - `field_name` (string) — name of the column to update
    - `new_value` (string) — new value to set
  - **Output:**
    ```json
    { "status": "success" }
    ```
  - **Errors:**
    ```json
    { "error": "wrong arguments input should be user_id, filed_name, new_value" }
    { "status": "error", "message": "No user found with the given user_id" }
    ```

---

- **Update user (`update_user` [POST]):**
  - **Input (form fields):**
    - `user_id` (int)
    - `user_tag_id` (string)
    - `user_name` (string)
    - `user_acro` (string)
    - `user_time_offset` (int)
    - `user_game_start_timestamp` (datetime string)
    - `is_displayed` (optional, "on" or absent)
  - **Output:**
    ```json
    { "status": "success" }
    ```
  - **Errors:**
    ```json
    { "error": "All fields are required." }
    { "error": "user tag is already in use, by user: ID, NAME" }
    { "error": "offset must me integers" }
    ```

---

- **Add user (`add_user` [POST]):**
  - **Input (form fields):**
    - `user_tag_id`, `user_name`, `user_acro`, `user_time_offset`, `user_game_start_timestamp`, `is_displayed`
  - **Output:**
    ```json
    { "status": "succes" }
    ```
  - **Errors:**
    ```json
    { "error": "All fields are required." }
    { "error": "user tag is already in use, by user: ID, NAME" }
    { "error": "offset must me integers" }
    ```

---

- **Delete user (`delete_user` [POST]):**
  - **Input (form fields):**
    - `user_id`
  - **Output:**
    ```json
    { "status": "success" }
    ```
  - **Errors:**
    ```json
    { "error": "user_id is required" }
    ```

---

- **Bulk add user time (`bulk_add_user_time` [POST]):**
  - **Input (JSON):**
    - `user_ids`: array of user IDs
    - `time_offset`: string or int (e.g., `30+`, `50-`, `20`)
  - **Output:**
    ```json
    { "status": "success" }
    ```
  - **Errors:**
    ```json
    { "error": "user_ids and time_offset are required" }
    { "error": "time_offset must be an integer" }
    ```

---

### **Coin management**

- **Update coin (`update_coin` [POST]):**
  - **Input (form fields):**
    - `coin_id`, `coin_tag_id`, `coin_value`, `coin_category`, `last_used`, `is_active`
  - **Output:**
    ```json
    { "status": "success" }
    ```
  - **Errors:**
    ```json
    { "error": "All fields are required." }
    { "error": "coin tag is already in use, by : ID" }
    ```

---

- **Add coin (`add_coin` [POST]):**
  - **Input (form fields):**
    - `coin_tag_id`, `coin_value`, `coin_category`, `last_used`, `is_active`
  - **Output:**
    ```json
    { "status": "succes" }
    ```
  - **Errors:**
    ```json
    { "error": "All fields are required." }
    { "error": "coin tag is already in use, by: ID" }
    ```

---

- **Delete coin (`delete_coin` [POST]):**
  - **Input (form fields):**
    - `coin_id`
  - **Output:**
    ```json
    { "status": "success" }
    ```

---

- **Bulk set coin field (`bulk_set_coin_field` [POST]):**
  - **Input (JSON):**
    - `coin_ids`: array of coin IDs
    - `field_name`: string
    - `new_value`: string
  - **Output:**
    ```json
    { "status": "success" }
    ```

---

- **Bulk add coin time (`bulk_add_coin_time` [POST]):**
  - **Input (JSON):**
    - `coin_ids`: array of coin IDs
    - `time_offset`: integer
  - **Output:**
    ```json
    { "status": "success" }
    ```

---

### **User category management**

- **Update user category (`update_user_category` [POST]):**
  - **Input (form fields):**
    - `category_id`, `category_name`
  - **Output:**
    ```json
    { "status": "success" }
    ```

- **Add user category (`add_user_category` [POST]):**
  - **Input (form fields):**
    - `category_name`
  - **Output:**
    ```json
    { "status": "succes" }
    ```

- **Delete user category (`delete_user_category` [POST]):**
  - **Input (form fields):**
    - `category_id`
  - **Output:**
    ```json
    { "status": "success" }
    ```

- **Bulk add user time by category (`bulk_add_user_time_category` [POST]):**
  - **Input (JSON):**
    - `ids`: array of category IDs
    - `time_offset`: string or int (e.g., `30+`, `50-`)
  - **Output:**
    ```json
    { "status": "success" }
    ```

---

### **User-category relation management**

- **Add relation (`add_user_cat_rel` [POST]):**
  - **Input (form fields):**
    - `user_id`, `category_id`
  - **Output:**
    ```json
    { "status": "success" }
    ```

- **Update relation (`update_user_cat_rel` [POST]):**
  - **Input (form fields):**
    - `row_id`, `user_id`, `category_id`
  - **Output:**
    ```json
    { "status": "success" }
    ```

- **Delete relation (`delete_user_cat_rel` [POST]):**
  - **Input (form fields):**
    - `row_id`
  - **Output:**
    ```json
    { "status": "success" }
    ```

- **Toggle relation (`toggle_user_cat_rel` [POST]):**
  - **Input (form fields):**
    - `user_id`, `category_id`, `is_checked` ("on"/absent)
  - **Output:**
    ```json
    { "message": "Operation successful!" }
    ```

---

### **Coin category management**

- **Update coin category (`update_coin_category` [POST]):**
  - **Input (form fields):**
    - `category_id`, `category_name`
  - **Output:**
    ```json
    { "status": "success" }
    ```

- **Add coin category (`add_coin_category` [POST]):**
  - **Input (form fields):**
    - `category_name`
  - **Output:**
    ```json
    { "status": "succes" }
    ```

- **Delete coin category (`delete_coin_category` [POST]):**
  - **Input (form fields):**
    - `category_id`
  - **Output:**
    ```json
    { "status": "success" }
    ```

- **Bulk add coin time by category (`bulk_add_coin_time_category` [POST]):**
  - **Input (JSON):**
    - `ids`: array of category IDs
    - `time_offset`: string or int
  - **Output:**
    ```json
    { "status": "success" }
    ```

---

## Display API (`/api/display`):

### **Get simplified time overview (`get_time_simple` [GET]):**
- **Description:**  
  Returns a dictionary of acronyms and their remaining times for users marked as displayed.
- **Endpoint:** `/api/display/get_time_simple`
- **Input:** *(no parameters)*
- **Output:**
```json
{
  "ABC": 120,
  "XYZ": 45
}
```
- **Notes:**
  - Keys are user acronyms.
  - Values are integer remaining times in seconds.

---

### **Get time overview (`get_time` [GET]):**
- **Description:**  
  Returns the same data as `get_time_simple`; kept for future enhancements.
- **Endpoint:** `/api/display/get_time`
- **Input:** *(no parameters)*
- **Output:**
```json
{
  "ABC": 120,
  "XYZ": 45
}
```
- **Notes:**  
  - Identical behavior to `get_time_simple`.

---

### **Show times (`show_times` [GET]):**
- **Description:**  
  Returns a list of users with their name, offset, and start timestamp (ISO format).
- **Endpoint:** `/api/display/show_times`
- **Input:** *(no parameters)*
- **Output:**
```json
[
  {
    "name": "John Doe",
    "offset": 300,
    "start": "2025-08-02T12:30:00"
  },
  {
    "name": "Jane",
    "offset": 120,
    "start": "2025-08-02T12:40:00"
  }
]
```
- **Notes:**
  - Only users with `is_displayed = 1` are returned.
  - Offset and start are raw database values; `offset` is in seconds.

---

## Misc API (`/api/misc`):

### **Get logs (`get_logs` [GET]):**
- **Description:**  
  Returns all log entries stored in the `logs` table.
- **Endpoint:** `/api/misc/get_logs`
- **Input:** *(no parameters)*
- **Output (raw JSON array of rows):**
```json
[
  [1, "2025-08-02 12:30:00", 3, 120, "updated offset"],
  [2, "2025-08-02 12:45:00", 5, -30, "manual adjustment"]
]
```
- **Notes:**
  - Each log entry is returned as an array in the following order:  
    `[id, timestamp, user_id, amount, details]`
  - No filtering or formatting is applied in this endpoint.

