import os
import uuid
import pandas as pd
import csv
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.tools import StructuredTool
from langchain.agents import AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools.render import render_text_description
from langchain_core.utils.function_calling import convert_to_openai_tool
from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser


llm = ChatOpenAI(temperature=0, model_name="gpt-4o", streaming=False)

from dotenv import load_dotenv
load_dotenv()


# File path for our mock database
RESERVATIONS_FILE = "reservations.csv"

# Initialize the CSV file if it doesn't exist
def initialize_csv():
    if not os.path.exists(RESERVATIONS_FILE):
        with open(RESERVATIONS_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["reservation_id", "reservation_date", "planned_trip_date", 
                             "trip_destination", "description"])

# Tool to save a reservation
def save_reservation(planned_trip_date, trip_destination, description):
    """
    Save a new trip reservation.
    
    Args:
        planned_trip_date: The date of the planned trip (YYYY-MM-DD format)
        trip_destination: Destination of the trip
        description: Additional details about the trip
    
    Returns:
        A confirmation message with the reservation ID
    """
    initialize_csv()
    
    # Generate a unique reservation ID
    reservation_id = str(uuid.uuid4())[:8]
    reservation_date = datetime.now().strftime('%Y-%m-%d')

    # Save to CSV
    with open(RESERVATIONS_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([reservation_id, reservation_date, planned_trip_date, 
                         trip_destination, description])
    print(f"Saved reservation to CSV: {RESERVATIONS_FILE}" )
    
    return f"Reservation created successfully! Your reservation ID is: {reservation_id}"

# Tool to read a reservation
def read_reservation(reservation_id):
    """
    Look up a reservation by ID.
    
    Args:
        reservation_id: The unique ID of the reservation to look up
    
    Returns:
        Details of the reservation or an error message if not found
    """
    initialize_csv()
    
    try:
        df = pd.read_csv(RESERVATIONS_FILE)
        reservation = df[df['reservation_id'] == reservation_id]
        
        if reservation.empty:
            return f"No reservation found with ID: {reservation_id}"
        
        # Get the first (and should be only) matching reservation
        res = reservation.iloc[0]
        return f"Reservation found:\nID: {res['reservation_id']}\nBooked on: {res['reservation_date']}\nTrip date: {res['planned_trip_date']}\nDestination: {res['trip_destination']}\nDetails: {res['description']}"
    
    except Exception as e:
        return f"Error looking up reservation: {str(e)}"

##TODO: read what save_reservation tool does and fill in the description
save_reservation_tool = StructuredTool.from_function(
    func=save_reservation,
    name="save_reservation",
    description="""
    Use this tool to save a new trip reservation. 
    Input arguments: 
    - `planned_trip_date`: The date of the planned trip (YYYY-MM-DD format).
    - `trip_destination`: Destination of the trip.
    - `description`: Additional details about the trip.
    Tool output: A confirmation message with the reservation ID.
    """
)

read_reservation_tool = StructuredTool.from_function(
    func=read_reservation,
    name="read_reservation",
    description="""
    Use this tool to look up a reservation by its ID. 
    Input arguments: 
    - `reservation_id`: The unique ID of the reservation to look up.
    Tool output: Details of the reservation or an error message if not found.
    """
)

##TODO: Add tools that you want to use in the agent
tools = [save_reservation_tool, read_reservation_tool]

# Prompt template for the agent
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", 
         """You are a helpful travel booking assistant.
You can help users make new travel reservations or look up existing ones.

To make a new reservation, you need:
1. The planned trip date (in YYYY-MM-DD format)
2. The destination
3. Any additional details or description

To look up an existing reservation, you need the reservation ID.

TOOLS:\n------\n\nAssistant has access to the following tools:\n\n{tools}\n\n
If you are not sure which tool is best for the task use multiple and them select best output. 
When you are using a tool, remember to provide all relevant context for the tool to execute the task, especially if the context is present in previous messages from chat history. 
Pay attention if user is asking about sale or rent offers. 

If you gave the user some recommendations in previous messages and he agrees with them use those recommendations in your actions. 
When analyzing tool output, compare it with Human question, if it only partially answered it explain it to the user. 
 
To use a tool, please use the following format:\n\n```\n
Thought: Do I need to use a tool? Yes\n
Action: the action to take, should be one of [{tool_names}]\n
Action Input: the input to the action\n
Observation: the result of the action\n

... (repeat Thought/Action/Observation as needed)
Final Answer: The response to the user including relevant information from the tools

Begin!

New input:""",
        ),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

##TODO: parse tool names from tools so that they are easy to read in prompt, expected output: 'save_reservation, read_reservation'
tool_names=", ".join([t.name for t in tools])


prompt = prompt.partial(tools=render_text_description(tools), tool_names=tool_names)
llm_with_tools = llm.bind(tools=[convert_to_openai_tool(tool) for tool in tools])



agent = (
         RunnablePassthrough.assign(
            agent_scratchpad=lambda x: format_to_openai_tool_messages(x["intermediate_steps"]),
        
            )
         | prompt
         | llm_with_tools
         | OpenAIToolsAgentOutputParser())


##TODO: initiate agent_executor based on previously defined agent and tools
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=False)


def run_agent_with_query(query):
    return agent_executor.invoke({"input": query})

if __name__=="__main__":
    ##TODO: put a breakpoint in csv saving to see how agent and code overlap, evaluate inputs/outputs
    query = "I want to book a trip on 2023-12-25 to Paris, France. 2 people for 3 nights. Its a business trip"
    output = run_agent_with_query(query)

    query_2 = "What is the status of reservation 9c89a904?"
    output_2 = run_agent_with_query(query_2)
    print( output_2)