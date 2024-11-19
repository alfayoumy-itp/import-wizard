import streamlit as st
import pandas as pd
import openpyxl
from validations import validate_customer_template  # Import validation functions

# Upload Templates
TEMPLATES = {
    "Customer Template": validate_customer_template,
    # Add other templates here with corresponding validation functions
}

st.title("Interactive Import Wizard")

# Step 1: File Upload
uploaded_file = st.file_uploader("Upload an Excel/CSV File", type=["csv", "xlsx"])

if uploaded_file:
    file_extension = uploaded_file.name.split('.')[-1].lower()
    if file_extension == "csv":
        data = pd.read_csv(uploaded_file, dtype=str)
    elif file_extension == "xlsx":
        data = pd.read_excel(uploaded_file, dtype=str)

    st.write("Preview of Uploaded File:")
    st.dataframe(data.head())

    # Step 2: Template Selection
    selected_template = st.selectbox("Select the Template", list(TEMPLATES.keys()))
    if selected_template:
        st.write(f"You selected the `{selected_template}` template.")

        # Step 3: Column Mapping
        st.subheader("Column Mapping")
        column_mapping = {}
        for col in data.columns:
            user_column = st.selectbox(
                f"Map `{col}` to template field:",
                options=["--Select--"] + list(data.columns),
                key=col
            )
            if user_column != "--Select--":
                column_mapping[col] = user_column

        # Automatically rename columns in the DataFrame
        data.rename(columns=column_mapping, inplace=True)

        # Step 4: Validation
        st.subheader("Validation Results")
        validation_function = TEMPLATES[selected_template]
        validation_errors = validation_function(data)

        if validation_errors:
            st.error("Validation errors found!")
            for error in validation_errors:
                st.write(error)
        else:
            st.success("All validations passed!")

        # Step 5: Export Validated File
        if st.button("Export Validated File"):
            output_file = f"Validated_{selected_template}.xlsx"
            data.to_excel(output_file, index=False)

            with open(output_file, "rb") as file:
                st.download_button(
                    label="Download Validated File",
                    data=file,
                    file_name=output_file,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
