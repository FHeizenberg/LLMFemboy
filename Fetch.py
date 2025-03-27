import requests
import json


class MockAPIClient:
    def __init__(self, base_url):
        """
        Initialize the MockAPI client with a base URL.

        :param base_url: Base URL of the MockAPI endpoint
        """
        self.base_url = base_url
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    def get_all_resources(self):
        """
        Fetch all resources from the MockAPI endpoint.

        :return: List of resources or None if request fails
        """
        try:
            response = requests.get(self.base_url, headers=self.headers)
            response.raise_for_status()  # Raise an exception for bad status codes

            # Parse the JSON response
            resources = response.json()

            # Return the first Query value as plain text
            return resources[0]['Query']

        except requests.RequestException as e:
            print(f"Error fetching resources: {e}")
            return ""

    def get_resource_by_id(self, resource_id):
        """
        Fetch a specific resource by its ID.

        :param resource_id: ID of the resource to fetch
        :return: Query value as plain text
        """
        try:
            response = requests.get(f"{self.base_url}/{resource_id}", headers=self.headers)
            response.raise_for_status()

            # Parse the JSON response
            resource = response.json()

            # Return the Query value as plain text
            return resource['Query']

        except requests.RequestException as e:
            print(f"Error fetching resource {resource_id}: {e}")
            return ""

    def create_resource(self, data):
        """
        Create a new resource on MockAPI.

        :param data: Dictionary containing resource data
        :return: Created resource or None if creation fails
        """
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                data=json.dumps(data)
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error creating resource: {e}")
            return None

    def update_resource(self, resource_id, data):
        """
        Update an existing resource.

        :param resource_id: ID of the resource to update
        :param data: Dictionary with updated resource data
        :return: Updated resource or None if update fails
        """
        try:
            response = requests.put(
                f"{self.base_url}/{resource_id}",
                headers=self.headers,
                data=json.dumps(data)
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error updating resource {resource_id}: {e}")
            return None

    def delete_resource(self, resource_id):
        """
        Delete a resource by its ID.

        :param resource_id: ID of the resource to delete
        :return: Boolean indicating success or failure
        """
        try:
            response = requests.delete(
                f"{self.base_url}/{resource_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            print(f"Error deleting resource {resource_id}: {e}")
            return False


# Example usage
def main():
    # MockAPI endpoints
    mock_api_user_query_url = 'https://67e27de897fc65f535365432.mockapi.io/ai/UserQuery'
    mock_api_llm_query_url = 'https://67e27de897fc65f535365432.mockapi.io/ai/LLMQuery'

    # Create client_user_query instance
    client_user_query = MockAPIClient(mock_api_user_query_url)

    # Get all resources
    #all_resources = client.get_all_resources()
    #print(all_resources)

     #Get a specific resource
    specific_resource = client_user_query.get_resource_by_id('1')
    print("Specific Resource:", specific_resource)

     #Delete a resource
    deletion_result = client_user_query.delete_resource('1')
    print("Deletion Successful:", deletion_result)

    # Create a new resource
    new_resource = client_user_query.create_resource({
        'Query': 'Empty',
        'id': '1'
    })
    print("Created Resource:", new_resource)

    # Update a resource
    # updated_resource = client_user_query.update_resource('1', {
    #    'Query': 'A2',
    #    'id': '3'
    # })
    # print("Updated Resource:", updated_resource)

    # Create client_llm_query instance
    client_llm_query = MockAPIClient(mock_api_llm_query_url)

    # Get all resources
    # all_resources = client.get_all_resources()
    # print(all_resources)

    # Get a specific resource
    specific_resource = client_llm_query.get_resource_by_id('1')
    print("Specific Resource:", specific_resource)

    # Delete a resource
    deletion_result = client_llm_query.delete_resource('1')
    print("Deletion Successful:", deletion_result)

    # Create a new resource
    new_resource = client_llm_query.create_resource({
        'Query': 'Empty',
        'id': '1'
    })
    print("Created Resource:", new_resource)

    # Update a resource
    # updated_resource = client_llm_query.update_resource('1', {
    #    'Query': 'A2',
    #    'id': '3'
    # })
    # print("Updated Resource:", updated_resource)


if __name__ == '__main__':
    main()