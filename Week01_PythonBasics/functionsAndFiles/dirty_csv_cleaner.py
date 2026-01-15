import csv
from pathlib import Path


def clean_csv(input_file, output_file, log_file):

    with open(input_file, newline="") as f:
        reader = csv.reader(f)
        cleaned_rows = []
        seen = set()

        header = next(reader)
        cleaned_header = [h.strip() for h in header]
        cleaned_rows.append(cleaned_header)

        for line_number, line in enumerate(reader, start=2):
            cleaned_row = [field.strip() for field in line]

            # validates that every row has corrrect quantity of elements
            if len(cleaned_row) < 4:
                with open(log_file, "a") as log:
                    log.write(
                        f"Row {line_number} dropped: missing fields {cleaned_row}\n"
                    )
                continue

            if len(cleaned_row) > 4:
                with open(log_file, "a") as log:
                    log.write(
                        f"Row {line_number} dropped: too many fields {cleaned_row}\n"
                    )
                continue

            age_str = cleaned_row[1]
            salary_str = cleaned_row[3]

            # checks if age field or salary field are empty
            if not age_str or not salary_str:
                with open(log_file, "a") as log:
                    message = "empty age field" if not age_str else "empty salary field"
                    log.write(f"Row {line_number} {message}\n")
                continue

            # validates that age is a digit
            if not age_str.isdigit():
                with open(log_file, "a") as log:
                    log.write(f"Row {line_number} dropped: non numeric age {age_str}\n")
                continue

            # validates that age is within logical range
            if int(age_str) < 0 or int(age_str) > 120:
                with open(log_file, "a") as log:
                    log.write(
                        f"Row {line_number} dropped: age outside of logical range {age_str}\n"
                    )
                continue

            # validates that salary is a digit
            if not salary_str.isdigit():
                with open(log_file, "a") as log:
                    log.write(
                        f"Row {line_number} dropped: non numeric salary {salary_str}\n"
                    )
                continue

            if int(salary_str) > 10_000_000 or int(salary_str) == 0:
                with open(log_file, "a") as log:
                    log.write(
                        f"Row {line_number} dropped: unrealistic salary {salary_str}\n"
                    )
                continue

            # check for duplicates
            row_tuple = tuple(cleaned_row)
            if row_tuple in seen:
                with open(log_file, "a") as log:
                    log.write(
                        f"Row {line_number} dropped: duplicate row {cleaned_row}\n"
                    )
                continue

            seen.add(row_tuple)

            cleaned_rows.append(cleaned_row)

        # writes the cleaned list to the csv file
        with open(output_file, "w", newline="") as out:
            writer = csv.writer(out)
            writer.writerows(cleaned_rows)

    pass
