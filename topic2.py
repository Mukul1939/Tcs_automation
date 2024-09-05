import streamlit as st
import re

# Function to replace special characters with underscores
def format_topic_name(topic_name):
    return re.sub(r'[^\w]', '_', topic_name)

# Function to generate Terraform code for a single topic
def generate_terraform_code(topic_name, partitions, custom_config=False, config_params=None):
    formatted_topic_name = format_topic_name(topic_name)
    base_config = f'''
resource "kafka_topic" "{formatted_topic_name}" {{
    name = "{topic_name}"
    replication_factor = local.replication_factor
    partitions = {partitions}
    '''
    
    if custom_config and config_params:
        config = "config = {\n"
        for key, value in config_params.items():
            config += f'        "{key}" = {value}\n'
        config += "    }\n"
    else:
        config = '''config = {
        "segment.ms" = local.segment_ms
        "cleanup.policy" = local.cleanup.policy["delete"]
        "compression.type" = local.compression.type["gzip"]
    }\n'''

    lifecycle = '''    lifecycle {
        prevent_destroy = true
    }
}
'''
    return base_config + config + lifecycle

# Streamlit UI
st.title("Kafka Topic Terraform Generator")

# Initialize session state to hold multiple topics
if "topics" not in st.session_state:
    st.session_state.topics = [{"name": "", "config_type": "Default", "partitions": 3, "config_params": {}, "extra_config": []}]

# Function to add a new topic
def add_topic():
    st.session_state.topics.append({"name": "", "config_type": "Default", "partitions": 3, "config_params": {}, "extra_config": []})

# Button to add new topics
if st.button("Add another topic"):
    add_topic()

# Display topic configuration fields for each topic
for idx, topic in enumerate(st.session_state.topics):
    st.subheader(f"Topic {idx + 1}")
    
    # Get topic name from user
    topic_name = st.text_input(f"Enter topic name for Topic {idx + 1}:", key=f"topic_name_{idx}")
    st.session_state.topics[idx]["name"] = topic_name
    
    # Ask if default or custom configuration for each topic
    config_type = st.radio(f"Select topic configuration type for Topic {idx + 1}:", ("Default", "Custom"), key=f"config_type_{idx}")
    st.session_state.topics[idx]["config_type"] = config_type
    
    # Initialize config_params dict
    config_params = {}

    # Add partitions input for custom config
    if config_type == "Custom":
        partitions = st.number_input(f"Enter number of partitions for Topic {idx + 1}:", min_value=1, value=3, step=1, key=f"partitions_{idx}")
        st.session_state.topics[idx]["partitions"] = partitions

        st.subheader(f"Custom Configuration for Topic {idx + 1}")
        segment_ms = st.text_input(f"Enter segment.ms value for Topic {idx + 1}:", "local.segment_ms", key=f"segment_ms_{idx}")
        cleanup_policy = st.text_input(f"Enter cleanup.policy value for Topic {idx + 1}:", 'local.cleanup.policy["delete"]', key=f"cleanup_policy_{idx}")
        compression_type = st.text_input(f"Enter compression.type value for Topic {idx + 1}:", 'local.compression.type["gzip"]', key=f"compression_type_{idx}")
        
        config_params = {
            "segment.ms": segment_ms,
            "cleanup.policy": cleanup_policy,
            "compression.type": compression_type
        }
        st.session_state.topics[idx]["config_params"] = config_params

        # Allow user to add new config keys dynamically for each topic
        st.subheader(f"Add additional configuration for Topic {idx + 1}")
        if "extra_config" not in st.session_state.topics[idx]:
            st.session_state.topics[idx]["extra_config"] = []
        
        # Button to add a new config field for this topic
        if st.button(f"Add new config for Topic {idx + 1}"):
            st.session_state.topics[idx]["extra_config"].append({"key": "", "value": ""})

        # Display dynamically added config fields for this topic
        for i, extra_config in enumerate(st.session_state.topics[idx]["extra_config"]):
            key = st.text_input(f"Config Key {i + 1} for Topic {idx + 1}:", value=extra_config["key"], key=f"key_{idx}_{i}")
            value = st.text_input(f"Config Value {i + 1} for Topic {idx + 1}:", value=extra_config["value"], key=f"value_{idx}_{i}")
            st.session_state.topics[idx]["extra_config"][i] = {"key": key, "value": value}
            if key and value:
                st.session_state.topics[idx]["config_params"][key] = value

# Button to generate Terraform code for all topics
if st.button("Generate Terraform Code"):
    terraform_code = ""
    for idx, topic in enumerate(st.session_state.topics):
        if topic["name"]:
            if topic["config_type"] == "Custom":
                terraform_code += generate_terraform_code(
                    topic["name"],
                    topic["partitions"],
                    custom_config=True,
                    config_params=topic["config_params"]
                )
            else:
                terraform_code += generate_terraform_code(
                    topic["name"],
                    partitions=3  # Default partitions = 3
                )
        else:
            st.error(f"Please enter a topic name for Topic {idx + 1}.")
    
    st.code(terraform_code, language='terraform')
