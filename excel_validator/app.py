from flask import Flask, request, render_template
import pandas as pd
import pymysql

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    data = pd.read_excel(file)

    errors = []
    valid_rows = []
    ids = []

    for index, row in data.iterrows():
        error = ""


        for column in [
            "Employee ID", "Full Name", "Job Title",
            "Salary (USD)", "Email", "Company"
        ]:
            if pd.isna(row[column]) or str(row[column]).strip() == "":
                error += column + " is missing. "


        salary = pd.to_numeric(row["Salary (USD)"], errors="coerce")

        if pd.isna(salary) or salary < 0:
            error += "Invalid Salary. "


        employee_id = str(row["Employee ID"]).strip()

        if employee_id in ids:
            error += "Duplicate Employee ID. "
        else:
            ids.append(employee_id)


        if error == "":
            valid_rows.append((
                employee_id,
                row["Full Name"],
                row["Job Title"],
                float(salary),
                row["Email"],
                row["Company"]
            ))
        else:
            errors.append("Row " + str(index + 1) + ": " + error)


    db = pymysql.connect(
        host="localhost",
        user="root",
        password="Bola@2040",
        database="excel_validator_db"
    )

    cursor = db.cursor()


    for row in valid_rows:
        cursor.execute("""
            INSERT IGNORE INTO employees
            (employee_id, full_name, job_title, salary, email, company)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, row)

    db.commit()
    db.close()


    return render_template(
    "result.html",
    errors=errors,
    valid_count=len(valid_rows)
)


if __name__ == "__main__":
    app.run(debug=True)