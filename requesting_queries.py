import requests

# Define the GraphQL query
graphql_query = """
{
  userPage {
    name
    surname
    email
    id
  }
}
"""

# Define the URL of the Apollo Federation gateway
gateway_url = "http://localhost:33000/api/gql"

# Set the headers (optional, but may be needed for authentication)
headers = {
    "Content-Type": "application/json",
    # Add any other headers if necessary
}

# Create the request payload
payload = {
    "query": graphql_query,
    # You can also include variables, operationName, etc. in the payload if needed
}

# Send the GraphQL query to the Apollo Federation gateway
response = requests.post(gateway_url, json=payload, headers=headers)

# Check the response status
if response.status_code == 200:
    # Parse and print the response JSON
    print(response.json())
else:
    print(f"Error: {response.status_code}\n{response.text}")