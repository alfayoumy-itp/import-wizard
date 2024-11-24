import pandas as pd
import re
import streamlit as st
from email_validator import validate_email, EmailNotValidError
import numpy as np
import phonenumbers

# List of valid countries
VALID_COUNTRIES = [
    "Afghanistan", "Albania", "Algeria", "American Samoa", "Andorra", "Angola", "Anguilla", "Antarctica",
    "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahamas",
    "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bermuda", "Bhutan",
    "Bolivia (Plurinational State of)", "Bonaire, Sint Eustatius and Saba", "Bosnia and Herzegovina",
    "Botswana", "Bouvet Island", "Brazil", "British Indian Ocean Territory", "Brunei Darussalam", "Bulgaria",
    "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Canary Islands", "Cayman Islands",
    "Central African Republic", "Ceuta and Melilla", "Chad", "Chile", "China", "Christmas Island",
    "Cocos (Keeling) Islands", "Colombia", "Comoros", "Congo", "Congo (the Democratic Republic of the)",
    "Cook Islands", "Costa Rica", "Croatia", "Cuba", "Curaçao", "Cyprus", "Czechia", "Côte d'Ivoire",
    "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador",
    "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Falkland Islands (Malvinas)",
    "Faroe Islands", "Fiji", "Finland", "France", "French Guiana", "French Polynesia", "French Southern Territories",
    "Gabon", "Gambia", "Georgia", "Germany", "Ghana", "Gibraltar", "Greece", "Greenland", "Grenada",
    "Guadeloupe", "Guam", "Guatemala", "Guernsey", "Guinea", "Guinea-Bissau", "Guyana", "Haiti",
    "Heard Island and McDonald Islands", "Holy See", "Honduras", "Hong Kong", "Hungary", "Iceland", "India",
    "Indonesia", "Iran (Islamic Republic of)", "Iraq", "Ireland", "Isle of Man", "Israel", "Italy", "Jamaica",
    "Japan", "Jersey", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea (the Democratic People's Republic of)",
    "Korea (the Republic of)", "Kosovo", "Kuwait", "Kyrgyzstan", "Lao People's Democratic Republic", "Latvia",
    "Lebanon", "Lesotho", "Liberia", "Libya", "Liechtenstein", "Lithuania", "Luxembourg", "Macao", "Madagascar",
    "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Martinique", "Mauritania", "Mauritius",
    "Mayotte", "Mexico", "Micronesia (Federated States of)", "Moldova (the Republic of)", "Monaco", "Mongolia",
    "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands",
    "Netherlands Antilles (Deprecated)", "New Caledonia", "New Zealand", "Nicaragua", "Niger", "Nigeria", "Niue",
    "Norfolk Island", "North Macedonia", "Northern Mariana Islands", "Norway", "Oman", "Pakistan", "Palau",
    "Palestine, State of", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Pitcairn", "Poland",
    "Portugal", "Puerto Rico", "Qatar", "Romania", "Russian Federation", "Rwanda", "Réunion",
    "Saint Barthélemy", "Saint Helena, Ascension and Tristan da Cunha", "Saint Kitts and Nevis", "Saint Lucia",
    "Saint Martin (French part)", "Saint Pierre and Miquelon", "Saint Vincent and the Grenadines", "Samoa",
    "San Marino", "Sao Tome and Principe", "Saudi Arabia", "Senegal", "Serbia", "Serbia and Montenegro (Deprecated)",
    "Seychelles", "Sierra Leone", "Singapore", "Sint Maarten (Dutch part)", "Slovakia", "Slovenia", "Solomon Islands",
    "Somalia", "South Africa", "South Georgia and the South Sandwich Islands", "South Sudan", "Spain", "Sri Lanka",
    "Sudan", "Suriname", "Svalbard and Jan Mayen", "Sweden", "Switzerland", "Syrian Arab Republic",
    "Taiwan (Province of China)", "Tajikistan", "Tanzania, the United Republic of", "Thailand", "Timor-Leste",
    "Togo", "Tokelau", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Turks and Caicos Islands",
    "Tuvalu", "Türkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States",
    "United States Minor Outlying Islands", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela (Bolivarian Republic of)",
    "Viet Nam", "Virgin Islands (British)", "Virgin Islands (U.S.)", "Wallis and Futuna", "Western Sahara",
    "Yemen", "Zambia", "Zimbabwe", "Åland Islands"
]

# Valid terms for validation
VALID_TERMS = [
    "1% 10 Net 30", "2% 10 Net 30", "Due on receipt", 
    "Net 15", "Net 30", "Net 45", "Net 60"
]

# Valid currency codes for validation
VALID_CURRENCIES = [
    "AFN", "ALL", "DZD", "USD", "EUR", "AOA", "XCD", "ARS", "AMD", "AWG", "AUD", 
    "AZN", "BSD", "BHD", "BDT", "BBD", "BYN", "BZD", "XOF", "BMD", "BTN", "INR", 
    "BOB", "BOV", "BAM", "BWP", "NOK", "BRL", "BND", "BGN", "BIF", "CVE", "KHR", 
    "XAF", "CAD", "KYD", "CLF", "CLP", "CNY", "COP", "COU", "KMF", "CDF", "NZD", 
    "CRC", "CUC", "CUP", "ANG", "CZK", "DKK", "DJF", "DOP", "EGP", "SVC", "ERN", 
    "ETB", "FKP", "FJD", "GMD", "GEL", "GHS", "GIP", "GTQ", "GBP", "GNF", "GYD", 
    "HTG", "HNL", "HKD", "HUF", "ISK", "IDR", "XDR", "IRR", "IQD", "ILS", "JMD", 
    "JPY", "JOD", "KZT", "KES", "KPW", "KRW", "KWD", "KGS", "LAK", "LBP", "LSL", 
    "ZAR", "LRD", "LYD", "CHF", "MOP", "MGA", "MWK", "MYR", "MVR", "MRU", "MUR", 
    "MXN", "MXV", "MDL", "MNT", "MAD", "MZN", "MMK", "NAD", "NPR", "NIO", "NGN", 
    "OMR", "PKR", "PAB", "PGK", "PYG", "PEN", "PHP", "PLN", "QAR", "MKD", "RON", 
    "RUB", "RWF", "SHP", "WST", "STN", "SAR", "RSD", "SCR", "SLE", "SGD", "ANG", 
    "SBD", "SOS", "SSP", "LKR", "SDG", "SRD", "SZL", "SEK", "CHE", "CHW", "SYP", 
    "TWD", "TJS", "TZS", "THB", "TOP", "TTD", "TND", "TRY", "TMT", "UGX", "UAH", 
    "AED", "USN", "UYI", "UYU", "UZS", "VUV", "VEF", "VND", "XPF", "YER", "ZMW", 
    "ZWL"
]

def format_errors_with_table(index_series, column_name, error_message):
    error_table = pd.DataFrame({
        "Row Index": index_series.index + 2,
        column_name: index_series.values
    })
    st.write(f"❌ Errors in {column_name}, {error_message}:\n")
    st.dataframe(error_table, hide_index=True)
    return column_name

# Helper Validation Functions
def validate_unique(column, column_name):
    duplicates = column[column.duplicated()]
    if not duplicates.empty:
        return format_errors_with_table(duplicates, column_name, "duplicate values found")
    return None

def validate_conditional(dataframe, condition_col, condition_val, target_col, target_name):
    invalid_rows = dataframe[
        (dataframe[condition_col] == condition_val) & dataframe[target_col].isnull()
    ][target_col]
    if not invalid_rows.empty:
        return format_errors_with_table(invalid_rows, target_name, f"missing values in '{target_name}' when '{condition_col}' is '{condition_val}'")
    return None

def validate_length(column, max_length, column_name):
    too_long = column[column.str.len() > max_length]
    if not too_long.empty:
        return format_errors_with_table(too_long, column_name, f"values exceed the maximum length of {max_length}")
    return None

def validate_emails(column, column_name):
    invalid_emails = []
    for email in column:
        try:
            # Validate email and normalize
            emailinfo = validate_email(email, check_deliverability=False)
            normalized_email = emailinfo.normalized
        except EmailNotValidError as e:
            invalid_emails.append(email)
    
    if invalid_emails:
        return format_errors_with_table(pd.Series(invalid_emails), column_name, "invalid email format")
    
    return None

def validate_phone_number(phone, subsidiary_country='US'):
    if pd.isnull(phone):
        return np.NaN
    
    # Skip single quote character if it exists as the first character
    if phone.startswith("'"):
        phone = phone[1:]

    # Check maximum length
    if len(phone) > 32:
        return "Invalid phone number: exceeds maximum length of 32 characters"

    # Check for emergency service phone numbers (commonly start with specific digits)
    emergency_numbers = ['112', '911', '999', '100', '101', '102']  # Add more if necessary
    if any(phone.startswith(emergency) for emergency in emergency_numbers):
        return "Valid emergency service number"

    # Attempt to parse the phone number
    try:
        if phone.startswith('+'):
            parsed_number = phonenumbers.parse(phone)
        else:
            # Assuming a default country code; adjust as needed
            parsed_number = phonenumbers.parse(phone, subsidiary_country)

        # Validate the phone number
        if not phonenumbers.is_valid_number(parsed_number) or not phonenumbers.is_possible_number(parsed_number):
            # Return the formatted number if valid
            return "Invalid phone number format: {phone}"

    except phonenumbers.NumberParseException as e:
        return f"Error parsing phone number: {e}"
    except phonenumbers.PhoneNumberFormatException as e:
        return f"Error formatting phone number: {e}"

    return "Invalid phone number format: {phone}"

def validate_phone(column, column_name):
    # Apply `validate_phone_number` to the column
    validation_results = column.apply(validate_phone_number)

    # Identify invalid phone numbers
    invalid_phones = validation_results[validation_results.str.contains("Invalid", na=False)]
    if not invalid_phones.empty:
        return format_errors_with_table(invalid_phones, column_name, "invalid phone number format")

    return None

def validate_boolean(column, column_name):
    invalid_values = column[~column.isin([True, False, "TRUE", "FALSE"])]
    if not invalid_values.empty:
        return format_errors_with_table(invalid_values, column_name, "contains values that are not boolean (TRUE, FALSE)")
    return None

def validate_subsidiary(column, column_name):
    errors = []
    # Check for missing values
    missing_subsidiary = column[column.isnull() | column.str.strip().eq("")]
    if not missing_subsidiary.empty:
        errors.append(format_errors_with_table(missing_subsidiary, column_name, "contains missing values"))
    
    # Validate format
    hierarchy_regex = r'^([^\|:]+(:[^\|:]+)*)(\|([^\|:]+(:[^\|:]+)*))*$'
    invalid_format = column[~column.str.match(hierarchy_regex, na=False)]
    if not invalid_format.empty:
        errors.append(format_errors_with_table(invalid_format, column_name, "has invalid subsidiary hierarchy format"))
    
    return "\n".join(errors) if errors else None

def validate_country(column, column_name):
    invalid_countries = column[~column.isin(VALID_COUNTRIES)]
    if not invalid_countries.empty:
        return format_errors_with_table(invalid_countries, column_name, "contains invalid country names")
    return None

def validate_null_values(column, column_name):
    null_rows = column[column.isnull()]
    if not null_rows.empty:
        return format_errors_with_table(null_rows, column_name, "contains null (missing) values")
    return None

def validate_terms(column, column_name):
    invalid_terms = column[~column.isin(VALID_TERMS)]
    if not invalid_terms.empty:
        return format_errors_with_table(
            invalid_terms, column_name, 
            "contains invalid payment terms"
        )
    return None

def validate_currency(column, column_name):
    invalid_currencies = column[~column.isin(VALID_CURRENCIES)]
    if not invalid_currencies.empty:
        return format_errors_with_table(
            invalid_currencies, column_name, 
            "contains invalid currency codes"
        )
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

    # 3. Length Validations
    length_constraints = {
        "externalId": 100,
        "entityId": 80,
        "companyName": 83,
        "firstName": 32,
        "lastName": 32,
        "email": 300,
        "phone": 21,
        "Address1_AddressName": 150,
        "Address2_AddressName": 150,
        "Address2_attention": 83,
        "Address2_Addressee": 83,
        "Address1_Addressee": 83,
        "Address1_line1": 150,
        "Address1_line2": 150,
        "Address1_city": 50,
        "Address1_phone": 21,
        "Address2_line1": 150,
        "Address2_line2": 150,
        "Address2_city": 50,
        "Address2_phone": 21,
        "accountNumber": 99,
        "vatregnumber": 50
    }
    for field, max_length in length_constraints.items():
        if field in dataframe.columns:
            errors.append(validate_length(dataframe[field].astype(str), max_length, field))

    # 4. Email Validation
    if "email" in dataframe.columns:
        errors.append(validate_emails(dataframe["email"], "email"))

    # 5. Phone Validation
    for phone_field in ["phone", "Address1_phone", "Address2_phone"]:
        if phone_field in dataframe.columns:
            errors.append(validate_phone(dataframe[phone_field], phone_field))

    # 6. Boolean Validations
    for boolean_field in ["isPerson", "isInactive", "Address1_defaultBilling", "Address1_defaultShipping", "Address2_defaultBilling", "Address2_defaultShipping"]:
        if boolean_field in dataframe.columns:
            dataframe[boolean_field] = dataframe[boolean_field].str.upper()
            errors.append(validate_boolean(dataframe[boolean_field], boolean_field))
    
    # 7. Conditional Fields
    if "isPerson" in dataframe.columns:
        if "companyName" in dataframe.columns:
            errors.append(validate_conditional(dataframe, "isPerson", "FALSE", "companyName", "Company Name"))
        if "firstName" in dataframe.columns:
            errors.append(validate_conditional(dataframe, "isPerson", "TRUE", "firstName", "First Name"))
        if "lastName" in dataframe.columns:
            errors.append(validate_conditional(dataframe, "isPerson", "TRUE", "lastName", "Last Name"))


    # 8. Subsidiary Validation
    if "subsidiary" in dataframe.columns:
        subsidiary_errors = validate_subsidiary(dataframe["subsidiary"].astype(str), "subsidiary")
        errors.append(subsidiary_errors)

    # 9. Country Validation
    for country_field in ["Address1_country", "Address2_country"]:
        if country_field in dataframe.columns:
            errors.append(validate_country(dataframe[country_field].dropna(), country_field))
            errors.append(validate_null_values(dataframe[country_field], country_field))

    # 10. Terms and Currency
    if "terms" in dataframe.columns:
        errors.append(validate_terms(dataframe["terms"], "Terms"))
    if "currency" in dataframe.columns:
        errors.append(validate_currency(dataframe["currency"], "Currency"))

    # Remove empty errors
    return [error for error in errors if error]
