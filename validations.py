import pandas as pd
import re
import streamlit as st

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

def format_errors_with_table(index_series, column_name):
    error_table = pd.DataFrame({
        "Row Index": index_series.index+2,
        column_name: index_series.values
    })
    st.write(f"❌ Errors in {column_name}:\n")
    style = error_table.style.hide_index()
    st.write(style.to_html(), unsafe_allow_html=True)
    return column_name

# Helper Validation Functions
def validate_unique(column, column_name):
    duplicates = column[column.duplicated()]
    if not duplicates.empty:
        return format_errors_with_table(duplicates, column_name)
    return None

def validate_conditional(dataframe, condition_col, condition_val, target_col, target_name):
    invalid_rows = dataframe[
        (dataframe[condition_col] == condition_val) & dataframe[target_col].isnull()
    ][target_col]
    if not invalid_rows.empty:
        return format_errors_with_table(invalid_rows, target_name)
    return None

def validate_length(column, max_length, column_name):
    too_long = column[column.str.len() > max_length]
    if not too_long.empty:
        return format_errors_with_table(too_long, column_name)
    return None

def validate_email(column):
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    invalid_emails = column[~column.str.match(email_regex, na=False)]
    if not invalid_emails.empty:
        return format_errors_with_table(invalid_emails, "Email")
    return None

def validate_phone(column):
    phone_regex = r'^\+?\d[\d\s()-]{8,}$'
    invalid_phones = column[~column.str.match(phone_regex, na=False)]
    if not invalid_phones.empty:
        return format_errors_with_table(invalid_phones, "Phone")
    return None

def validate_boolean(column, column_name):
    invalid_values = column[~column.isin([True, False, "TRUE", "FALSE"])]
    if not invalid_values.empty:
        return format_errors_with_table(invalid_values, column_name)
    return None

def validate_subsidiary(column):
    errors = []
    # Check for missing values
    missing_subsidiary = column[column.isnull() | column.str.strip().eq("")]
    if not missing_subsidiary.empty:
        errors.append(format_errors_with_table(missing_subsidiary, "Subsidiary"))
    
    # Validate format
    hierarchy_regex = r'^([^\|:]+(:[^\|:]+)*)(\|([^\|:]+(:[^\|:]+)*))*$'
    invalid_format = column[~column.str.match(hierarchy_regex, na=False)]
    if not invalid_format.empty:
        errors.append(format_errors_with_table(invalid_format, "Subsidiary"))
    
    return "\n".join(errors) if errors else None

def validate_country(column, column_name):
    invalid_countries = column[~column.isin(VALID_COUNTRIES)]
    if not invalid_countries.empty:
        return format_errors_with_table(invalid_countries, column_name)
    return None

def validate_null_values(column, column_name):
    null_rows = column[column.isnull()]
    if not null_rows.empty:
        return format_errors_with_table(null_rows, column_name)
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

    # 5. Email Validation
    if "email" in dataframe.columns:
        errors.append(validate_email(dataframe["email"]))

    # 6. Phone Validation
    if "phone" in dataframe.columns:
        errors.append(validate_phone(dataframe["phone"]))

    # 7. Boolean Validations
    for boolean_field in ["isPerson", "isInactive", "Address1_defaultBilling", "Address1_defaultShipping", "Address2_defaultBilling", "Address2_defaultShipping"]:
        if boolean_field in dataframe.columns:
            dataframe[boolean_field] = dataframe[boolean_field].str.upper()
            errors.append(validate_boolean(dataframe[boolean_field], boolean_field))
    
    # 8. Subsidiary Validation
    if "subsidiary" in dataframe.columns:
        subsidiary_errors = validate_subsidiary(dataframe["subsidiary"].astype(str))
        errors.append(subsidiary_errors)

    # 9. Country Validation
    for country_field in ["Address1_country", "Address2_country"]:
        if country_field in dataframe.columns:
            errors.append(validate_country(dataframe[country_field].dropna(), country_field))
            errors.append(validate_null_values(dataframe[country_field], country_field))

    # Remove empty errors
    return [error for error in errors if error]
