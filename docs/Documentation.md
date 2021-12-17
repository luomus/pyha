# Pyha documentation

## In general

Pyha is a system for making, managing and monitoring data requests. A data request is made with certain set of filters
to receive unsecured occurrence data. Each data owner that is part of the request will approve or decline the request
for their datasets (collections). 

Pyha was been implemented for four groups of users:
- applicants of the data request
- data owners
- administrators (ict-admins)
- authorities (DEFUNCT: sensitive data is no longer separately approved by an authority; all is handled via data owners)

A data request is initiated in the FinBIF public portal by selecting filters. FinBIF portal will call API of Pyha to 
initiate a new data request. The applicant will then receive an email with a link to Pyha where the user will continue
to fill in information of the data request.  After data request has been approved, the applicant can also download the 
files of the approved data requests and monitor the processing of their data requests. 

Data owners are required to log in, after which they can go through the data requesters, manage their status, and send 
questions to the applicants. Ownership of datasets is defined in dataset (collection) metadata.

All parties will be notified at sufficiently short intervals (by e-mail) of requests which require them 
to take action.

Note: The system contains functionality for two different workflows:
 - one where sensitive data is approved separately (no longer functional; data warehouse API does not support it and should
   be removed from Pyha)
 - one where all requests are handled only by the owner of the dataset
 
## System components

### Request Selection View (/index)

The request selection view lists all the material requests made by the applicant, as well as their
general information and status. For dataset owners, all requests that contain occurrences from their
datasets. ICT-admins see all requests.
### Requestview (/requestview/id)

The status view of the request shows the applicant all the information related to the request and its status
 - with the exception of discussions between dataset owners. 
Dataset owners see the same, but they also have additional feature to chat with other datasets owners about 
the request. They also have an additional tool to make a decision to approve or decline the request and fill
in their reasoning. 

### Fill in the request form (/requestform/id)

In the view, the layman fills the material request with the restrictions they have chosen,
for the purpose and with the contact information of the system (accepting the data protection
conditions).

### Checking out (/logout)

Logout.

### Interface (/api/)

Provides an interface to other applications. ([Api Documentation] (Api.md))

### Interface to ajax queries (/ajax/)

Provides an interface for ajax queries.

### Settings

Provides ICT-admins settings for customizing the software's automatic functionality.

## Architecture

### Database

Database information can be found here: [Database] (Database.md)

### Translations

Translation information can be found here: [Translation] (Translation.md).
