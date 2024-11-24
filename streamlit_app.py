import streamlit as st
import pandas as pd
import openpyxl
from validations import validate_customer_template  # Import validation functions
import countries
import weird_characters

# Upload Templates
TEMPLATES = {
    "Assembly Template": "Assembly Template.xlsx",
    "Bill of Material Template": "Bill of material template.xlsx",
    "Customer Template": "Customer Template.xlsx",
    # Add all templates you have in the dictionary
}

VALIDATIONS = {
    "Customer Template": validate_customer_template,
    # Add all templates you have in the dictionary
}

# Sidebar Navigation
menu = ["Interactive Import Wizard", "Rename Country Names", "Clean Weird Characters"]
choice = st.sidebar.selectbox("Select Page", menu)

if choice == "Interactive Import Wizard":
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
            template_file = TEMPLATES[selected_template]
            st.write(f"You selected the {selected_template} template.")
            
            # Load template column headers
            try:
                template_data = pd.read_excel(template_file, dtype=str)
                template_columns = template_data.columns.tolist()
            except Exception as e:
                st.error(f"Error loading the template file: {e}")
                template_columns = []

            # Step 3: Mapping Columns
            st.subheader("Column Mapping")
            column_mapping = {}

            for col in data.columns:
                # Check if the column name matches any of the template columns
                default_selection = col if col in template_columns else "--Select--"
                
                # Get the index of the default selection in the options list
                options = ["--Select--"] + template_columns
                default_index = options.index(default_selection)
                
                # Create a selectbox with the default selection
                mapped_field = st.selectbox(
                    f"Map your data column `{col}` to a template field:",
                    options=options,
                    index=default_index,
                    key=col
                )
                
                # Add mapping if a valid field is selected
                if mapped_field != "--Select--":
                    column_mapping[col] = mapped_field

            # Step 4: Data Exploration
            st.subheader("Data Exploration")
            # Show the column-wise data insights
            if st.checkbox("Show Column Information"):
                # Display data types and number of missing values
                col_info = pd.DataFrame({
                    'Null Values': data.isnull().sum(),
                    'Non-Null Values': data.notnull().sum(),
                    'Unique Values': data.nunique()
                })
                st.write(col_info)

            # Step 5: Validation
            st.subheader("Validation Results")
            if st.button("Validate File"):
                # Automatically rename columns in the DataFrame
                data.rename(columns=column_mapping, inplace=True)
                validation_function = VALIDATIONS[selected_template]
                validation_errors = validation_function(data)

                if validation_errors:
                    st.error("Validation errors found!")
                else:
                    st.success("All validations passed!")

            # Step 6: Export Validated File
            st.subheader("Export Results")
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


elif choice == "Rename Country Names":
    st.title("Rename Country Names")

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

        # Step 2: Select Country Column
        country_column = st.selectbox("Select the column containing country names:", data.columns)

        # Step 3: Rename Countries
        if st.button("Rename Countries"):
            try:
                updated_data = countries.rename_countries(data, country_column)
                st.success("Country names updated successfully!")
                st.dataframe(updated_data.head())

                # Step 4: Export Updated File
                output_file = "Updated_Country_Names.xlsx"
                updated_data.to_excel(output_file, index=False)
                with open(output_file, "rb") as file:
                    st.download_button(
                        label="Download Updated File",
                        data=file,
                        file_name=output_file,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            except Exception as e:
                st.error(f"Error during processing: {e}")
                


elif menu == "Clean Weird Characters":
    st.title("Clean Weird Characters")

    # File upload
    uploaded_file = st.file_uploader("Upload a file (CSV/Excel)", type=["csv", "xlsx"])
    
    if uploaded_file:
        # Load the file into a DataFrame
        file_extension = uploaded_file.name.split('.')[-1].lower()
        if file_extension == "csv":
            df = pd.read_csv(uploaded_file, dtype=str)
        elif file_extension == "xlsx":
            df = pd.read_excel(uploaded_file, dtype=str)

        st.write("Preview of Uploaded File:")
        st.dataframe(df.head())

        # Column selection
        st.subheader("Select Columns to Clean")
        selected_columns = st.multiselect("Select the columns to clean:", df.columns.tolist())

        # Language selection
        st.subheader("Select Language")
        language = st.radio("Choose the language:", ["English", "Arabic"])

        # Process and clean the data
        if st.button("Clean Data"):
            if not selected_columns:
                st.error("Please select at least one column to clean.")
            else:
                # Use the clean_columns function from the module
                cleaned_df, weird_characters_df = weird_characters.clean_columns(df, selected_columns, language)

                st.success("Data cleaning completed!")
                st.write("Preview of Cleaned Data:")
                st.dataframe(cleaned_df.head())

                # Download files
                st.subheader("Download Results")

                # 1) Rows with weird characters
                if not weird_characters_df.empty:
                    st.write("Download rows with weird characters:")
                    weird_file = "rows_with_weird_characters.xlsx"
                    weird_characters_df.to_excel(weird_file, index=False)
                    with open(weird_file, "rb") as file:
                        st.download_button(
                            label="Download Rows with Weird Characters",
                            data=file,
                            file_name=weird_file,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                else:
                    st.info("No weird characters found in the selected columns.")

                # 2) Cleaned file
                cleaned_file = "cleaned_data.xlsx"
                cleaned_df.to_excel(cleaned_file, index=False)
                with open(cleaned_file, "rb") as file:
                    st.download_button(
                        label="Download Cleaned File",
                        data=file,
                        file_name=cleaned_file,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )