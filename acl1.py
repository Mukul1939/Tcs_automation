import streamlit as st
import re

# Function to replace special characters with underscores
def format_resource_name(name):
    return re.sub(r'[^\w]', '_', name)

# Function to generate Terraform ACL code for a single operation
def generate_acl_terraform_code(resource_name, resource_type, user, operation):
    formatted_resource_name = format_resource_name(resource_name)
    formatted_user = format_resource_name(user)
    formatted_operation = format_resource_name(operation)
    
    terraform_code = f'''
resource "kafka_acl" "{formatted_resource_name}_{formatted_operation}_{formatted_user}" {{
    resource_name = "{resource_name}"
    resource_type = "{resource_type}"
    acl_principal = "User:{user}"
    acl_host = "*"
    acl_operation = "{operation}"
    acl_permission = "Allow"
}}
'''
    return terraform_code

# Streamlit UI
st.title("Kafka ACL Terraform Generator")

# Initialize session state to hold multiple ACLs
if "acls" not in st.session_state:
    st.session_state.acls = [{"resource_name": "", "resource_type": "Topic", "user": "", "operations": []}]

# Function to add a new ACL
def add_acl():
    st.session_state.acls.append({"resource_name": "", "resource_type": "Topic", "user": "", "operations": []})

# Button to add new ACLs
if st.button("Add another ACL"):
    add_acl()

# Display ACL configuration fields for each ACL
for idx, acl in enumerate(st.session_state.acls):
    st.subheader(f"ACL {idx + 1}")
    
    # Get resource type (Topic or Group)
    resource_type = st.radio(f"Select resource type for ACL {idx + 1}:", ("Topic", "Group"), key=f"resource_type_{idx}")
    st.session_state.acls[idx]["resource_type"] = resource_type
    
    # Get resource name (topic name or group ID)
    resource_name = st.text_input(f"Enter {resource_type.lower()} name for ACL {idx + 1}:", key=f"resource_name_{idx}")
    st.session_state.acls[idx]["resource_name"] = resource_name
    
    # Get user
    user = st.text_input(f"Enter user for ACL {idx + 1}:", key=f"user_{idx}")
    st.session_state.acls[idx]["user"] = user
    
    # Get multiple operations as comma-separated input
    operations = st.text_input(f"Enter operations (e.g., read, write, describe) for ACL {idx + 1}, separated by commas:", key=f"operations_{idx}")
    st.session_state.acls[idx]["operations"] = [op.strip() for op in operations.split(',')] if operations else []

# Button to generate Terraform code for all ACLs
if st.button("Generate ACL Terraform Code"):
    terraform_code = ""
    for idx, acl in enumerate(st.session_state.acls):
        resource_name = acl["resource_name"]
        resource_type = acl["resource_type"]
        user = acl["user"]
        operations = acl["operations"]
        
        if resource_name and user and operations:
            for operation in operations:
                terraform_code += generate_acl_terraform_code(resource_name, resource_type, user, operation)
        else:
            st.error(f"Please fill all the fields for ACL {idx + 1}.")
    
    st.code(terraform_code, language='terraform')
