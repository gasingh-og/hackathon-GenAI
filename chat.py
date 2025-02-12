import streamlit as st
from llm import send_request 


def tuples_to_dict(data):
    if isinstance(data, tuple):  # If a single tuple is passed instead of a list
        data = [data]  # Convert it to a list
    result = {"entity": [], "value": []}
    for entity, value in data:
        result["entity"].append(entity)
        result["value"].append(value)
    return result


def main():
    st.title("Analytics")

    # Input field for user message
    user_message = st.text_input("Enter your question:")

    if st.button("Submit"):
        if user_message.strip():
            with st.spinner("Sending request..."):
                response = send_request(user_message)
                st.success("Response received!")
                st.markdown(f"{response}")
                print('response',response)
                data = tuples_to_dict(response)
                print('data', data)
                st.dataframe(data)
                # # Add collapsible section to show full JSON response
                # with st.expander("View Full Response JSON"):
                #     st.json(response)
            # else:
            #     st.error("Failed to fetch the response.")
            #     error_details = response.get("error", "No error details available.")
            #     st.markdown(f"**Error Details:** {error_details}")
        else:
            st.warning("Please enter a message before submitting.")


if __name__ == "__main__":
    main()