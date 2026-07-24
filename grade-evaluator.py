import csv
import sys
import os

def load_csv_data():
    """
    Prompts the user for a filename, checks if it exists,
    and extracts all fields into a list of dictionaries.
    Skips (and reports) any row that is missing required fields
    or contains data that cannot be converted to a number.
    """
    filename = input("Enter the name of the CSV file to process (e.g., grades.csv): ")

    if not os.path.exists(filename):
        print(f"Error: The file '{filename}' was not found.")
        sys.exit(1)

    assignments = []
    skipped_rows = 0

    try:
        with open(filename, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            # An empty file (0 bytes) has no header at all.
            if reader.fieldnames is None:
                print(f"Warning: '{filename}' is empty (no header row found).")
                return assignments

            required_fields = {'assignment', 'group', 'score', 'weight'}
            if not required_fields.issubset(set(reader.fieldnames)):
                missing = required_fields - set(reader.fieldnames)
                print(f"Error: CSV is missing required column(s): {', '.join(missing)}")
                sys.exit(1)

            for row in reader:
                try:
                    assignment_name = (row.get('assignment') or '').strip()
                    group = (row.get('group') or '').strip()
                    score_raw = row.get('score')
                    weight_raw = row.get('weight')

                    if not assignment_name or not group:
                        raise ValueError("missing assignment name or group")
                    if score_raw is None or score_raw.strip() == '':
                        raise ValueError("missing score")
                    if weight_raw is None or weight_raw.strip() == '':
                        raise ValueError("missing weight")

                    assignments.append({
                        'assignment': assignment_name,
                        'group': group,
                        'score': float(score_raw),
                        'weight': float(weight_raw)
                    })
                except (ValueError, TypeError) as row_error:
                    skipped_rows += 1
                    print(f"Warning: Skipping invalid row {dict(row)} ({row_error}).")

        if skipped_rows:
            print(f"\n{skipped_rows} row(s) were skipped due to missing or invalid data.\n")

        if not assignments:
            print("Warning: No valid assignment records were found in the file.")

        return assignments

    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        sys.exit(1)


def evaluate_grades(data):
    """
    Validates grades, calculates GPA, determines pass/fail status,
    and identifies which failed formative assignment(s), if any,
    are eligible for resubmission.
    """
    print("\n--- Processing Grades ---")

    # Guard clause: nothing to evaluate (e.g. a freshly reset, empty grades.csv)
    if not data:
        print("No assignment data available to evaluate. Please provide a populated grades.csv.")
        return

    # a) Grade Validation: every score must be between 0 and 100
    score_errors = [
        f"'{a['assignment']}' has an out-of-range score of {a['score']}"
        for a in data if not (0 <= a['score'] <= 100)
    ]
    if score_errors:
        print("Error: One or more scores are outside the valid 0-100 range:")
        for e in score_errors:
            print(f"  - {e}")
        print("Grade evaluation halted until scores are corrected.")
        return

    # b) Weight Validation: Total = 100, Summative = 40, Formative = 60
    def is_group(a, name):
        return a['group'].strip().lower() == name

    total_weight = sum(a['weight'] for a in data)
    formative_weight = sum(a['weight'] for a in data if is_group(a, 'formative'))
    summative_weight = sum(a['weight'] for a in data if is_group(a, 'summative'))
    other_weight = total_weight - formative_weight - summative_weight

    weight_errors = []
    if abs(total_weight - 100) > 0.001:
        weight_errors.append(f"Total weight is {total_weight:.2f}, expected 100.")
    if abs(formative_weight - 60) > 0.001:
        weight_errors.append(f"Formative weight is {formative_weight:.2f}, expected 60.")
    if abs(summative_weight - 40) > 0.001:
        weight_errors.append(f"Summative weight is {summative_weight:.2f}, expected 40.")
    if abs(other_weight) > 0.001:
        weight_errors.append(f"Found {other_weight:.2f} points of weight in unrecognized group(s) (expected only 'Formative' and 'Summative').")

    if weight_errors:
        print("Error: Weight validation failed:")
        for e in weight_errors:
            print(f"  - {e}")
        print("Grade evaluation halted until weights are corrected.")
        return

    # c) GPA Calculation
    total_grade = sum(a['score'] * a['weight'] / 100 for a in data)
    gpa = (total_grade / 100) * 5.0

    def category_percentage(name, category_weight):
        if category_weight == 0:
            return 0.0
        weighted_sum = sum(a['score'] * a['weight'] for a in data if is_group(a, name))
        return weighted_sum / category_weight

    formative_score = category_percentage('formative', formative_weight)
    summative_score = category_percentage('summative', summative_weight)

    print(f"\nTotal Weighted Grade: {total_grade:.2f}%")
    print(f"Formative Category Score: {formative_score:.2f}%")
    print(f"Summative Category Score: {summative_score:.2f}%")
    print(f"GPA: {gpa:.2f} / 5.0")

    # d) Pass/Fail: must be >= 50% in BOTH categories
    passed = formative_score >= 50 and summative_score >= 50
    status = "PASSED" if passed else "FAILED"
    print(f"\nFinal Status: {status}")

    # e) & f) Resubmission logic + final decision output
    if passed:
        print("No resubmission needed.")
    else:
        failed_formatives = [
            a for a in data if is_group(a, 'formative') and a['score'] < 50
        ]

        if not failed_formatives:
            print("Resubmission: Not applicable under this rule (the failure is in the "
                  "Summative category, or no formative assignment scored below 50%).")
        else:
            # Find the highest weight among failed formative assignments
            # without using max().
            highest_weight = 0
            for a in failed_formatives:
                if a['weight'] > highest_weight:
                    highest_weight = a['weight']

            resubmission_candidates = [
                a['assignment'] for a in failed_formatives if a['weight'] == highest_weight
            ]

            print("Resubmission Eligibility (highest-weight failed Formative assignment(s)):")
            for name in resubmission_candidates:
                print(f"  - {name} (weight: {highest_weight})")


if __name__ == "__main__":
    # 1. Load the data
    course_data = load_csv_data()

    # 2. Process the features
    evaluate_grades(course_data)
