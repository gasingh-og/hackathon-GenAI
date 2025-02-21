import streamlit as st
from llm import send_request 
import pandas as pd


def main():
    st.title("Analytics")

    # Input field for user message
    user_message = st.text_input("Enter your question:")

    if st.button("Submit"):
        if user_message.strip():
            with st.spinner("Sending request..."):
                response = send_request(user_message)
                st.success("Response received!")
                # st.markdown(f"{response}")
                df=pd.DataFrame(response);
                st.dataframe(df)
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