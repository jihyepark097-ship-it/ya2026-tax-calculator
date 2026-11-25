import os
import pandas as pd 

def is_valid_ic(ic_number):
    clean_ic = ic_number.strip()
    return clean_ic.isdigit() and len (clean_ic) == 12


def is_valid_user_id(user_id):
     clean_id = user_id.strip()
     return len(clean_id) > 0


def is_valid_amount(value):
    try:
        clean_val = float(value.strip())
        return clean_val >= 0
    except ValueError:
        return False

USERS_FILE = "users.csv"
RECORDS_FILE = "tax_records.csv"


def get_ic_password(ic_number):
    clean_ic = ic_number.strip()
    return clean_ic[-4:]


def load_users(filename=USERS_FILE):
    if not os.path.exists(filename):
        return {}
    try:
        df = pd.read_csv(filename, dtype=str).fillna("")
        users = {}
        for _, row in df.iterrows():
            uid = row.get("user_id", "").strip()
            ic = row.get("ic_number", "").strip()
            if uid and ic:
                users[uid] = ic
        return users
    except Exception:
        return {}


def register_user(user_id, ic_number, filename=USERS_FILE):
    clean_id = user_id.strip()
    clean_ic = ic_number.strip()

    if not is_valid_user_id(clean_id) or not is_valid_ic(clean_ic):
        return False, "Invalid User ID or 12-digit IC number."

    users = load_users(filename)
    if clean_id in users:
        return False, "User ID already exists. Please log in instead."

    # List -> Dictionary -> pandas DataFrame
    new_user_records = [
        {
            "user_id": clean_id,
            "ic_number": clean_ic,
            "password": get_ic_password(clean_ic),
        }
    ]
    new_df = pd.DataFrame(new_user_records)

    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        existing_df = pd.read_csv(filename, dtype=str)
        updated_df = pd.concat([existing_df, new_df], ignore_index=True)
    else:
        updated_df = new_df

    updated_df.to_csv(filename, index=False)
    return True, f"Registered! Your password is the last 4 digits of your IC ({get_ic_password(clean_ic)})."

def authenticate_user(user_id, password_last4, filename=USERS_FILE):
    clean_id = user_id.strip()
    clean_pw = password_last4.strip()
    users = load_users(filename)
    if clean_id not in users:
        return False, None
    if get_ic_password(users[clean_id]) == clean_pw:
        return True, users[clean_id]
    return False, None


def calculate_chargeable_income(annual_income, total_relief):
    chargeable = float(annual_income) - float(total_relief)
    return max(0.0, chargeable)


def calculate_ya2026_tax(chargeable_income):
    ci = max(0.0, float(chargeable_income))
    brackets = [
        (5000, 0.0, 0.00),
        (20000, 5000, 0.01),
        (35000, 20000, 0.03),
        (50000, 35000, 0.06),
        (70000, 50000, 0.11),
        (100000, 70000, 0.19),
        (400000, 100000, 0.25),
        (600000, 400000, 0.26),
        (2000000, 600000, 0.28),
    ]

    tax = 0.0
    for upper, lower, rate in brackets:
        if ci > lower:
            taxable_in_band = min(ci, upper) - lower
            tax += taxable_in_band * rate
        else:
            break

    if ci > 2000000:
        tax += (ci - 2000000) * 0.30

    rebate = 400.0 if ci <= 35000 else 0.0
    tax_payable = max(0.0, tax - rebate)
    return round(tax, 2), round(rebate, 2), round(tax_payable, 2)


def build_tax_record(
    user_id,
    ic_number,
    annual_income,
    total_relief,
    test_case_id=None,
    year_of_assessment=2026,
):
    chargeable = calculate_chargeable_income(annual_income, total_relief)
    gross_tax, rebate, tax_payable = calculate_ya2026_tax(chargeable)
    return {
        "user_id": user_id.strip(),
        "ic_number": ic_number.strip(),
        "test_case_id": test_case_id if test_case_id else "N/A",
        "year_of_assessment": year_of_assessment,
        "annual_income": round(float(annual_income), 2),
        "total_relief": round(float(total_relief), 2),
        "chargeable_income": round(chargeable, 2),
        "gross_tax": gross_tax,
        "rebate": rebate,
        "tax_payable": tax_payable,
    }

def save_tax_record(record, filename=RECORDS_FILE):
    new_df = pd.DataFrame([record])
    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        try:
            existing_df = pd.read_csv(filename, dtype={"ic_number": str})
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        except Exception:
            combined_df = new_df
    else:
        combined_df = new_df

    combined_df.to_csv(filename, index=False)
    return combined_df

def load_tax_records(filename=RECORDS_FILE):
    if not os.path.exists(filename) or os.path.getsize(filename) == 0:
        return pd.DataFrame(columns=[
            "user_id", "ic_number", "annual_income", "total_relief",
            "chargeable_income", "gross_tax", "rebate", "tax_payable"
        ])
    try:
        return pd.read_csv(filename)
    except Exception:
        return pd.DataFrame()


