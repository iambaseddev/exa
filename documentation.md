# Exa.ai Websets API Documentation

*This document is a compilation of documentation from various Exa.ai Websets API pages.*

## Source: https://docs.exa.ai/websets/api/get-started.md

# Get started

> Create your first Webset

## Create and setup your API key

1. Go to the [Exa Dashboard](https://dashboard.exa.ai)
2. Click on "API Keys" in the left sidebar
3. Click "Create API Key"
4. Give your key a name and click "Create"
5. Copy your API key and store it securely - you won't be able to see it again!

<Card title="Get your Exa API key" icon="key" horizontal href="https://dashboard.exa.ai/api-keys" />

<br />

## Create a .env file

Create a file called `.env` in the root of your project and add the following line.

```bash
EXA_API_KEY=your api key without quotes
```

<br />

## Make an API request

Use our Python or JavaScript SDKs, or call the API directly with cURL.

<Tabs>
  <Tab title="Python">
    Install the latest version of the python SDK with pip. If you want to store your API key in a `.env` file, make sure to install the dotenv library.

    ```bash
    pip install exa-py
    pip install python-dotenv
    ```

    Create a file called `webset.py` and add the code below:

    ```python python
    from exa_py import Exa
    from dotenv import load_dotenv
    from exa_py.websets.types import CreateWebsetParameters, CreateEnrichmentParameters

    import os

    load_dotenv()
    exa = Exa(os.getenv('EXA_API_KEY'))

    # Create a Webset with search and enrichments
    webset = exa.websets.create(
        params=CreateWebsetParameters(
            search={
                "query": "Top AI research labs focusing on large language models",
                "count": 5
            },
            enrichments=[
                CreateEnrichmentParameters(
                    description="LinkedIn profile of VP of Engineering or related role",
                    format="text",
                ),
            ],
        )
    )

    print(f"Webset created with ID: {webset.id}")

    # Wait until Webset completes processing
    webset = exa.websets.wait_until_idle(webset.id)

    # Retrieve Webset Items
    items = exa.websets.items.list(webset_id=webset.id)
    for item in items.data:
        print(f"Item: {item.model_dump_json(indent=2)}")
    ```
  </Tab>

  <Tab title="JavaScript">
    Install the latest version of the JavaScript SDK with npm or pnpm:

    ```bash
    npm install exa-js
    ```

    Create a file called `webset.js` and add the code below:

    ```javascript javascript
    import * as dotenv from "dotenv";
    import Exa, { CreateWebsetParameters, CreateEnrichmentParameters } from "exa-js";

    // Load environment variables
    dotenv.config();

    async function main() {
      const exa = new Exa(process.env.EXA_API_KEY);

      try {
        // Create a Webset with search and enrichments
        const webset = await exa.websets.create({
          search: {
            query: "Top AI research labs focusing on large language models",
            count: 10
          },
          enrichments: [
            {
              description: "Estimate the company'\''s founding year",
              format: "number"
            }
          ],
        });

        console.log(`Webset created with ID: ${webset.id}`);

        // Wait until Webset completes processing
        const idleWebset = await exa.websets.waitUntilIdle(webset.id, {
          timeout: 60000,
          pollInterval: 2000,
          onPoll: (status) => console.log(`Current status: ${status}...`)
        });

        // Retrieve Webset Items
        const items = await exa.websets.items.list(webset.id, { limit: 10 });
        for (const item of items.data) {
          console.log(`Item: ${JSON.stringify(item, null, 2)}`);
        }
      } catch (error) {
        console.error("Error:", error);
      }
    }

    main();
    ```
  </Tab>

  <Tab title="cURL">
    Pass the following command to your terminal to create a Webset:

    ```bash bash
    curl --request POST \
      --url https://api.exa.ai/websets/v0/websets/ \
      --header 'accept: application/json' \
      --header 'content-type: application/json' \
      --header "x-api-key: ${EXA_API_KEY}" \
      --data '{
        "search": {
          "query": "Top AI research labs focusing on large language models",
          "count": 5
        },
        "enrichments": [
          {
            "description": "Find the company'\''s founding year",
            "format": "number"
          }
        ]
      }'
    ```

    To check the status of your Webset:

    ```bash bash
    curl --request GET \
      --url https://api.exa.ai/websets/v0/websets/{WEBSET_ID} \
      --header 'accept: application/json' \
      --header "x-api-key: ${EXA_API_KEY}"
    ```

    To list items in your Webset:

    ```bash bash
    curl --request GET \
      --url https://api.exa.ai/websets/v0/websets/{WEBSET_ID}/items \
      --header 'accept: application/json' \
      --header "x-api-key: ${EXA_API_KEY}"
    ```

    Or you can use the `expand` parameter to get the latest 100 within your Webset:

    ```bash bash
    curl --request GET \
      --url https://api.exa.ai/websets/v0/websets/{WEBSET_ID}?expand=items \
      --header 'accept: application/json' \
      --header "x-api-key: ${EXA_API_KEY}"
    ```
  </Tab>
</Tabs>

***

## What's next?

* Learn [how Websets work](/websets/api/how-it-works) and understand the event-driven process
* Configure [webhooks](/websets/api/webhooks) to receive real-time updates as items are added into your Websets
* Learn about [Enrichments](/websets/api/websets/enrichments) to extract specific data points
* See how to [Manage Items](/websets/api/websets/items) in your Webset


## Source: https://docs.exa.ai/websets/api/overview.md

# Overview

> The Websets API helps you find, verify, and process web data at scale to build your unique collection of web content.

The Websets API helps you create your own unique slice of the web by organizing content in containers (`Webset`). These containers store structured results (`WebsetItem`) which are discovered by search agents (`WebsetSearch`) that find web pages matching your specific criteria. Once these items are added to your Webset, they can be further processed with enrichment agents to extract additional data.

Whether you're looking for companies, people, or research papers, each result becomes a structured Item with source content, verification status, and type-specific fields. These Items can be further enriched with enrichments.

## Key Features

At its core, the API is:

* **Asynchronous**: It's an async-first API. Searches (`Webset Search`) can take from seconds to minutes, depending on the complexity.

* **Structured**: Every result (`Webset Item`) includes structured properties, webpage content, and verification against your criteria, with reasoning and references explaining why it matches.

* **Event-Driven**: Events are published and delivered through webhooks to notify when items are found and when enrichments complete, allowing you to process data as it arrives.

***

## Core Objects

<img src="https://mintlify.s3.us-west-1.amazonaws.com/exa-52/images/websets/api/core.png" alt="Core concepts diagram showing relationships between Webset, Search, Item and Enrichment objects" />

* **Webset**: Container that organizes your unique collection of web content and its related searches
* **Search**: An agent that searches and crawls the web to find precise entities matching your criteria, adding them to your Webset as structured WebsetItems
* **Item**: A structured result with source content, verification status, and type-specific fields (company, person, research paper, etc.)
* **Enrichment**: An agent that searches the web to enhance existing WebsetItems with additional structured data

## Next Steps

* Follow our [quickstart guide](/websets/api/get-started)
* Learn more about [how it works](/websets/api/how-it-works)
* Browse the [API reference](/websets/api/websets/create-a-webset)


## Source: https://docs.exa.ai/websets/api/websets/create-a-webset.md

# Create a Webset

## OpenAPI

````yaml post /v0/websets
paths:
  path: /v0/websets
  method: post
  servers:
    - url: https://api.exa.ai/websets/
      description: Production
  request:
    security:
      - title: api key
        parameters:
          query: {}
          header:
            x-api-key:
              type: apiKey
              description: Your Exa API key
          cookie: {}
    parameters:
      path: {}
      query: {}
      header: {}
      cookie: {}
    body:
      application/json:
        schemaArray:
          - type: object
            properties:
              search:
                allOf:
                  - type:
                      - object
                    properties:
                      query:
                        type:
                          - string
                        minLength: 1
                        maxLength: 5000
                        description: >-
                          Your search query.


                          Use this to describe what you are looking for.


                          Any URL provided will be crawled and used as context
                          for the search.
                        examples:
                          - >-
                            Marketing agencies based in the US, that focus on
                            consumer products.
                      count:
                        default: 10
                        type:
                          - number
                        minimum: 1
                        description: >-
                          Number of Items the Webset will attempt to find.


                          The actual number of Items found may be less than this
                          number depending on the search complexity.
                      entity:
                        $ref: '#/components/schemas/WebsetEntity'
                        description: >-
                          Entity the Webset will return results for.


                          It is not required to provide it, we automatically
                          detect the entity from all the information provided in
                          the query. Only use this when you need more fine
                          control.
                      criteria:
                        type:
                          - array
                        items:
                          type:
                            - object
                          $ref: '#/components/schemas/CreateCriterionParameters'
                          title: CreateCriterionParameters
                        minItems: 1
                        maxItems: 5
                        description: >-
                          Criteria every item is evaluated against.


                          It's not required to provide your own criteria, we
                          automatically detect the criteria from all the
                          information provided in the query. Only use this when
                          you need more fine control.
                    required:
                      - query
                    description: Create initial search for the Webset.
              enrichments:
                allOf:
                  - type:
                      - array
                    items:
                      type:
                        - object
                      $ref: '#/components/schemas/CreateEnrichmentParameters'
                      title: CreateEnrichmentParameters
                    maxItems: 10
                    description: Add Enrichments for the Webset.
              externalId:
                allOf:
                  - type:
                      - string
                    description: >-
                      The external identifier for the webset.


                      You can use this to reference the Webset by your own
                      internal identifiers.
              metadata:
                allOf:
                  - description: >-
                      Set of key-value pairs you want to associate with this
                      object.
                    type:
                      - object
                    additionalProperties:
                      type:
                        - string
                      maxLength: 1000
            required: true
            refIdentifier: '#/components/schemas/CreateWebsetParameters'
            examples:
              - search: &ref_0
                  query: >-
                    Marketing agencies based in the US, that focus on consumer
                    products.
                  count: 10
            requiredProperties:
              - search
            example:
              search: *ref_0
        examples:
          example:
            value:
              search:
                query: >-
                  Marketing agencies based in the US, that focus on consumer
                  products.
                count: 10
  response:
    '201':
      application/json:
        schemaArray:
          - type: object
            properties:
              id:
                allOf:
                  - type:
                      - string
                    description: The unique identifier for the webset
              object:
                allOf:
                  - type: string
                    const: webset
                    default: webset
              status:
                allOf:
                  - type:
                      - string
                    enum:
                      - idle
                      - running
                      - paused
                    description: The status of the webset
                    title: WebsetStatus
              externalId:
                allOf:
                  - type: string
                    description: The external identifier for the webset
                    nullable: true
              searches:
                allOf:
                  - type:
                      - array
                    items:
                      type:
                        - object
                      $ref: '#/components/schemas/WebsetSearch'
                    description: The searches that have been performed on the webset.
              enrichments:
                allOf:
                  - type:
                      - array
                    items:
                      type:
                        - object
                      $ref: '#/components/schemas/WebsetEnrichment'
                    description: The Enrichments to apply to the Webset Items.
              metadata:
                allOf:
                  - default: {}
                    description: >-
                      Set of key-value pairs you want to associate with this
                      object.
                    type:
                      - object
                    additionalProperties:
                      type:
                        - string
                      maxLength: 1000
              createdAt:
                allOf:
                  - type:
                      - string
                    format: date-time
                    description: The date and time the webset was created
              updatedAt:
                allOf:
                  - type:
                      - string
                    format: date-time
                    description: The date and time the webset was updated
            refIdentifier: '#/components/schemas/Webset'
            requiredProperties:
              - id
              - object
              - status
              - externalId
              - searches
              - enrichments
              - createdAt
              - updatedAt
        examples:
          example:
            value:
              id: <string>
              object: webset
              status: idle
              externalId: <string>
              searches:
                - id: <string>
                  object: webset_search
                  status: created
                  query: <string>
                  entity:
                    type: company
                  criteria:
                    - description: <string>
                      successRate: 50
                  count: 2
                  progress:
                    found: 123
                    completion: 50
                  metadata: {}
                  canceledAt: '2023-11-07T05:31:56Z'
                  canceledReason: webset_deleted
                  createdAt: '2023-11-07T05:31:56Z'
                  updatedAt: '2023-11-07T05:31:56Z'
              enrichments:
                - id: <string>
                  object: webset_enrichment
                  status: pending
                  websetId: <string>
                  title: <string>
                  description: <string>
                  format: text
                  options:
                    - label: <string>
                  instructions: <string>
                  metadata: {}
                  createdAt: '2023-11-07T05:31:56Z'
                  updatedAt: '2023-11-07T05:31:56Z'
              metadata: {}
              createdAt: '2023-11-07T05:31:56Z'
              updatedAt: '2023-11-07T05:31:56Z'
        description: Webset created
    '409':
      _mintlify/placeholder:
        schemaArray:
          - type: any
            description: Webset with this externalId already exists
        examples: {}
        description: Webset with this externalId already exists
  deprecated: false
  type: path
components:
  schemas:
    WebsetCompanyEntity:
      type:
        - object
      properties:
        type:
          type: string
          const: company
          default: company
      required:
        - type
    WebsetPersonEntity:
      type:
        - object
      properties:
        type:
          type: string
          const: person
          default: person
      required:
        - type
    WebsetArticleEntity:
      type:
        - object
      properties:
        type:
          type: string
          const: article
          default: article
      required:
        - type
    WebsetResearchPaperEntity:
      type:
        - object
      properties:
        type:
          type: string
          const: research_paper
          default: research_paper
      required:
        - type
    WebsetCustomEntity:
      type:
        - object
      properties:
        type:
          type: string
          const: custom
          default: custom
        description:
          type:
            - string
          minLength: 2
          maxLength: 200
          description: >-
            When you decide to use a custom entity, this is the description of
            the entity.


            The entity represents what type of results the Webset will return.
            For example, if you want results to be Job Postings, you might use
            "Job Postings" as the entity description.
      required:
        - type
        - description
    WebsetEntity:
      oneOf:
        - type:
            - object
          $ref: '#/components/schemas/WebsetCompanyEntity'
        - type:
            - object
          $ref: '#/components/schemas/WebsetPersonEntity'
        - type:
            - object
          $ref: '#/components/schemas/WebsetArticleEntity'
        - type:
            - object
          $ref: '#/components/schemas/WebsetResearchPaperEntity'
        - type:
            - object
          $ref: '#/components/schemas/WebsetCustomEntity'
    CreateCriterionParameters:
      type:
        - object
      properties:
        description:
          type:
            - string
          minLength: 1
          maxLength: 300
          description: The description of the criterion
      required:
        - description
    CreateEnrichmentParameters:
      type:
        - object
      properties:
        description:
          type:
            - string
          minLength: 1
          maxLength: 5000
          description: >-
            Provide a description of the enrichment task you want to perform to
            each Webset Item.
        format:
          type:
            - string
          enum:
            - text
            - date
            - number
            - options
            - email
            - phone
          description: >-
            Format of the enrichment response.


            We automatically select the best format based on the description. If
            you want to explicitly specify the format, you can do so here.
        options:
          type:
            - array
          items:
            type:
              - object
            properties:
              label:
                type:
                  - string
                description: The label of the option
            required:
              - label
          minItems: 1
          maxItems: 20
          description: >-
            When the format is options, the different options for the enrichment
            agent to choose from.
        metadata:
          description: Set of key-value pairs you want to associate with this object.
          type:
            - object
          additionalProperties:
            type:
              - string
            maxLength: 1000
      required:
        - description
    WebsetSearch:
      type:
        - object
      properties:
        id:
          type:
            - string
          description: The unique identifier for the search
        object:
          type: string
          const: webset_search
          default: webset_search
        status:
          type:
            - string
          enum:
            - created
            - running
            - completed
            - canceled
          description: The status of the search
          title: WebsetSearchStatus
        query:
          type:
            - string
          minLength: 1
          maxLength: 5000
          description: The query used to create the search.
        entity:
          $ref: '#/components/schemas/WebsetEntity'
          description: >-
            The entity the search will return results for.


            When no entity is provided during creation, we will automatically
            select the best entity based on the query.
          nullable: true
        criteria:
          type:
            - array
          items:
            type:
              - object
            properties:
              description:
                type:
                  - string
                minLength: 1
                maxLength: 300
                description: The description of the criterion
              successRate:
                type:
                  - number
                minimum: 0
                maximum: 100
                description: >-
                  Value between 0 and 100 representing the percentage of results
                  that meet the criterion.
            required:
              - description
              - successRate
          description: >-
            The criteria the search will use to evaluate the results. If not
            provided, we will automatically generate them for you.
        count:
          type:
            - number
          minimum: 1
          description: >-
            The number of results the search will attempt to find. The actual
            number of results may be less than this number depending on the
            search complexity.
        progress:
          type:
            - object
          properties:
            found:
              type:
                - number
              description: The number of results found so far
            completion:
              type:
                - number
              minimum: 0
              maximum: 100
              description: The completion percentage of the search
          required:
            - found
            - completion
          description: The progress of the search
        metadata:
          default: {}
          description: Set of key-value pairs you want to associate with this object.
          type:
            - object
          additionalProperties:
            type:
              - string
            maxLength: 1000
        canceledAt:
          type: string
          format: date-time
          description: The date and time the search was canceled
          nullable: true
        canceledReason:
          type: string
          enum:
            - webset_deleted
            - webset_canceled
          description: The reason the search was canceled
          nullable: true
        createdAt:
          type:
            - string
          format: date-time
          description: The date and time the search was created
        updatedAt:
          type:
            - string
          format: date-time
          description: The date and time the search was updated
      required:
        - id
        - object
        - status
        - query
        - entity
        - criteria
        - count
        - progress
        - canceledAt
        - canceledReason
        - createdAt
        - updatedAt
    WebsetEnrichment:
      type:
        - object
      properties:
        id:
          type:
            - string
          description: The unique identifier for the enrichment
        object:
          type: string
          const: webset_enrichment
          default: webset_enrichment
        status:
          type:
            - string
          enum:
            - pending
            - canceled
            - completed
          description: The status of the enrichment
          title: WebsetEnrichmentStatus
        websetId:
          type:
            - string
          description: The unique identifier for the Webset this enrichment belongs to.
        title:
          type: string
          description: >-
            The title of the enrichment.


            This will be automatically generated based on the description and
            format.
          nullable: true
        description:
          type:
            - string
          description: >-
            The description of the enrichment task provided during the creation
            of the enrichment.
        format:
          type: string
          $ref: '#/components/schemas/WebsetEnrichmentFormat'
          description: The format of the enrichment response.
          nullable: true
        options:
          type: array
          items:
            type:
              - object
            properties:
              label:
                type:
                  - string
                description: The label of the option
            required:
              - label
          description: >-
            When the format is options, the different options for the enrichment
            agent to choose from.
          title: WebsetEnrichmentOptions
          nullable: true
        instructions:
          type: string
          description: >-
            The instructions for the enrichment Agent.


            This will be automatically generated based on the description and
            format.
          nullable: true
        metadata:
          default: {}
          description: The metadata of the enrichment
          type:
            - object
          additionalProperties:
            type:
              - string
            maxLength: 1000
        createdAt:
          type:
            - string
          format: date-time
          description: The date and time the enrichment was created
        updatedAt:
          type:
            - string
          format: date-time
          description: The date and time the enrichment was updated
      required:
        - id
        - object
        - status
        - websetId
        - title
        - description
        - format
        - options
        - instructions
        - createdAt
        - updatedAt
    WebsetEnrichmentFormat:
      type: string
      enum:
        - text
        - date
        - number
        - options
        - email
        - phone

````

## Source: https://docs.exa.ai/websets/api/websets/get-a-webset.md

# Get a Webset

## OpenAPI

````yaml get /v0/websets/{id}
paths:
  path: /v0/websets/{id}
  method: get
  servers:
    - url: https://api.exa.ai/websets/
      description: Production
  request:
    security:
      - title: api key
        parameters:
          query: {}
          header:
            x-api-key:
              type: apiKey
              description: Your Exa API key
          cookie: {}
    parameters:
      path:
        id:
          schema:
            - type: string
              required: true
              description: The id or externalId of the Webset.
      query:
        expand:
          schema:
            - type: array
              items:
                allOf:
                  - type: string
                    enum:
                      - items
              required: false
              description: Expand the response with the specified resources
      header: {}
      cookie: {}
    body: {}
  response:
    '200':
      application/json:
        schemaArray:
          - type: object
            properties:
              id:
                allOf:
                  - type:
                      - string
                    description: The unique identifier for the webset
              object:
                allOf:
                  - type: string
                    const: webset
                    default: webset
              status:
                allOf:
                  - type:
                      - string
                    enum:
                      - idle
                      - running
                      - paused
                    description: The status of the webset
                    title: WebsetStatus
              externalId:
                allOf:
                  - type: string
                    description: The external identifier for the webset
                    nullable: true
              searches:
                allOf:
                  - type:
                      - array
                    items:
                      type:
                        - object
                      $ref: '#/components/schemas/WebsetSearch'
                    description: The searches that have been performed on the webset.
              enrichments:
                allOf:
                  - type:
                      - array
                    items:
                      type:
                        - object
                      $ref: '#/components/schemas/WebsetEnrichment'
                    description: The Enrichments to apply to the Webset Items.
              metadata:
                allOf:
                  - default: {}
                    description: >-
                      Set of key-value pairs you want to associate with this
                      object.
                    type:
                      - object
                    additionalProperties:
                      type:
                        - string
                      maxLength: 1000
              createdAt:
                allOf:
                  - type:
                      - string
                    format: date-time
                    description: The date and time the webset was created
              updatedAt:
                allOf:
                  - type:
                      - string
                    format: date-time
                    description: The date and time the webset was updated
              items:
                allOf:
                  - type:
                      - array
                    items:
                      type:
                        - object
                      $ref: '#/components/schemas/WebsetItem'
                    description: >-
                      When expand query parameter contains `items`, this will
                      contain the items in the webset
            refIdentifier: '#/components/schemas/GetWebsetResponse'
            requiredProperties:
              - id
              - object
              - status
              - externalId
              - searches
              - enrichments
              - createdAt
              - updatedAt
        examples:
          example:
            value:
              id: <string>
              object: webset
              status: idle
              externalId: <string>
              searches:
                - id: <string>
                  object: webset_search
                  status: created
                  query: <string>
                  entity:
                    type: company
                  criteria:
                    - description: <string>
                      successRate: 50
                  count: 2
                  progress:
                    found: 123
                    completion: 50
                  metadata: {}
                  canceledAt: '2023-11-07T05:31:56Z'
                  canceledReason: webset_deleted
                  createdAt: '2023-11-07T05:31:56Z'
                  updatedAt: '2023-11-07T05:31:56Z'
              enrichments:
                - id: <string>
                  object: webset_enrichment
                  status: pending
                  websetId: <string>
                  title: <string>
                  description: <string>
                  format: text
                  options:
                    - label: <string>
                  instructions: <string>
                  metadata: {}
                  createdAt: '2023-11-07T05:31:56Z'
                  updatedAt: '2023-11-07T05:31:56Z'
              metadata: {}
              createdAt: '2023-11-07T05:31:56Z'
              updatedAt: '2023-11-07T05:31:56Z'
              items:
                - id: <string>
                  object: webset_item
                  source: search
                  sourceId: <string>
                  websetId: <string>
                  properties:
                    type: person
                    url: <string>
                    description: <string>
                    person:
                      name: <string>
                      location: <string>
                      position: <string>
                      pictureUrl: <string>
                  evaluations:
                    - criterion: <string>
                      reasoning: <string>
                      satisfied: 'yes'
                      references: []
                  enrichments:
                    - object: enrichment_result
                      format: text
                      result:
                        - <string>
                      reasoning: <string>
                      references:
                        - title: <string>
                          snippet: <string>
                          url: <string>
                      enrichmentId: <string>
                  createdAt: '2023-11-07T05:31:56Z'
                  updatedAt: '2023-11-07T05:31:56Z'
        description: Webset
    '404':
      _mintlify/placeholder:
        schemaArray:
          - type: any
            description: Webset not found
        examples: {}
        description: Webset not found
  deprecated: false
  type: path
components:
  schemas:
    WebsetCompanyEntity:
      type:
        - object
      properties:
        type:
          type: string
          const: company
          default: company
      required:
        - type
    WebsetPersonEntity:
      type:
        - object
      properties:
        type:
          type: string
          const: person
          default: person
      required:
        - type
    WebsetArticleEntity:
      type:
        - object
      properties:
        type:
          type: string
          const: article
          default: article
      required:
        - type
    WebsetResearchPaperEntity:
      type:
        - object
      properties:
        type:
          type: string
          const: research_paper
          default: research_paper
      required:
        - type
    WebsetCustomEntity:
      type:
        - object
      properties:
        type:
          type: string
          const: custom
          default: custom
        description:
          type:
            - string
          minLength: 2
          maxLength: 200
          description: >-
            When you decide to use a custom entity, this is the description of
            the entity.


            The entity represents what type of results the Webset will return.
            For example, if you want results to be Job Postings, you might use
            "Job Postings" as the entity description.
      required:
        - type
        - description
    WebsetEntity:
      oneOf:
        - type:
            - object
          $ref: '#/components/schemas/WebsetCompanyEntity'
        - type:
            - object
          $ref: '#/components/schemas/WebsetPersonEntity'
        - type:
            - object
          $ref: '#/components/schemas/WebsetArticleEntity'
        - type:
            - object
          $ref: '#/components/schemas/WebsetResearchPaperEntity'
        - type:
            - object
          $ref: '#/components/schemas/WebsetCustomEntity'
    WebsetSearch:
      type:
        - object
      properties:
        id:
          type:
            - string
          description: The unique identifier for the search
        object:
          type: string
          const: webset_search
          default: webset_search
        status:
          type:
            - string
          enum:
            - created
            - running
            - completed
            - canceled
          description: The status of the search
          title: WebsetSearchStatus
        query:
          type:
            - string
          minLength: 1
          maxLength: 5000
          description: The query used to create the search.
        entity:
          $ref: '#/components/schemas/WebsetEntity'
          description: >-
            The entity the search will return results for.


            When no entity is provided during creation, we will automatically
            select the best entity based on the query.
          nullable: true
        criteria:
          type:
            - array
          items:
            type:
              - object
            properties:
              description:
                type:
                  - string
                minLength: 1
                maxLength: 300
                description: The description of the criterion
              successRate:
                type:
                  - number
                minimum: 0
                maximum: 100
                description: >-
                  Value between 0 and 100 representing the percentage of results
                  that meet the criterion.
            required:
              - description
              - successRate
          description: >-
            The criteria the search will use to evaluate the results. If not
            provided, we will automatically generate them for you.
        count:
          type:
            - number
          minimum: 1
          description: >-
            The number of results the search will attempt to find. The actual
            number of results may be less than this number depending on the
            search complexity.
        progress:
          type:
            - object
          properties:
            found:
              type:
                - number
              description: The number of results found so far
            completion:
              type:
                - number
              minimum: 0
              maximum: 100
              description: The completion percentage of the search
          required:
            - found
            - completion
          description: The progress of the search
        metadata:
          default: {}
          description: Set of key-value pairs you want to associate with this object.
          type:
            - object
          additionalProperties:
            type:
              - string
            maxLength: 1000
        canceledAt:
          type: string
          format: date-time
          description: The date and time the search was canceled
          nullable: true
        canceledReason:
          type: string
          enum:
            - webset_deleted
            - webset_canceled
          description: The reason the search was canceled
          nullable: true
        createdAt:
          type:
            - string
          format: date-time
          description: The date and time the search was created
        updatedAt:
          type:
            - string
          format: date-time
          description: The date and time the search was updated
      required:
        - id
        - object
        - status
        - query
        - entity
        - criteria
        - count
        - progress
        - canceledAt
        - canceledReason
        - createdAt
        - updatedAt
    WebsetEnrichment:
      type:
        - object
      properties:
        id:
          type:
            - string
          description: The unique identifier for the enrichment
        object:
          type: string
          const: webset_enrichment
          default: webset_enrichment
        status:
          type:
            - string
          enum:
            - pending
            - canceled
            - completed
          description: The status of the enrichment
          title: WebsetEnrichmentStatus
        websetId:
          type:
            - string
          description: The unique identifier for the Webset this enrichment belongs to.
        title:
          type: string
          description: >-
            The title of the enrichment.


            This will be automatically generated based on the description and
            format.
          nullable: true
        description:
          type:
            - string
          description: >-
            The description of the enrichment task provided during the creation
            of the enrichment.
        format:
          type: string
          $ref: '#/components/schemas/WebsetEnrichmentFormat'
          description: The format of the enrichment response.
          nullable: true
        options:
          type: array
          items:
            type:
              - object
            properties:
              label:
                type:
                  - string
                description: The label of the option
            required:
              - label
          description: >-
            When the format is options, the different options for the enrichment
            agent to choose from.
          title: WebsetEnrichmentOptions
          nullable: true
        instructions:
          type: string
          description: >-
            The instructions for the enrichment Agent.


            This will be automatically generated based on the description and
            format.
          nullable: true
        metadata:
          default: {}
          description: The metadata of the enrichment
          type:
            - object
          additionalProperties:
            type:
              - string
            maxLength: 1000
        createdAt:
          type:
            - string
          format: date-time
          description: The date and time the enrichment was created
        updatedAt:
          type:
            - string
          format: date-time
          description: The date and time the enrichment was updated
      required:
        - id
        - object
        - status
        - websetId
        - title
        - description
        - format
        - options
        - instructions
        - createdAt
        - updatedAt
    WebsetItemPersonProperties:
      type:
        - object
      properties:
        type:
          type: string
          const: person
          default: person
        url:
          type:
            - string
          format: uri
          description: The URL of the person profile
        description:
          type:
            - string
          description: Short description of the relevance of the person
        person:
          type:
            - object
          properties:
            name:
              type:
                - string
              description: The name of the person
            location:
              type: string
              description: The location of the person
              nullable: true
            position:
              type: string
              description: The current work position of the person
              nullable: true
            pictureUrl:
              type: string
              format: uri
              description: The image URL of the person
              nullable: true
          required:
            - name
            - location
            - position
            - pictureUrl
          title: WebsetItemPersonPropertiesFields
      required:
        - type
        - url
        - description
        - person
    WebsetItemCompanyProperties:
      type:
        - object
      properties:
        type:
          type: string
          const: company
          default: company
        url:
          type:
            - string
          format: uri
          description: The URL of the company website
        description:
          type:
            - string
          description: Short description of the relevance of the company
        content:
          type: string
          description: The text content of the company website
          nullable: true
        company:
          type:
            - object
          properties:
            name:
              type:
                - string
              description: The name of the company
            location:
              type: string
              description: The main location of the company
              nullable: true
            employees:
              type: number
              description: The number of employees of the company
              nullable: true
            industry:
              type: string
              description: The industry of the company
              nullable: true
            about:
              type: string
              description: A short description of the company
              nullable: true
            logoUrl:
              type: string
              format: uri
              description: The logo URL of the company
              nullable: true
          required:
            - name
            - location
            - employees
            - industry
            - about
            - logoUrl
          title: WebsetItemCompanyPropertiesFields
      required:
        - type
        - url
        - description
        - content
        - company
    WebsetItemArticleProperties:
      type:
        - object
      properties:
        type:
          type: string
          const: article
          default: article
        url:
          type:
            - string
          format: uri
          description: The URL of the article
        description:
          type:
            - string
          description: Short description of the relevance of the article
        content:
          type: string
          description: The text content for the article
          nullable: true
        article:
          type:
            - object
          properties:
            author:
              type: string
              description: The author(s) of the article
              nullable: true
            publishedAt:
              type: string
              description: The date and time the article was published
              nullable: true
          required:
            - author
            - publishedAt
          title: WebsetItemArticlePropertiesFields
      required:
        - type
        - url
        - description
        - content
        - article
    WebsetItemResearchPaperProperties:
      type:
        - object
      properties:
        type:
          type: string
          const: research_paper
          default: research_paper
        url:
          type:
            - string
          format: uri
          description: The URL of the research paper
        description:
          type:
            - string
          description: Short description of the relevance of the research paper
        content:
          type: string
          description: The text content of the research paper
          nullable: true
        researchPaper:
          type:
            - object
          properties:
            author:
              type: string
              description: The author(s) of the research paper
              nullable: true
            publishedAt:
              type: string
              description: The date and time the research paper was published
              nullable: true
          required:
            - author
            - publishedAt
          title: WebsetItemResearchPaperPropertiesFields
      required:
        - type
        - url
        - description
        - content
        - researchPaper
    WebsetItemCustomProperties:
      type:
        - object
      properties:
        type:
          type: string
          const: custom
          default: custom
        url:
          type:
            - string
          format: uri
          description: The URL of the Item
        description:
          type:
            - string
          description: Short description of the Item
        content:
          type: string
          description: The text content of the Item
          nullable: true
        custom:
          type:
            - object
          properties:
            author:
              type: string
              description: The author(s) of the website
              nullable: true
            publishedAt:
              type: string
              description: The date and time the website was published
              nullable: true
          required:
            - author
            - publishedAt
          title: WebsetItemCustomPropertiesFields
      required:
        - type
        - url
        - description
        - content
        - custom
    WebsetItemEvaluation:
      type:
        - object
      properties:
        criterion:
          type:
            - string
          description: The description of the criterion
        reasoning:
          type:
            - string
          description: The reasoning for the result of the evaluation
        satisfied:
          type:
            - string
          enum:
            - 'yes'
            - 'no'
            - unclear
          description: The satisfaction of the criterion
        references:
          default: []
          type:
            - array
          items:
            type:
              - object
            properties:
              title:
                type: string
                description: The title of the reference
                nullable: true
              snippet:
                type: string
                description: The relevant snippet of the reference content
                nullable: true
              url:
                description: The URL of the reference
                type:
                  - string
            required:
              - title
              - snippet
              - url
          description: The references used to generate the result.
      required:
        - criterion
        - reasoning
        - satisfied
    EnrichmentResult:
      type:
        - object
      properties:
        object:
          type: string
          const: enrichment_result
          default: enrichment_result
        format:
          type:
            - string
          $ref: '#/components/schemas/WebsetEnrichmentFormat'
        result:
          type: array
          items:
            type:
              - string
          description: The result of the enrichment.
          nullable: true
        reasoning:
          type: string
          description: The reasoning for the result when an Agent is used.
          nullable: true
        references:
          type:
            - array
          items:
            type:
              - object
            properties:
              title:
                type: string
                description: The title of the reference
                nullable: true
              snippet:
                type: string
                description: The relevant snippet of the reference content
                nullable: true
              url:
                description: The URL of the reference
                type:
                  - string
            required:
              - title
              - snippet
              - url
          description: The references used to generate the result.
        enrichmentId:
          type:
            - string
          description: The id of the Enrichment that generated the result
      required:
        - object
        - format
        - result
        - reasoning
        - references
        - enrichmentId
    WebsetItem:
      type:
        - object
      properties:
        id:
          type:
            - string
          description: The unique identifier for the Webset Item
        object:
          type: string
          const: webset_item
          default: webset_item
        source:
          type:
            - string
          enum:
            - search
          description: The source of the Item
        sourceId:
          type:
            - string
          description: The unique identifier for the source
        websetId:
          type:
            - string
          description: The unique identifier for the Webset this Item belongs to.
        properties:
          oneOf:
            - type:
                - object
              $ref: '#/components/schemas/WebsetItemPersonProperties'
              title: WebsetItemPropertiesPerson
            - type:
                - object
              $ref: '#/components/schemas/WebsetItemCompanyProperties'
              title: WebsetItemPropertiesCompany
            - type:
                - object
              $ref: '#/components/schemas/WebsetItemArticleProperties'
              title: WebsetItemPropertiesArticle
            - type:
                - object
              $ref: '#/components/schemas/WebsetItemResearchPaperProperties'
              title: WebsetItemPropertiesResearchPaper
            - type:
                - object
              $ref: '#/components/schemas/WebsetItemCustomProperties'
              title: WebsetItemPropertiesCustom
          description: The properties of the Item
        evaluations:
          type:
            - array
          items:
            type:
              - object
            $ref: '#/components/schemas/WebsetItemEvaluation'
          description: The criteria evaluations of the item
        enrichments:
          type: array
          items:
            type:
              - object
            $ref: '#/components/schemas/EnrichmentResult'
          description: The enrichments results of the Webset item
          nullable: true
        createdAt:
          type:
            - string
          format: date-time
          description: The date and time the item was created
        updatedAt:
          type:
            - string
          format: date-time
          description: The date and time the item was last updated
      required:
        - id
        - object
        - source
        - sourceId
        - websetId
        - properties
        - evaluations
        - enrichments
        - createdAt
        - updatedAt
    WebsetEnrichmentFormat:
      type: string
      enum:
        - text
        - date
        - number
        - options
        - email
        - phone

````

## Source: https://docs.exa.ai/websets/api/websets/update-a-webset.md

# Update a Webset

## OpenAPI

````yaml post /v0/websets/{id}
paths:
  path: /v0/websets/{id}
  method: post
  servers:
    - url: https://api.exa.ai/websets/
      description: Production
  request:
    security:
      - title: api key
        parameters:
          query: {}
          header:
            x-api-key:
              type: apiKey
              description: Your Exa API key
          cookie: {}
    parameters:
      path:
        id:
          schema:
            - type: string
              required: true
              description: The id or externalId of the Webset
      query: {}
      header: {}
      cookie: {}
    body:
      application/json:
        schemaArray:
          - type: object
            properties:
              metadata:
                allOf:
                  - description: >-
                      Set of key-value pairs you want to associate with this
                      object.
                    type: object
                    additionalProperties:
                      type:
                        - string
                      maxLength: 1000
                    nullable: true
            required: true
            refIdentifier: '#/components/schemas/UpdateWebsetRequest'
        examples:
          example:
            value:
              metadata: {}
  response:
    '200':
      application/json:
        schemaArray:
          - type: object
            properties:
              id:
                allOf:
                  - type:
                      - string
                    description: The unique identifier for the webset
              object:
                allOf:
                  - type: string
                    const: webset
                    default: webset
              status:
                allOf:
                  - type:
                      - string
                    enum:
                      - idle
                      - running
                      - paused
                    description: The status of the webset
                    title: WebsetStatus
              externalId:
                allOf:
                  - type: string
                    description: The external identifier for the webset
                    nullable: true
              searches:
                allOf:
                  - type:
                      - array
                    items:
                      type:
                        - object
                      $ref: '#/components/schemas/WebsetSearch'
                    description: The searches that have been performed on the webset.
              enrichments:
                allOf:
                  - type:
                      - array
                    items:
                      type:
                        - object
                      $ref: '#/components/schemas/WebsetEnrichment'
                    description: The Enrichments to apply to the Webset Items.
              metadata:
                allOf:
                  - default: {}
                    description: >-
                      Set of key-value pairs you want to associate with this
                      object.
                    type:
                      - object
                    additionalProperties:
                      type:
                        - string
                      maxLength: 1000
              createdAt:
                allOf:
                  - type:
                      - string
                    format: date-time
                    description: The date and time the webset was created
              updatedAt:
                allOf:
                  - type:
                      - string
                    format: date-time
                    description: The date and time the webset was updated
            refIdentifier: '#/components/schemas/Webset'
            requiredProperties:
              - id
              - object
              - status
              - externalId
              - searches
              - enrichments
              - createdAt
              - updatedAt
        examples:
          example:
            value:
              id: <string>
              object: webset
              status: idle
              externalId: <string>
              searches:
                - id: <string>
                  object: webset_search
                  status: created
                  query: <string>
                  entity:
                    type: company
                  criteria:
                    - description: <string>
                      successRate: 50
                  count: 2
                  progress:
                    found: 123
                    completion: 50
                  metadata: {}
                  canceledAt: '2023-11-07T05:31:56Z'
                  canceledReason: webset_deleted
                  createdAt: '2023-11-07T05:31:56Z'
                  updatedAt: '2023-11-07T05:31:56Z'
              enrichments:
                - id: <string>
                  object: webset_enrichment
                  status: pending
                  websetId: <string>
                  title: <string>
                  description: <string>
                  format: text
                  options:
                    - label: <string>
                  instructions: <string>
                  metadata: {}
                  createdAt: '2023-11-07T05:31:56Z'
                  updatedAt: '2023-11-07T05:31:56Z'
              metadata: {}
              createdAt: '2023-11-07T05:31:56Z'
              updatedAt: '2023-11-07T05:31:56Z'
        description: Webset updated
    '404':
      _mintlify/placeholder:
        schemaArray:
          - type: any
            description: Webset not found
        examples: {}
        description: Webset not found
  deprecated: false
  type: path
components:
  schemas:
    WebsetCompanyEntity:
      type:
        - object
      properties:
        type:
          type: string
          const: company
          default: company
      required:
        - type
    WebsetPersonEntity:
      type:
        - object
      properties:
        type:
          type: string
          const: person
          default: person
      required:
        - type
    WebsetArticleEntity:
      type:
        - object
      properties:
        type:
          type: string
          const: article
          default: article
      required:
        - type
    WebsetResearchPaperEntity:
      type:
        - object
      properties:
        type:
          type: string
          const: research_paper
          default: research_paper
      required:
        - type
    WebsetCustomEntity:
      type:
        - object
      properties:
        type:
          type: string
          const: custom
          default: custom
        description:
          type:
            - string
          minLength: 2
          maxLength: 200
          description: >-
            When you decide to use a custom entity, this is the description of
            the entity.


            The entity represents what type of results the Webset will return.
            For example, if you want results to be Job Postings, you might use
            "Job Postings" as the entity description.
      required:
        - type
        - description
    WebsetEntity:
      oneOf:
        - type:
            - object
          $ref: '#/components/schemas/WebsetCompanyEntity'
        - type:
            - object
          $ref: '#/components/schemas/WebsetPersonEntity'
        - type:
            - object
          $ref: '#/components/schemas/WebsetArticleEntity'
        - type:
            - object
          $ref: '#/components/schemas/WebsetResearchPaperEntity'
        - type:
            - object
          $ref: '#/components/schemas/WebsetCustomEntity'
    WebsetSearch:
      type:
        - object
      properties:
        id:
          type:
            - string
          description: The unique identifier for the search
        object:
          type: string
          const: webset_search
          default: webset_search
        status:
          type:
            - string
          enum:
            - created
            - running
            - completed
            - canceled
          description: The status of the search
          title: WebsetSearchStatus
        query:
          type:
            - string
          minLength: 1
          maxLength: 5000
          description: The query used to create the search.
        entity:
          $ref: '#/components/schemas/WebsetEntity'
          description: >-
            The entity the search will return results for.


            When no entity is provided during creation, we will automatically
            select the best entity based on the query.
          nullable: true
        criteria:
          type:
            - array
          items:
            type:
              - object
            properties:
              description:
                type:
                  - string
                minLength: 1
                maxLength: 300
                description: The description of the criterion
              successRate:
                type:
                  - number
                minimum: 0
                maximum: 100
                description: >-
                  Value between 0 and 100 representing the percentage of results
                  that meet the criterion.
            required:
              - description
              - successRate
          description: >-
            The criteria the search will use to evaluate the results. If not
            provided, we will automatically generate them for you.
        count:
          type:
            - number
          minimum: 1
          description: >-
            The number of results the search will attempt to find. The actual
            number of results may be less than this number depending on the
            search complexity.
        progress:
          type:
            - object
          properties:
            found:
              type:
                - number
              description: The number of results found so far
            completion:
              type:
                - number
              minimum: 0
              maximum: 100
              description: The completion percentage of the search
          required:
            - found
            - completion
          description: The progress of the search
        metadata:
          default: {}
          description: Set of key-value pairs you want to associate with this object.
          type:
            - object
          additionalProperties:
            type:
              - string
            maxLength: 1000
        canceledAt:
          type: string
          format: date-time
          description: The date and time the search was canceled
          nullable: true
        canceledReason:
          type: string
          enum:
            - webset_deleted
            - webset_canceled
          description: The reason the search was canceled
          nullable: true
        createdAt:
          type:
            - string
          format: date-time
          description: The date and time the search was created
        updatedAt:
          type:
            - string
          format: date-time
          description: The date and time the search was updated
      required:
        - id
        - object
        - status
        - query
        - entity
        - criteria
        - count
        - progress
        - canceledAt
        - canceledReason
        - createdAt
        - updatedAt
    WebsetEnrichment:
      type:
        - object
      properties:
        id:
          type:
            - string
          description: The unique identifier for the enrichment
        object:
          type: string
          const: webset_enrichment
          default: webset_enrichment
        status:
          type:
            - string
          enum:
            - pending
            - canceled
            - completed
          description: The status of the enrichment
          title: WebsetEnrichmentStatus
        websetId:
          type:
            - string
          description: The unique identifier for the Webset this enrichment belongs to.
        title:
          type: string
          description: >-
            The title of the enrichment.


            This will be automatically generated based on the description and
            format.
          nullable: true
        description:
          type:
            - string
          description: >-
            The description of the enrichment task provided during the creation
            of the enrichment.
        format:
          type: string
          $ref: '#/components/schemas/WebsetEnrichmentFormat'
          description: The format of the enrichment response.
          nullable: true
        options:
          type: array
          items:
            type:
              - object
            properties:
              label:
                type:
                  - string
                description: The label of the option
            required:
              - label
          description: >-
            When the format is options, the different options for the enrichment
            agent to choose from.
          title: WebsetEnrichmentOptions
          nullable: true
        instructions:
          type: string
          description: >-
            The instructions for the enrichment Agent.


            This will be automatically generated based on the description and
            format.
          nullable: true
        metadata:
          default: {}
          description: The metadata of the enrichment
          type:
            - object
          additionalProperties:
            type:
              - string
            maxLength: 1000
        createdAt:
          type:
            - string
          format: date-time
          description: The date and time the enrichment was created
        updatedAt:
          type:
            - string
          format: date-time
          description: The date and time the enrichment was updated
      required:
        - id
        - object
        - status
        - websetId
        - title
        - description
        - format
        - options
        - instructions
        - createdAt
        - updatedAt
    WebsetEnrichmentFormat:
      type: string
      enum:
        - text
        - date
        - number
        - options
        - email
        - phone

````

## Source: https://docs.exa.ai/websets/api/websets/delete-a-webset.md

# Delete a Webset

> Deletes a Webset.

Once deleted, the Webset and all its Items will no longer be available.

## OpenAPI

````yaml delete /v0/websets/{id}
paths:
  path: /v0/websets/{id}
  method: delete
  servers:
    - url: https://api.exa.ai/websets/
      description: Production
  request:
    security:
      - title: api key
        parameters:
          query: {}
          header:
            x-api-key:
              type: apiKey
              description: Your Exa API key
          cookie: {}
    parameters:
      path:
        id:
          schema:
            - type: string
              required: true
              description: The id or externalId of the Webset
      query: {}
      header: {}
      cookie: {}
    body: {}
  response:
    '200':
      application/json:
        schemaArray:
          - type: object
            properties:
              id:
                allOf:
                  - type:
                      - string
                    description: The unique identifier for the webset
              object:
                allOf:
                  - type: string
                    const: webset
                    default: webset
              status:
                allOf:
                  - type:
                      - string
                    enum:
                      - idle
                      - running
                      - paused
                    description: The status of the webset
                    title: WebsetStatus
              externalId:
                allOf:
                  - type: string
                    description: The external identifier for the webset
                    nullable: true
              searches:
                allOf:
                  - type:
                      - array
                    items:
                      type:
                        - object
                      $ref: '#/components/schemas/WebsetSearch'
                    description: The searches that have been performed on the webset.
              enrichments:
                allOf:
                  - type:
                      - array
                    items:
                      type:
                        - object
                      $ref: '#/components/schemas/WebsetEnrichment'
                    description: The Enrichments to apply to the Webset Items.
              metadata:
                allOf:
                  - default: {}
                    description: >-
                      Set of key-value pairs you want to associate with this
                      object.
                    type:
                      - object
                    additionalProperties:
                      type:
                        - string
                      maxLength: 1000
              createdAt:
                allOf:
                  - type:
                      - string
                    format: date-time
                    description: The date and time the webset was created
              updatedAt:
                allOf:
                  - type:
                      - string
                    format: date-time
                    description: The date and time the webset was updated
            refIdentifier: '#/components/schemas/Webset'
            requiredProperties:
              - id
              - object
              - status
              - externalId
              - searches
              - enrichments
              - createdAt
              - updatedAt
        examples:
          example:
            value:
              id: <string>
              object: webset
              status: idle
              externalId: <string>
              searches:
                - id: <string>
                  object: webset_search
                  status: created
                  query: <string>
                  entity:
                    type: company
                  criteria:
                    - description: <string>
                      successRate: 50
                  count: 2
                  progress:
                    found: 123
                    completion: 50
                  metadata: {}
                  canceledAt: '2023-11-07T05:31:56Z'
                  canceledReason: webset_deleted
                  createdAt: '2023-11-07T05:31:56Z'
                  updatedAt: '2023-11-07T05:31:56Z'
              enrichments:
                - id: <string>
                  object: webset_enrichment
                  status: pending
                  websetId: <string>
                  title: <string>
                  description: <string>
                  format: text
                  options:
                    - label: <string>
                  instructions: <string>
                  metadata: {}
                  createdAt: '2023-11-07T05:31:56Z'
                  updatedAt: '2023-11-07T05:31:56Z'
              metadata: {}
              createdAt: '2023-11-07T05:31:56Z'
              updatedAt: '2023-11-07T05:31:56Z'
        description: Webset deleted
    '404':
      _mintlify/placeholder:
        schemaArray:
          - type: any
            description: Webset not found
        examples: {}
        description: Webset not found
  deprecated: false
  type: path
components:
  schemas:
    WebsetCompanyEntity:
      type:
        - object
      properties:
        type:
          type: string
          const: company
          default: company
      required:
        - type
    WebsetPersonEntity:
      type:
        - object
      properties:
        type:
          type: string
          const: person
          default: person
      required:
        - type
    WebsetArticleEntity:
      type:
        - object
      properties:
        type:
          type: string
          const: article
          default: article
      required:
        - type
    WebsetResearchPaperEntity:
      type:
        - object
      properties:
        type:
          type: string
          const: research_paper
          default: research_paper
      required:
        - type
    WebsetCustomEntity:
      type:
        - object
      properties:
        type:
          type: string
          const: custom
          default: custom
        description:
          type:
            - string
          minLength: 2
          maxLength: 200
          description: >-
            When you decide to use a custom entity, this is the description of
            the entity.


            The entity represents what type of results the Webset will return.
            For example, if you want results to be Job Postings, you might use
            "Job Postings" as the entity description.
      required:
        - type
        - description
    WebsetEntity:
      oneOf:
        - type:
            - object
          $ref: '#/components/schemas/WebsetCompanyEntity'
        - type:
            - object
          $ref: '#/components/schemas/WebsetPersonEntity'
        - type:
            - object
          $ref: '#/components/schemas/WebsetArticleEntity'
        - type:
            - object
          $ref: '#/components/schemas/WebsetResearchPaperEntity'
        - type:
            - object
          $ref: '#/components/schemas/WebsetCustomEntity'
    WebsetSearch:
      type:
        - object
      properties:
        id:
          type:
            - string
          description: The unique identifier for the search
        object:
          type: string
          const: webset_search
          default: webset_search
        status:
          type:
            - string
          enum:
            - created
            - running
            - completed
            - canceled
          description: The status of the search
          title: WebsetSearchStatus
        query:
          type:
            - string
          minLength: 1
          maxLength: 5000
          description: The query used to create the search.
        entity:
          $ref: '#/components/schemas/WebsetEntity'
          description: >-
            The entity the search will return results for.


            When no entity is provided during creation, we will automatically
            select the best entity based on the query.
          nullable: true
        criteria:
          type:
            - array
          items:
            type:
              - object
            properties:
              description:
                type:
                  - string
                minLength: 1
                maxLength: 300
                description: The description of the criterion
              successRate:
                type:
                  - number
                minimum: 0
                maximum: 100
                description: >-
                  Value between 0 and 100 representing the percentage of results
                  that meet the criterion.
            required:
              - description
              - successRate
          description: >-
            The criteria the search will use to evaluate the results. If not
            provided, we will automatically generate them for you.
        count:
          type:
            - number
          minimum: 1
          description: >-
            The number of results the search will attempt to find. The actual
            number of results may be less than this number depending on the
            search complexity.
        progress:
          type:
            - object
          properties:
            found:
              type:
                - number
              description: The number of results found so far
            completion:
              type:
                - number
              minimum: 0
              maximum: 100
              description: The completion percentage of the search
          required:
            - found
            - completion
          description: The progress of the search
        metadata:
          default: {}
          description: Set of key-value pairs you want to associate with this object.
          type:
            - object
          additionalProperties:
            type:
              - string
            maxLength: 1000
        canceledAt:
          type: string
          format: date-time
          description: The date and time the search was canceled
          nullable: true
        canceledReason:
          type: string
          enum:
            - webset_deleted
            - webset_canceled
          description: The reason the search was canceled
          nullable: true
        createdAt:
          type:
            - string
          format: date-time
          description: The date and time the search was created
        updatedAt:
          type:
            - string
          format: date-time
          description: The date and time the search was updated
      required:
        - id
        - object
        - status
        - query
        - entity
        - criteria
        - count
        - progress
        - canceledAt
        - canceledReason
        - createdAt
        - updatedAt
    WebsetEnrichment:
      type:
        - object
      properties:
        id:
          type:
            - string
          description: The unique identifier for the enrichment
        object:
          type: string
          const: webset_enrichment
          default: webset_enrichment
        status:
          type:
            - string
          enum:
            - pending
            - canceled
            - completed
          description: The status of the enrichment
          title: WebsetEnrichmentStatus
        websetId:
          type:
            - string
          description: The unique identifier for the Webset this enrichment belongs to.
        title:
          type: string
          description: >-
            The title of the enrichment.


            This will be automatically generated based on the description and
            format.
          nullable: true
        description:
          type:
            - string
          description: >-
            The description of the enrichment task provided during the creation
            of the enrichment.
        format:
          type: string
          $ref: '#/components/schemas/WebsetEnrichmentFormat'
          description: The format of the enrichment response.
          nullable: true
        options:
          type: array
          items:
            type:
              - object
            properties:
              label:
                type:
                  - string
                description: The label of the option
            required:
              - label
          description: >-
            When the format is options, the different options for the enrichment
            agent to choose from.
          title: WebsetEnrichmentOptions
          nullable: true
        instructions:
          type: string
          description: >-
            The instructions for the enrichment Agent.


            This will be automatically generated based on the description and
            format.
          nullable: true
        metadata:
          default: {}
          description: The metadata of the enrichment
          type:
            - object
          additionalProperties:
            type:
              - string
            maxLength: 1000
        createdAt:
          type:
            - string
          format: date-time
          description: The date and time the enrichment was created
        updatedAt:
          type:
            - string
          format: date-time
          description: The date and time the enrichment was updated
      required:
        - id
        - object
        - status
        - websetId
        - title
        - description
        - format
        - options
        - instructions
        - createdAt
        - updatedAt
    WebsetEnrichmentFormat:
      type: string
      enum:
        - text
        - date
        - number
        - options
        - email
        - phone

````

## Source: https://docs.exa.ai/websets/api/websets/cancel-a-running-webset.md

# Cancel a running Webset

> Cancels all operations being performed on a Webset.

Any enrichment or search will be stopped and the Webset will be marked as `idle`.

## OpenAPI

````yaml post /v0/websets/{id}/cancel
paths:
  path: /v0/websets/{id}/cancel
  method: post
  servers:
    - url: https://api.exa.ai/websets/
      description: Production
  request:
    security:
      - title: api key
        parameters:
          query: {}
          header:
            x-api-key:
              type: apiKey
              description: Your Exa API key
          cookie: {}
    parameters:
      path:
        id:
          schema:
            - type: string
              required: true
              description: The id or externalId of the Webset
      query: {}
      header: {}
      cookie: {}
    body: {}
  response:
    '200':
      application/json:
        schemaArray:
          - type: object
            properties:
              id:
                allOf:
                  - type:
                      - string
                    description: The unique identifier for the webset
              object:
                allOf:
                  - type: string
                    const: webset
                    default: webset
              status:
                allOf:
                  - type:
                      - string
                    enum:
                      - idle
                      - running
                      - paused
                    description: The status of the webset
                    title: WebsetStatus
              externalId:
                allOf:
                  - type: string
                    description: The external identifier for the webset
                    nullable: true
              searches:
                allOf:
                  - type:
                      - array
                    items:
                      type:
                        - object
                      $ref: '#/components/schemas/WebsetSearch'
                    description: The searches that have been performed on the webset.
              enrichments:
                allOf:
                  - type:
                      - array
                    items:
                      type:
                        - object
                      $ref: '#/components/schemas/WebsetEnrichment'
                    description: The Enrichments to apply to the Webset Items.
              metadata:
                allOf:
                  - default: {}
                    description: >-
                      Set of key-value pairs you want to associate with this
                      object.
                    type:
                      - object
                    additionalProperties:
                      type:
                        - string
                      maxLength: 1000
              createdAt:
                allOf:
                  - type:
                      - string
                    format: date-time
                    description: The date and time the webset was created
              updatedAt:
                allOf:
                  - type:
                      - string
                    format: date-time
                    description: The date and time the webset was updated
            refIdentifier: '#/components/schemas/Webset'
            requiredProperties:
              - id
              - object
              - status
              - externalId
              - searches
              - enrichments
              - createdAt
              - updatedAt
        examples:
          example:
            value:
              id: <string>
              object: webset
              status: idle
              externalId: <string>
              searches:
                - id: <string>
                  object: webset_search
                  status: created
                  query: <string>
                  entity:
                    type: company
                  criteria:
                    - description: <string>
                      successRate: 50
                  count: 2
                  progress:
                    found: 123
                    completion: 50
                  metadata: {}
                  canceledAt: '2023-11-07T05:31:56Z'
                  canceledReason: webset_deleted
                  createdAt: '2023-11-07T05:31:56Z'
                  updatedAt: '2023-11-07T05:31:56Z'
              enrichments:
                - id: <string>
                  object: webset_enrichment
                  status: pending
                  websetId: <string>
                  title: <string>
                  description: <string>
                  format: text
                  options:
                    - label: <string>
                  instructions: <string>
                  metadata: {}
                  createdAt: '2023-11-07T05:31:56Z'
                  updatedAt: '2023-11-07T05:31:56Z'
              metadata: {}
              createdAt: '2023-11-07T05:31:56Z'
              updatedAt: '2023-11-07T05:31:56Z'
        description: Webset canceled
  deprecated: false
  type: path
components:
  schemas:
    WebsetCompanyEntity:
      type:
        - object
      properties:
        type:
          type: string
          const: company
          default: company
      required:
        - type
    WebsetPersonEntity:
      type:
        - object
      properties:
        type:
          type: string
          const: person
          default: person
      required:
        - type
    WebsetArticleEntity:
      type:
        - object
      properties:
        type:
          type: string
          const: article
          default: article
      required:
        - type
    WebsetResearchPaperEntity:
      type:
        - object
      properties:
        type:
          type: string
          const: research_paper
          default: research_paper
      required:
        - type
    WebsetCustomEntity:
      type:
        - object
      properties:
        type:
          type: string
          const: custom
          default: custom
        description:
          type:
            - string
          minLength: 2
          maxLength: 200
          description: >-
            When you decide to use a custom entity, this is the description of
            the entity.


            The entity represents what type of results the Webset will return.
            For example, if you want results to be Job Postings, you might use
            "Job Postings" as the entity description.
      required:
        - type
        - description
    WebsetEntity:
      oneOf:
        - type:
            - object
          $ref: '#/components/schemas/WebsetCompanyEntity'
        - type:
            - object
          $ref: '#/components/schemas/WebsetPersonEntity'
        - type:
            - object
          $ref: '#/components/schemas/WebsetArticleEntity'
        - type:
            - object
          $ref: '#/components/schemas/WebsetResearchPaperEntity'
        - type:
            - object
          $ref: '#/components/schemas/WebsetCustomEntity'
    WebsetSearch:
      type:
        - object
      properties:
        id:
          type:
            - string
          description: The unique identifier for the search
        object:
          type: string
          const: webset_search
          default: webset_search
        status:
          type:
            - string
          enum:
            - created
            - running
            - completed
            - canceled
          description: The status of the search
          title: WebsetSearchStatus
        query:
          type:
            - string
          minLength: 1
          maxLength: 5000
          description: The query used to create the search.
        entity:
          $ref: '#/components/schemas/WebsetEntity'
          description: >-
            The entity the search will return results for.


            When no entity is provided during creation, we will automatically
            select the best entity based on the query.
          nullable: true
        criteria:
          type:
            - array
          items:
            type:
              - object
            properties:
              description:
                type:
                  - string
                minLength: 1
                maxLength: 300
                description: The description of the criterion
              successRate:
                type:
                  - number
                minimum: 0
                maximum: 100
                description: >-
                  Value between 0 and 100 representing the percentage of results
                  that meet the criterion.
            required:
              - description
              - successRate
          description: >-
            The criteria the search will use to evaluate the results. If not
            provided, we will automatically generate them for you.
        count:
          type:
            - number
          minimum: 1
          description: >-
            The number of results the search will attempt to find. The actual
            number of results may be less than this number depending on the
            search complexity.
        progress:
          type:
            - object
          properties:
            found:
              type:
                - number
              description: The number of results found so far
            completion:
              type:
                - number
              minimum: 0
              maximum: 100
              description: The completion percentage of the search
          required:
            - found
            - completion
          description: The progress of the search
        metadata:
          default: {}
          description: Set of key-value pairs you want to associate with this object.
          type:
            - object
          additionalProperties:
            type:
              - string
            maxLength: 1000
        canceledAt:
          type: string
          format: date-time
          description: The date and time the search was canceled
          nullable: true
        canceledReason:
          type: string
          enum:
            - webset_deleted
            - webset_canceled
          description: The reason the search was canceled
          nullable: true
        createdAt:
          type:
            - string
          format: date-time
          description: The date and time the search was created
        updatedAt:
          type:
            - string
          format: date-time
          description: The date and time the search was updated
      required:
        - id
        - object
        - status
        - query
        - entity
        - criteria
        - count
        - progress
        - canceledAt
        - canceledReason
        - createdAt
        - updatedAt
    WebsetEnrichment:
      type:
        - object
      properties:
        id:
          type:
            - string
          description: The unique identifier for the enrichment
        object:
          type: string
          const: webset_enrichment
          default: webset_enrichment
        status:
          type:
            - string
          enum:
            - pending
            - canceled
            - completed
          description: The status of the enrichment
          title: WebsetEnrichmentStatus
        websetId:
          type:
            - string
          description: The unique identifier for the Webset this enrichment belongs to.
        title:
          type: string
          description: >-
            The title of the enrichment.


            This will be automatically generated based on the description and
            format.
          nullable: true
        description:
          type:
            - string
          description: >-
            The description of the enrichment task provided during the creation
            of the enrichment.
        format:
          type: string
          $ref: '#/components/schemas/WebsetEnrichmentFormat'
          description: The format of the enrichment response.
          nullable: true
        options:
          type: array
          items:
            type:
              - object
            properties:
              label:
                type:
                  - string
                description: The label of the option
            required:
              - label
          description: >-
            When the format is options, the different options for the enrichment
            agent to choose from.
          title: WebsetEnrichmentOptions
          nullable: true
        instructions:
          type: string
          description: >-
            The instructions for the enrichment Agent.


            This will be automatically generated based on the description and
            format.
          nullable: true
        metadata:
          default: {}
          description: The metadata of the enrichment
          type:
            - object
          additionalProperties:
            type:
              - string
            maxLength: 1000
        createdAt:
          type:
            - string
          format: date-time
          description: The date and time the enrichment was created
        updatedAt:
          type:
            - string
          format: date-time
          description: The date and time the enrichment was updated
      required:
        - id
        - object
        - status
        - websetId
        - title
        - description
        - format
        - options
        - instructions
        - createdAt
        - updatedAt
    WebsetEnrichmentFormat:
      type: string
      enum:
        - text
        - date
        - number
        - options
        - email
        - phone

````

## Source: https://docs.exa.ai/websets/api/websets/list-all-websets.md

# List all Websets

> Returns a list of Websets.

You can paginate through the results using the `cursor` parameter.

## OpenAPI

````yaml get /v0/websets
paths:
  path: /v0/websets
  method: get
  servers:
    - url: https://api.exa.ai/websets/
      description: Production
  request:
    security:
      - title: api key
        parameters:
          query: {}
          header:
            x-api-key:
              type: apiKey
              description: Your Exa API key
          cookie: {}
    parameters:
      path: {}
      query:
        cursor:
          schema:
            - type: string
              required: false
              description: The cursor to paginate through the results
              minLength: 1
        limit:
          schema:
            - type: number
              required: false
              description: The number of Websets to return
              maximum: 100
              minimum: 1
              default: 25
      header: {}
      cookie: {}
    body: {}
  response:
    '200':
      application/json:
        schemaArray:
          - type: object
            properties:
              data:
                allOf:
                  - type:
                      - array
                    items:
                      type:
                        - object
                      $ref: '#/components/schemas/Webset'
                    description: The list of websets
              hasMore:
                allOf:
                  - type:
                      - boolean
                    description: Whether there are more results to paginate through
              nextCursor:
                allOf:
                  - type: string
                    description: The cursor to paginate through the next set of results
                    nullable: true
            refIdentifier: '#/components/schemas/ListWebsetsResponse'
            requiredProperties:
              - data
              - hasMore
              - nextCursor
        examples:
          example:
            value:
              data:
                - id: <string>
                  object: webset
                  status: idle
                  externalId: <string>
                  searches:
                    - id: <string>
                      object: webset_search
                      status: created
                      query: <string>
                      entity:
                        type: company
                      criteria:
                        - description: <string>
                          successRate: 50
                      count: 2
                      progress:
                        found: 123
                        completion: 50
                      metadata: {}
                      canceledAt: '2023-11-07T05:31:56Z'
                      canceledReason: webset_deleted
                      createdAt: '2023-11-07T05:31:56Z'
                      updatedAt: '2023-11-07T05:31:56Z'
                  enrichments:
                    - id: <string>
                      object: webset_enrichment
                      status: pending
                      websetId: <string>
                      title: <string>
                      description: <string>
                      format: text
                      options:
                        - label: <string>
                      instructions: <string>
                      metadata: {}
                      createdAt: '2023-11-07T05:31:56Z'
                      updatedAt: '2023-11-07T05:31:56Z'
                  metadata: {}
                  createdAt: '2023-11-07T05:31:56Z'
                  updatedAt: '2023-11-07T05:31:56Z'
              hasMore: true
              nextCursor: <string>
        description: List of Websets
  deprecated: false
  type: path
components:
  schemas:
    WebsetCompanyEntity:
      type:
        - object
      properties:
        type:
          type: string
          const: company
          default: company
      required:
        - type
    WebsetPersonEntity:
      type:
        - object
      properties:
        type:
          type: string
          const: person
          default: person
      required:
        - type
    WebsetArticleEntity:
      type:
        - object
      properties:
        type:
          type: string
          const: article
          default: article
      required:
        - type
    WebsetResearchPaperEntity:
      type:
        - object
      properties:
        type:
          type: string
          const: research_paper
          default: research_paper
      required:
        - type
    WebsetCustomEntity:
      type:
        - object
      properties:
        type:
          type: string
          const: custom
          default: custom
        description:
          type:
            - string
          minLength: 2
          maxLength: 200
          description: >-
            When you decide to use a custom entity, this is the description of
            the entity.


            The entity represents what type of results the Webset will return.
            For example, if you want results to be Job Postings, you might use
            "Job Postings" as the entity description.
      required:
        - type
        - description
    WebsetEntity:
      oneOf:
        - type:
            - object
          $ref: '#/components/schemas/WebsetCompanyEntity'
        - type:
            - object
          $ref: '#/components/schemas/WebsetPersonEntity'
        - type:
            - object
          $ref: '#/components/schemas/WebsetArticleEntity'
        - type:
            - object
          $ref: '#/components/schemas/WebsetResearchPaperEntity'
        - type:
            - object
          $ref: '#/components/schemas/WebsetCustomEntity'
    WebsetSearch:
      type:
        - object
      properties:
        id:
          type:
            - string
          description: The unique identifier for the search
        object:
          type: string
          const: webset_search
          default: webset_search
        status:
          type:
            - string
          enum:
            - created
            - running
            - completed
            - canceled
          description: The status of the search
          title: WebsetSearchStatus
        query:
          type:
            - string
          minLength: 1
          maxLength: 5000
          description: The query used to create the search.
        entity:
          $ref: '#/components/schemas/WebsetEntity'
          description: >-
            The entity the search will return results for.


            When no entity is provided during creation, we will automatically
            select the best entity based on the query.
          nullable: true
        criteria:
          type:
            - array
          items:
            type:
              - object
            properties:
              description:
                type:
                  - string
                minLength: 1
                maxLength: 300
                description: The description of the criterion
              successRate:
                type:
                  - number
                minimum: 0
                maximum: 100
                description: >-
                  Value between 0 and 100 representing the percentage of results
                  that meet the criterion.
            required:
              - description
              - successRate
          description: >-
            The criteria the search will use to evaluate the results. If not
            provided, we will automatically generate them for you.
        count:
          type:
            - number
          minimum: 1
          description: >-
            The number of results the search will attempt to find. The actual
            number of results may be less than this number depending on the
            search complexity.
        progress:
          type:
            - object
          properties:
            found:
              type:
                - number
              description: The number of results found so far
            completion:
              type:
                - number
              minimum: 0
              maximum: 100
              description: The completion percentage of the search
          required:
            - found
            - completion
          description: The progress of the search
        metadata:
          default: {}
          description: Set of key-value pairs you want to associate with this object.
          type:
            - object
          additionalProperties:
            type:
              - string
            maxLength: 1000
        canceledAt:
          type: string
          format: date-time
          description: The date and time the search was canceled
          nullable: true
        canceledReason:
          type: string
          enum:
            - webset_deleted
            - webset_canceled
          description: The reason the search was canceled
          nullable: true
        createdAt:
          type:
            - string
          format: date-time
          description: The date and time the search was created
        updatedAt:
          type:
            - string
          format: date-time
          description: The date and time the search was updated
      required:
        - id
        - object
        - status
        - query
        - entity
        - criteria
        - count
        - progress
        - canceledAt
        - canceledReason
        - createdAt
        - updatedAt
    WebsetEnrichment:
      type:
        - object
      properties:
        id:
          type:
            - string
          description: The unique identifier for the enrichment
        object:
          type: string
          const: webset_enrichment
          default: webset_enrichment
        status:
          type:
            - string
          enum:
            - pending
            - canceled
            - completed
          description: The status of the enrichment
          title: WebsetEnrichmentStatus
        websetId:
          type:
            - string
          description: The unique identifier for the Webset this enrichment belongs to.
        title:
          type: string
          description: >-
            The title of the enrichment.


            This will be automatically generated based on the description and
            format.
          nullable: true
        description:
          type:
            - string
          description: >-
            The description of the enrichment task provided during the creation
            of the enrichment.
        format:
          type: string
          $ref: '#/components/schemas/WebsetEnrichmentFormat'
          description: The format of the enrichment response.
          nullable: true
        options:
          type: array
          items:
            type:
              - object
            properties:
              label:
                type:
                  - string
                description: The label of the option
            required:
              - label
          description: >-
            When the format is options, the different options for the enrichment
            agent to choose from.
          title: WebsetEnrichmentOptions
          nullable: true
        instructions:
          type: string
          description: >-
            The instructions for the enrichment Agent.


            This will be automatically generated based on the description and
            format.
          nullable: true
        metadata:
          default: {}
          description: The metadata of the enrichment
          type:
            - object
          additionalProperties:
            type:
              - string
            maxLength: 1000
        createdAt:
          type:
            - string
          format: date-time
          description: The date and time the enrichment was created
        updatedAt:
          type:
            - string
          format: date-time
          description: The date and time the enrichment was updated
      required:
        - id
        - object
        - status
        - websetId
        - title
        - description
        - format
        - options
        - instructions
        - createdAt
        - updatedAt
    Webset:
      type:
        - object
      properties:
        id:
          type:
            - string
          description: The unique identifier for the webset
        object:
          type: string
          const: webset
          default: webset
        status:
          type:
            - string
          enum:
            - idle
            - running
            - paused
          description: The status of the webset
          title: WebsetStatus
        externalId:
          type: string
          description: The external identifier for the webset
          nullable: true
        searches:
          type:
            - array
          items:
            type:
              - object
            $ref: '#/components/schemas/WebsetSearch'
          description: The searches that have been performed on the webset.
        enrichments:
          type:
            - array
          items:
            type:
              - object
            $ref: '#/components/schemas/WebsetEnrichment'
          description: The Enrichments to apply to the Webset Items.
        metadata:
          default: {}
          description: Set of key-value pairs you want to associate with this object.
          type:
            - object
          additionalProperties:
            type:
              - string
            maxLength: 1000
        createdAt:
          type:
            - string
          format: date-time
          description: The date and time the webset was created
        updatedAt:
          type:
            - string
          format: date-time
          description: The date and time the webset was updated
      required:
        - id
        - object
        - status
        - externalId
        - searches
        - enrichments
        - createdAt
        - updatedAt
    WebsetEnrichmentFormat:
      type: string
      enum:
        - text
        - date
        - number
        - options
        - email
        - phone

````

## Source: https://docs.exa.ai/websets/api/get-started.md

# Get started

> Create your first Webset

## Create and setup your API key

1. Go to the [Exa Dashboard](https://dashboard.exa.ai)
2. Click on "API Keys" in the left sidebar
3. Click "Create API Key"
4. Give your key a name and click "Create"
5. Copy your API key and store it securely - you won't be able to see it again!

<Card title="Get your Exa API key" icon="key" horizontal href="https://dashboard.exa.ai/api-keys" />

<br />

## Create a .env file

Create a file called `.env` in the root of your project and add the following line.

```bash
EXA_API_KEY=your api key without quotes
```

<br />

## Make an API request

Use our Python or JavaScript SDKs, or call the API directly with cURL.

<Tabs>
  <Tab title="Python">
    Install the latest version of the python SDK with pip. If you want to store your API key in a `.env` file, make sure to install the dotenv library.

    ```bash
    pip install exa-py
    pip install python-dotenv
    ```

    Create a file called `webset.py` and add the code below:

    ```python python
    from exa_py import Exa
    from dotenv import load_dotenv
    from exa_py.websets.types import CreateWebsetParameters, CreateEnrichmentParameters

    import os

    load_dotenv()
    exa = Exa(os.getenv('EXA_API_KEY'))

    # Create a Webset with search and enrichments
    webset = exa.websets.create(
        params=CreateWebsetParameters(
            search={
                "query": "Top AI research labs focusing on large language models",
                "count": 5
            },
            enrichments=[
                CreateEnrichmentParameters(
                    description="LinkedIn profile of VP of Engineering or related role",
                    format="text",
                ),
            ],
        )
    )

    print(f"Webset created with ID: {webset.id}")

    # Wait until Webset completes processing
    webset = exa.websets.wait_until_idle(webset.id)

    # Retrieve Webset Items
    items = exa.websets.items.list(webset_id=webset.id)
    for item in items.data:
        print(f"Item: {item.model_dump_json(indent=2)}")
    ```
  </Tab>

  <Tab title="JavaScript">
    Install the latest version of the JavaScript SDK with npm or pnpm:

    ```bash
    npm install exa-js
    ```

    Create a file called `webset.js` and add the code below:

    ```javascript javascript
    import * as dotenv from "dotenv";
    import Exa, { CreateWebsetParameters, CreateEnrichmentParameters } from "exa-js";

    // Load environment variables
    dotenv.config();

    async function main() {
      const exa = new Exa(process.env.EXA_API_KEY);

      try {
        // Create a Webset with search and enrichments
        const webset = await exa.websets.create({
          search: {
            query: "Top AI research labs focusing on large language models",
            count: 10
          },
          enrichments: [
            {
              description: "Estimate the company'\''s founding year",
              format: "number"
            }
          ],
        });

        console.log(`Webset created with ID: ${webset.id}`);

        // Wait until Webset completes processing
        const idleWebset = await exa.websets.waitUntilIdle(webset.id, {
          timeout: 60000,
          pollInterval: 2000,
          onPoll: (status) => console.log(`Current status: ${status}...`)
        });

        // Retrieve Webset Items
        const items = await exa.websets.items.list(webset.id, { limit: 10 });
        for (const item of items.data) {
          console.log(`Item: ${JSON.stringify(item, null, 2)}`);
        }
      } catch (error) {
        console.error("Error:", error);
      }
    }

    main();
    ```
  </Tab>

  <Tab title="cURL">
    Pass the following command to your terminal to create a Webset:

    ```bash bash
    curl --request POST \
      --url https://api.exa.ai/websets/v0/websets/ \
      --header 'accept: application/json' \
      --header 'content-type: application/json' \
      --header "x-api-key: ${EXA_API_KEY}" \
      --data '{
        "search": {
          "query": "Top AI research labs focusing on large language models",
          "count": 5
        },
        "enrichments": [
          {
            "description": "Find the company'\''s founding year",
            "format": "number"
          }
        ]
      }'
    ```

    To check the status of your Webset:

    ```bash bash
    curl --request GET \
      --url https://api.exa.ai/websets/v0/websets/{WEBSET_ID} \
      --header 'accept: application/json' \
      --header "x-api-key: ${EXA_API_KEY}"
    ```

    To list items in your Webset:

    ```bash bash
    curl --request GET \
      --url https://api.exa.ai/websets/v0/websets/{WEBSET_ID}/items \
      --header 'accept: application/json' \
      --header "x-api-key: ${EXA_API_KEY}"
    ```

    Or you can use the `expand` parameter to get the latest 100 within your Webset:

    ```bash bash
    curl --request GET \
      --url https://api.exa.ai/websets/v0/websets/{WEBSET_ID}?expand=items \
      --header 'accept: application/json' \
      --header "x-api-key: ${EXA_API_KEY}"
    ```
  </Tab>
</Tabs>

***

## What's next?

* Learn [how Websets work](/websets/api/how-it-works) and understand the event-driven process
* Configure [webhooks](/websets/api/webhooks) to receive real-time updates as items are added into your Websets
* Learn about [Enrichments](/websets/api/websets/enrichments) to extract specific data points
* See how to [Manage Items](/websets/api/websets/items) in your Webset


## Source: https://docs.exa.ai/websets/api/overview.md

# Overview

> The Websets API helps you find, verify, and process web data at scale to build your unique collection of web content.

The Websets API helps you create your own unique slice of the web by organizing content in containers (`Webset`). These containers store structured results (`WebsetItem`) which are discovered by search agents (`WebsetSearch`) that find web pages matching your specific criteria. Once these items are added to your Webset, they can be further processed with enrichment agents to extract additional data.

Whether you're looking for companies, people, or research papers, each result becomes a structured Item with source content, verification status, and type-specific fields. These Items can be further enriched with enrichments.

## Key Features

At its core, the API is:

* **Asynchronous**: It's an async-first API. Searches (`Webset Search`) can take from seconds to minutes, depending on the complexity.

* **Structured**: Every result (`Webset Item`) includes structured properties, webpage content, and verification against your criteria, with reasoning and references explaining why it matches.

* **Event-Driven**: Events are published and delivered through webhooks to notify when items are found and when enrichments complete, allowing you to process data as it arrives.

***

## Core Objects

<img src="https://mintlify.s3.us-west-1.amazonaws.com/exa-52/images/websets/api/core.png" alt="Core concepts diagram showing relationships between Webset, Search, Item and Enrichment objects" />

* **Webset**: Container that organizes your unique collection of web content and its related searches
* **Search**: An agent that searches and crawls the web to find precise entities matching your criteria, adding them to your Webset as structured WebsetItems
* **Item**: A structured result with source content, verification status, and type-specific fields (company, person, research paper, etc.)
* **Enrichment**: An agent that searches the web to enhance existing WebsetItems with additional structured data

## Next Steps

* Follow our [quickstart guide](/websets/api/get-started)
* Learn more about [how it works](/websets/api/how-it-works)
* Browse the [API reference](/websets/api/websets/create-a-webset)
