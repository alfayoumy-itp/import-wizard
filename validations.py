import pandas as pd
import re

# Helper Validation Functions
def validate_unique(column, column_name):
    duplicates = column[column.duplicated()]
    if not duplicates.empty:
        return f"❌ {column_name} contains duplicate values: {duplicates.to_list()}"
    return None

def validate_conditional(dataframe, condition_col, condition_val, target_col, target_name):
    invalid_rows = dataframe[
        (dataframe[condition_col] == condition_val) & dataframe[target_col].isnull()
    ]
    if not invalid_rows.empty:
        return f"❌ {target_name} is required when {condition_col} is {condition_val}. Rows: {invalid_rows.index.to_list()}"
    return None

def validate_length(column, max_length, column_name):
    too_long = column[column.str.len() > max_length]
    if not too_long.empty:
        return f"❌ {column_name} exceeds max length of {max_length}. Rows: {too_long.index.to_list()}"
    return None

def validate_email(column):
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    invalid_emails = column[~column.str.match(email_regex, na=False)]
    if not invalid_emails.empty:
        return f"❌ Invalid email addresses found: {invalid_emails.to_list()}"
    return None

def validate_phone(column):
    phone_regex = r'^\+?\d[\d\s()-]{8,}$'
    invalid_phones = column[~column.str.match(phone_regex, na=False)]
    if not invalid_phones.empty:
        return f"❌ Invalid phone numbers found: {invalid_phones.to_list()}"
    return None

def validate_boolean(column, column_name):
    invalid_values = column[~column.isin([True, False, "TRUE", "FALSE", "true", "false"])]
    if not invalid_values.empty:
        return f"❌ {column_name} contains invalid boolean values. Rows: {invalid_values.index.to_list()}"
    return None


# Validation Rules for Templates
def validate_customer_template(dataframe):
    errors = []

    # 1. External ID must be unique
    if "externalId" in dataframe.columns:
        errors.append(validate_unique(dataframe["externalId"], "External ID"))

    # 2. Customer ID must be unique
    if "entityId" in dataframe.columns:
        errors.append(validate_unique(dataframe["entityId"], "Customer ID"))

    # 3. Conditional Fields
    if "isPerson" in dataframe.columns:
        if "companyName" in dataframe.columns:
            errors.append(validate_conditional(dataframe, "isPerson", "FALSE", "companyName", "Company Name"))
        if "firstName" in dataframe.columns:
            errors.append(validate_conditional(dataframe, "isPerson", "TRUE", "firstName", "First Name"))
        if "lastName" in dataframe.columns:
            errors.append(validate_conditional(dataframe, "isPerson", "TRUE", "lastName", "Last Name"))

    # 4. Length Validations
    length_constraints = {
        "externalId": 100,
        "entityId": 80,
        "companyName": 83,
        "firstName": 32,
        "lastName": 32,
        "email": 300,
        "phone": 21,
        "Address1_line1": 150,
        "Address1_city": 50,
    }
    for field, max_length in length_constraints.items():
        if field in dataframe.columns:
            errors.append(validate_length(dataframe[field].astype(str), max_length, field))

    # 5. Email Validation
    if "email" in dataframe.columns:
        errors.append(validate_email(dataframe["email"]))

    # 6. Phone Validation
    if "phone" in dataframe.columns:
        errors.append(validate_phone(dataframe["phone"]))

    # 7. Boolean Validations
    for boolean_field in ["isPerson", "isInactive"]:
        if boolean_field in dataframe.columns:
            errors.append(validate_boolean(dataframe[boolean_field], boolean_field))

    # Remove empty errors
    return [error for error in errors if error]
