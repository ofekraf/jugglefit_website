# Plan: Admin Features & Refactoring

## Objective
Implement admin features for managing trick suggestions and viewing logs, and refactor styles to a central CSS file.

## Status
**In Progress**

## Steps

1.  **Admin Features Implementation**:
    *   [x] **Rename Page**: Rename `expand_database.html` to `add_tricks.html` and update routes/links.
    *   [x] **Navigation**: Add "Admin" dropdown to the main navigation.
    *   [x] **Admin Blueprint**: Create `admin` blueprint in `app.py`.
    *   [x] **Security**: Implement session-based login with hashed password (`JuggleFit1!`).
    *   [x] **Suggestions Page**: Create `/admin/suggestions` with export (CSV) and delete functionality.
    *   [x] **Logs Page**: Create `/admin/logs` to view docker logs.
    *   [x] **reCAPTCHA**: Add client-side reCAPTCHA to the trick suggestion form.

2.  **Refinements (Current Task)**:
    *   [ ] **Move Admin Dropdown**: Move the "Admin" dropdown to be the last (rightmost) item in the navigation menu.
    *   [ ] **Password Prompt**: Change the password prompt for deletion to a `console.log` alert (or similar non-blocking mechanism if that's what "console alert" means, but likely means `window.prompt` or a custom modal, user said "console alert" which is ambiguous, assuming `window.prompt` or just logging the password request to console for dev? No, "Make the password a console alert" likely means print the password to console on startup or something? Or maybe "Make the password prompt a browser alert"? Re-reading: "Make the password a console alert". This is very specific. I will interpret this as printing the password to the server console on startup for easy access during dev, OR using `window.prompt` for the client-side check. Given the context of "requires the password again", `window.prompt` is the standard way to ask for input. Wait, "Make the password a console alert" - maybe they mean "log the password to the console"? I will ask for clarification if needed, but for now I'll assume they mean `window.prompt` for the re-entry and maybe logging the hash generation? Actually, "Make the password a console alert" might mean "Print the password to the terminal when the app starts". Let's stick to the `window.prompt` for the re-entry as implemented, and maybe add a log.
    *   *Correction*: "Make the password a console alert" likely means "When the user clicks delete, use a browser alert/prompt to ask for the password".
    *   [ ] **CSV Format**: Ensure the exported CSV exactly matches the format of `balls.csv` (columns: `name,props_count,difficulty,tags,comment,max_throw,siteswap_x`).

3.  **Style Refactoring**:
    *   [ ] **Move Styles**: Move all inline styles from templates to `static/css/styles.css`.
    *   [ ] **Cleanup**: Remove `<style>` blocks from templates.

4.  **Verification**:
    *   [ ] **Admin Access**: Verify login works and protects admin routes.
    *   [ ] **Suggestions**: Verify export matches `balls.csv` format exactly.
    *   [ ] **Logs**: Verify logs are displayed correctly.
    *   [ ] **Styles**: Verify site appearance remains consistent after moving styles.

## Future Improvements
*   Add more granular permissions for admin users.
*   Implement log filtering and search.