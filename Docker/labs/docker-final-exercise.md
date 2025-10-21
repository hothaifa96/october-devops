# Docker Exercise: API Logger and Data Viewer

## Objective

Create a system of two Docker containers:

1. One container logs API responses into a file at random intervals.
2. Another container reads and summarizes the log based on the hour.

---

## Part 1: API Logging Script

### Task:

Write a **Python or Bash script** that performs the following:

- Runs in an **infinite loop**.
- At **random intervals**, fetches data from **any public API**.
- On each request:
  - Logs the **current date and time**, the **API URL**, and the **full response**.
- Appends this information to a **log file** (in append mode).

---

## Part 2: Dockerizing the Logger

### Task:

- Create a **Dockerfile** for the logging script.
- Build a **Docker image** from this file.
- Run a **Docker container** from this image:
  - Use a **Docker volume** to persist and share the log file with other containers.

---

## Part 3: Log Viewer Script

### Task:

Write another **Python or Bash script** that:

- Reads from the **shared log file**.
- Groups and displays the API response entries by **hour**.
- For example, if two entries are logged at `12:01:05` and `12:04:05`, the viewer shows them both under `12:00`.

---

## Part 4: Dockerizing the Viewer

### Task:

- Create a **second Dockerfile** for the viewer script.
- Build a **Docker image**.
- Run a **second Docker container** from this image:
  - Mount the **same volume** to access the log file.
  - On execution, it should display the grouped data based on the hour.

---

##  Notes

- You may use **any public API**, such as:
  - `https://api.chucknorris.io/jokes/random`
  - `https://catfact.ninja/fact`
  - Or any other of your choice.
- Each log entry must include:
  - **Timestamp**
  - **API URL**
  - **Response**
- The viewer container does **not** need to run continuously — it can be executed on demand.