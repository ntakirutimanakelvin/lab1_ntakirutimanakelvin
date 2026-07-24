# Lab 1: Grade Evaluator & Archiver

Calculates a student's final academic standing from `grades.csv`, then archives
and resets that CSV using a companion Bash script.

## Files

- `grade-evaluator.py` — reads `grades.csv`, validates it, calculates the GPA,
  and determines Pass/Fail status and resubmission eligibility.
- `organizer.sh` — archives the current `grades.csv` with a timestamp, resets
  the workspace with a fresh empty `grades.csv`, and logs the action.
- `grades.csv` — sample grade data.

## Requirements

- Python 3
- Bash (Linux/macOS or WSL/Git Bash on Windows)

## Running `grade-evaluator.py`

```bash
python3 grade-evaluator.py
```

You'll be prompted for a filename:

```
Enter the name of the CSV file to process (e.g., grades.csv): grades.csv
```

The script will:

1. Validate that every score is between 0–100.
2. Validate that weights total 100, with exactly 60 in the `Formative`
   group and 40 in the `Summative` group.
3. Calculate the total weighted grade and GPA (`GPA = (Total Grade / 100) * 5.0`).
4. Print PASSED or FAILED (requires ≥ 50% in **both** the Formative and
   Summative categories).
5. If FAILED, list the failed Formative assignment(s) with the highest
   weight as eligible for resubmission (ties are all listed).

Rows with missing or invalid data are skipped with a warning rather than
crashing the program; a missing file or an empty CSV is also handled
gracefully.

### `grades.csv` format

```csv
assignment,group,score,weight
Quiz,Formative,85,20
Midterm Project,Summative,70,20
```

## Running `organizer.sh`

```bash
chmod +x organizer.sh   # first time only
./organizer.sh
```

Each run:

1. Creates an `archive/` directory if it doesn't already exist.
2. Renames the current `grades.csv` to `grades_<YYYYMMDD-HHMMSS>.csv` and
   moves it into `archive/`.
3. Creates a fresh, empty `grades.csv` in the current directory.
4. Appends a line to `organizer.log` recording the timestamp, the original
   filename, and the new archived filename (log entries accumulate across
   runs).

Run it whenever you want to snapshot the current grade sheet before
loading in a new batch of grades.
