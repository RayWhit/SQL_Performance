import requests
import time
import math
import numpy as np
from scipy.stats import kstest
from scipy.stats import lognorm
from scipy.stats.mstats import variation
import matplotlib.pyplot as plt


graphql_queries = {  
  "gql_ug" : """
  {
    userPage {
      id
      name
      surname
      email
      GDPRInfo
      valid
    }
  }""",

  "gql_documents" : """{
    documentsPage {
      author
      created
      description
      dspaceId
      id
      lastchange
      name
    }
  }""",

  "gql_events" : """
  {
    eventGroupPage {
      id
      groupId
      eventId
      created
      lastchange
    }
  }""",

  "gql_externalids" : """{
    externalidtypePage {
      id
      name
      lastchange
      created
      nameEn
    }
  }""",

  "gql_facilities" : """{
    facilityEventStateTypePage {
      id
      name
      nameEn
      lastchange
    }
  }""",

  "gql_forms" : """{
    formCategoryPage {
      id
      name
      nameEn
      created
      lastchange
    }
  }""",

  "gql_granting" : """{
    programPage {
      id
      name
      lastchange
      nameEn
    }
  }""",

  "gql_grantinga" : """{
    ************************ dont have yet *****************************
  }""",

  "gql_lessons" : """{
    plannedLessonPage {
      id
      name
      lastchange
      length
      order
    }
  }""",

  "gql_preferences" : """{
    ************************ dont have yet *****************************
  }""",

  "gql_presences" : """{
    taskPage {
      id
      name
      lastchange
      briefDes
      dateOfEntry
      dateOfFulfillment
      dateOfSubmission
      detailedDes
      reference
    }
  }""",

  "gql_projects" : """{
    projectCategoryPage {
      id
      lastchange
      name
      nameEn
    }
  }""",

  "gql_publications" : """{
    publicationPage {
      id
      name
      lastchange
      place
      publishedDate
      reference
      valid
    }
  }""",

  "gql_surveys" : """{
    surveyPage {
      id
      name
      lastchange
    }
  }""",

  "gql_workflow" : """{
    ************************ dont have yet *****************************
  }""",
  

  "gql_workflows" : """{
    authorizationGroupPage {
      id
      created
      accesslevel
      lastchange
    }
  }"""

}



# print(graphql_queries)



print()
for query in graphql_queries:

  graphql_query = graphql_queries[query]

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


  times = []





  for i in range(1000):
    start_time = time.time()

    # Send the GraphQL query to the Apollo Federation gateway
    response = requests.post(gateway_url, json=payload, headers=headers)
    end_time = time.time()

    times.append(end_time - start_time)

    # Check the response status
    if response.status_code == 200:
      # Parse and print the response JSON
      # print(response.json())
      # print("Time: ", end_time - start_time)
      error = False
      pass
    else:
      # print(f"Error: {response.status_code}\n{response.text}")
      error = True
      break
  
  print("************ ", query, " ************")
  if error:
    print("ERROR")
  else:
    # print(times)
    times.sort()
    # print(times)
    numpy_times = np.asarray(times, dtype=np.float32)
    print(kstest(numpy_times, 'norm'))
    print("Average time: ", 1000*sum(times)/len(times), " ms")
    print("Variance: ", np.var(numpy_times).item()*1000, " ms")

    plt.hist(numpy_times, edgecolor='black', bins=20)
    plt.show()

  print()
  



  # spocitej rozptyl